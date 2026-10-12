"""记录脱敏后的 HTTP 交互，仅在测试失败时附加到 Allure。"""

from copy import deepcopy
import json
import re
from typing import Any

import requests


_TRACE: list[dict[str, Any]] = []
_SENSITIVE_KEYS = {
    "authorization",
    "x-authorization",
    "cookie",
    "set-cookie",
    "password",
    "token",
    "refreshtoken",
    "credentialsid",
    "credentialsvalue",
    "deviceToken".lower(),
    "accesstoken",
}
_MAX_TEXT_LENGTH = 5000


class SecretString(str):
    """行为与 str 相同，但日志、pytest traceback 中的 repr 永不显示原值。"""

    def __repr__(self) -> str:
        return "'***REDACTED***'"


def clear_api_trace() -> None:
    _TRACE.clear()


def get_api_trace() -> list[dict[str, Any]]:
    return deepcopy(_TRACE)


def _redact_url(url: str) -> str:
    """遮盖 ThingsBoard 设备令牌路径和常见敏感查询参数。"""

    redacted = re.sub(
        r"(/api/v1/)[^/?]+",
        r"\1***REDACTED***",
        url,
        flags=re.IGNORECASE,
    )
    redacted = re.sub(
        r"(?i)(token|password|accessToken)=([^&]+)",
        r"\1=***REDACTED***",
        redacted,
    )
    return redacted


def _redact_data(value: Any, parent_key: str = "") -> Any:
    if parent_key.lower() in _SENSITIVE_KEYS:
        return "***REDACTED***"
    if isinstance(value, dict):
        return {
            str(key): _redact_data(item, str(key))
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_redact_data(item, parent_key) for item in value]
    if isinstance(value, str) and len(value) > _MAX_TEXT_LENGTH:
        return value[:_MAX_TEXT_LENGTH] + "...<truncated>"
    return value


def _body_for_report(body: Any) -> Any:
    if body is None or body == b"" or body == "":
        return None
    if isinstance(body, bytes):
        body = body.decode("utf-8", errors="replace")
    if isinstance(body, str):
        try:
            return _redact_data(json.loads(body))
        except json.JSONDecodeError:
            return _redact_data(body)
    return _redact_data(body)


def _safe_headers(headers: Any) -> dict[str, str]:
    if not headers:
        return {}
    return {
        str(key): (
            "***REDACTED***"
            if str(key).lower() in _SENSITIVE_KEYS
            else str(value)
        )
        for key, value in dict(headers).items()
    }


class TracedSession(requests.Session):
    """requests.Session 的兼容替代品，自动保存脱敏交互。"""

    def request(self, method: str, url: str, **kwargs) -> requests.Response:
        try:
            response = super().request(method, url, **kwargs)
        except requests.RequestException as exc:
            _TRACE.append(
                {
                    "request": {
                        "method": method.upper(),
                        "url": _redact_url(url),
                        "headers": _safe_headers(kwargs.get("headers")),
                        "body": _redact_data(kwargs.get("json")),
                    },
                    "error": type(exc).__name__,
                    "message": str(exc)[:_MAX_TEXT_LENGTH],
                }
            )
            raise

        prepared = response.request
        response_content_type = response.headers.get("Content-Type", "")
        if "json" in response_content_type.lower():
            try:
                response_body = _redact_data(response.json())
            except requests.exceptions.JSONDecodeError:
                response_body = _body_for_report(response.text)
        else:
            response_body = _body_for_report(response.text)

        _TRACE.append(
            {
                "request": {
                    "method": prepared.method,
                    "url": _redact_url(prepared.url or url),
                    "headers": _safe_headers(prepared.headers),
                    "body": _body_for_report(prepared.body),
                },
                "response": {
                    "status": response.status_code,
                    "elapsed_ms": round(response.elapsed.total_seconds() * 1000, 2),
                    "headers": _safe_headers(response.headers),
                    "body": response_body,
                },
            }
        )
        return response

