"""封装 ThingsBoard 认证接口，避免测试用例重复拼 URL 和请求头。"""

from typing import Any

import requests

from clients.http_trace import TracedSession


class AuthClient:
    def __init__(self, base_url: str, timeout: float = 10) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = TracedSession()
        self.session.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

    def login(self, username: str, password: str) -> requests.Response:
        """使用账号密码登录，成功响应中应包含 JWT token。"""

        return self.session.post(
            f"{self.base_url}/api/auth/login",
            json={"username": username, "password": password},
            timeout=self.timeout,
        )

    def get_current_user(self, token: str | None = None) -> requests.Response:
        """查询当前用户；token 为空时用于验证未认证访问。"""

        return self.session.get(
            f"{self.base_url}/api/auth/user",
            headers=(
                {"X-Authorization": f"Bearer {token}"}
                if token
                else {}
            ),
            timeout=self.timeout,
        )

    def close(self) -> None:
        self.session.close()


def response_json_or_empty(response: requests.Response) -> dict[str, Any]:
    """尽量解析 JSON；空响应或非 JSON 响应统一返回空字典。"""

    try:
        body = response.json()
    except requests.exceptions.JSONDecodeError:
        return {}
    return body if isinstance(body, dict) else {}

