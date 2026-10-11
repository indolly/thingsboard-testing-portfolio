"""读取 UI 自动化所需配置，不在日志中输出秘密值。"""

from dataclasses import dataclass, field
import json
import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
POSTMAN_LOCAL_ENV = (
    PROJECT_ROOT.parent
    / "postman"
    / "ThingsBoard_Local.postman_environment.local.json"
)


@dataclass(frozen=True)
class UiSettings:
    base_url: str
    tenant_username: str
    tenant_password: str = field(repr=False)
    customer_username: str
    customer_password: str = field(repr=False)
    device_name: str
    browser: str
    headless: bool
    timeout: float


def _load_dotenv_file() -> None:
    """读取模块内本地 .env；文件不存在时安静跳过。"""

    env_path = PROJECT_ROOT / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def _load_postman_values() -> dict[str, str]:
    """复用现有 Postman 本地环境，但不打印其中的凭据。"""

    if not POSTMAN_LOCAL_ENV.exists():
        return {}

    try:
        document = json.loads(POSTMAN_LOCAL_ENV.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(
            f"无法读取 Postman 本地环境文件：{POSTMAN_LOCAL_ENV}"
        ) from exc

    result: dict[str, str] = {}
    for item in document.get("values", []):
        if not isinstance(item, dict) or item.get("enabled") is False:
            continue
        key = item.get("key")
        value = item.get("value")
        if isinstance(key, str) and value is not None:
            result[key] = str(value)
    return result


def _value(postman_values: dict[str, str], env_name: str, *postman_names: str) -> str:
    environment_value = os.getenv(env_name, "").strip()
    if environment_value:
        return environment_value

    for name in postman_names:
        postman_value = postman_values.get(name, "").strip()
        if postman_value:
            return postman_value
    return ""


def get_ui_settings() -> UiSettings:
    """返回经过校验的 UI 自动化配置。"""

    _load_dotenv_file()
    postman_values = _load_postman_values()

    base_url = _value(postman_values, "TB_BASE_URL", "baseUrl", "baseurl").rstrip("/")
    username = _value(
        postman_values,
        "TB_TENANT_USERNAME",
        "tenantUsername",
        "username",
    )
    password = _value(
        postman_values,
        "TB_TENANT_PASSWORD",
        "tenantPassword",
        "password",
    )
    customer_username = _value(
        postman_values,
        "TB_CUSTOMER_USERNAME",
        "customerUsername",
    )
    customer_password = _value(
        postman_values,
        "TB_CUSTOMER_PASSWORD",
        "customerPassword",
    )
    device_name = _value(
        postman_values,
        "TB_DEVICE_NAME",
        "deviceName",
    ) or "QA_TEMP_DEVICE_001"
    browser = os.getenv("UI_BROWSER", "chrome").strip().lower()
    headless_text = os.getenv("UI_HEADLESS", "true").strip().lower()

    required = {
        "TB_BASE_URL": base_url,
        "TB_TENANT_USERNAME": username,
        "TB_TENANT_PASSWORD": password,
        "TB_CUSTOMER_USERNAME": customer_username,
        "TB_CUSTOMER_PASSWORD": customer_password,
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise RuntimeError(
            "UI 测试配置缺少必填项："
            + ", ".join(missing)
            + "。请检查系统环境变量、ui-automation-python/.env 或 Postman local JSON。"
        )

    if browser not in {"chrome", "edge"}:
        raise RuntimeError("UI_BROWSER 只支持 chrome 或 edge。")
    if headless_text not in {"true", "false"}:
        raise RuntimeError("UI_HEADLESS 只支持 true 或 false。")

    try:
        timeout = float(os.getenv("UI_TIMEOUT", "15"))
    except ValueError as exc:
        raise RuntimeError("UI_TIMEOUT 必须是数字，例如 15。") from exc
    if timeout <= 0:
        raise RuntimeError("UI_TIMEOUT 必须大于 0。")

    return UiSettings(
        base_url=base_url,
        tenant_username=username,
        tenant_password=password,
        customer_username=customer_username,
        customer_password=customer_password,
        device_name=device_name,
        browser=browser,
        headless=headless_text == "true",
        timeout=timeout,
    )
