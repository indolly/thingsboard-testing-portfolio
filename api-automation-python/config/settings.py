"""从本地 .env 读取测试环境配置，并在测试开始前进行校验。"""

from dataclasses import dataclass, field
import json
import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")
POSTMAN_LOCAL_ENV = (
    PROJECT_ROOT.parent
    / "postman"
    / "ThingsBoard_Local.postman_environment.local.json"
)


@dataclass(frozen=True)
class Settings:
    base_url: str
    tenant_username: str
    tenant_password: str = field(repr=False)
    device_name: str
    device_profile_name: str
    device_token: str = field(repr=False)
    alarm_type: str
    alarm_severity: str
    alarm_trigger_temperature: float
    alarm_recovery_temperature: float
    alarm_wait_seconds: float
    asset_name: str
    customer_title: str
    customer_username: str
    customer_password: str = field(repr=False)
    request_timeout: float


def _load_postman_values() -> dict[str, str]:
    """读取本机 Postman 环境文件，不输出其中的凭据。"""

    if not POSTMAN_LOCAL_ENV.exists():
        return {}

    try:
        document = json.loads(POSTMAN_LOCAL_ENV.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(
            f"无法读取 Postman 本地环境文件：{POSTMAN_LOCAL_ENV}"
        ) from exc

    values: dict[str, str] = {}
    for item in document.get("values", []):
        if not isinstance(item, dict) or item.get("enabled") is False:
            continue
        key = item.get("key")
        value = item.get("value")
        if isinstance(key, str) and value is not None:
            values[key] = str(value)
    return values


def _first_value(
    postman_values: dict[str, str],
    environment_name: str,
    *postman_names: str,
) -> str:
    """优先使用 .env/系统环境变量，否则读取 Postman local JSON。"""

    environment_value = os.getenv(environment_name, "").strip()
    if environment_value:
        return environment_value

    for name in postman_names:
        value = postman_values.get(name, "").strip()
        if value:
            return value
    return ""


def get_settings() -> Settings:
    """返回已校验的配置；缺少必填项时给出容易定位的中文错误。"""

    postman_values = _load_postman_values()
    base_url = _first_value(
        postman_values,
        "TB_BASE_URL",
        "baseUrl",
        "baseurl",
    ).rstrip("/")
    tenant_username = _first_value(
        postman_values,
        "TB_TENANT_USERNAME",
        "tenantUsername",
        "username",
    )
    tenant_password = _first_value(
        postman_values,
        "TB_TENANT_PASSWORD",
        "tenantPassword",
        "password",
    )
    device_name = _first_value(
        postman_values,
        "TB_DEVICE_NAME",
        "deviceName",
    ) or "QA_TEMP_DEVICE_001"
    device_profile_name = _first_value(
        postman_values,
        "TB_DEVICE_PROFILE_NAME",
        "deviceProfileName",
    ) or "QA_TEMPERATURE_PROFILE"
    device_token = _first_value(
        postman_values,
        "TB_DEVICE_TOKEN",
        "deviceToken",
        "accessToken",
    )
    alarm_type = _first_value(
        postman_values,
        "TB_ALARM_TYPE",
        "alarmType",
    ) or "High Temperature"
    alarm_severity = _first_value(
        postman_values,
        "TB_ALARM_SEVERITY",
        "alarmSeverity",
    ) or "MAJOR"
    try:
        alarm_trigger_temperature = float(
            _first_value(
                postman_values,
                "TB_ALARM_TRIGGER_TEMPERATURE",
                "alarmTriggerTemperature",
            )
            or "80"
        )
        alarm_recovery_temperature = float(
            _first_value(
                postman_values,
                "TB_ALARM_RECOVERY_TEMPERATURE",
                "alarmRecoveryTemperature",
            )
            or "0"
        )
        alarm_wait_seconds = float(
            _first_value(
                postman_values,
                "TB_ALARM_WAIT_SECONDS",
                "alarmWaitSeconds",
            )
            or "30"
        )
    except ValueError as exc:
        raise RuntimeError(
            "告警触发温度、恢复温度和等待时间必须是数字。"
        ) from exc
    if alarm_wait_seconds <= 0:
        raise RuntimeError("TB_ALARM_WAIT_SECONDS 必须大于 0。")
    asset_name = _first_value(
        postman_values,
        "TB_ASSET_NAME",
        "assetName",
    ) or "QA_FACTORY_001"
    customer_title = _first_value(
        postman_values,
        "TB_CUSTOMER_TITLE",
        "customerTitle",
        "customerName",
    ) or "QA_CUSTOMER_001"
    customer_username = _first_value(
        postman_values,
        "TB_CUSTOMER_USERNAME",
        "customerUsername",
        "customerUserEmail",
        "customerEmail",
    ) or "qa.customer.001@example.com"
    customer_password = _first_value(
        postman_values,
        "TB_CUSTOMER_PASSWORD",
        "customerPassword",
        "customerUserPassword",
    )

    required = {
        "TB_BASE_URL": base_url,
        "TB_TENANT_USERNAME": tenant_username,
        "TB_TENANT_PASSWORD": tenant_password,
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise RuntimeError(
            "测试配置缺少必填项："
            + ", ".join(missing)
            + "。请检查 Postman local JSON 中的 baseUrl、tenantUsername、"
            + "tenantPassword，或在 .env 中填写对应的 TB_* 变量。"
        )

    try:
        request_timeout = float(
            _first_value(
                postman_values,
                "TB_REQUEST_TIMEOUT",
                "requestTimeout",
            )
            or "10"
        )
    except ValueError as exc:
        raise RuntimeError("TB_REQUEST_TIMEOUT 必须是数字，例如 10。") from exc

    if request_timeout <= 0:
        raise RuntimeError("TB_REQUEST_TIMEOUT 必须大于 0。")

    return Settings(
        base_url=base_url,
        tenant_username=tenant_username,
        tenant_password=tenant_password,
        device_name=device_name,
        device_profile_name=device_profile_name,
        device_token=device_token,
        alarm_type=alarm_type,
        alarm_severity=alarm_severity,
        alarm_trigger_temperature=alarm_trigger_temperature,
        alarm_recovery_temperature=alarm_recovery_temperature,
        alarm_wait_seconds=alarm_wait_seconds,
        asset_name=asset_name,
        customer_title=customer_title,
        customer_username=customer_username,
        customer_password=customer_password,
        request_timeout=request_timeout,
    )

