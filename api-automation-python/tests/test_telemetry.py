"""由 Postman TELEMETRY-001～TELEMETRY-002 迁移的遥测测试。"""

import time

import pytest
import requests

from clients.telemetry_client import TelemetryClient
from config.settings import Settings


TEMPERATURE_C = 20
TEMPERATURE_F = 68.0


def _latest_numeric_value(body: dict, key: str) -> float | None:
    """提取 ThingsBoard 最新遥测数组中的第一个数值。"""

    points = body.get(key)
    if not isinstance(points, list) or not points:
        return None
    value = points[0].get("value")
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


@pytest.fixture(scope="module")
def telemetry_upload_response(
    telemetry_client: TelemetryClient,
    device_access_token: str,
) -> requests.Response:
    """本模块只上报一次温度，供上传和查询两条用例共同验证。"""

    return telemetry_client.post_device_telemetry(
        device_access_token,
        {"temperature": TEMPERATURE_C},
    )


def test_telemetry_001_device_can_post_telemetry(
    telemetry_upload_response: requests.Response,
) -> None:
    """有效设备令牌上传遥测应返回 200 和空响应体。"""

    assert telemetry_upload_response.status_code == 200
    assert telemetry_upload_response.text.strip() == ""


def test_telemetry_002_temperature_and_fahrenheit_are_saved(
    telemetry_upload_response: requests.Response,
    telemetry_client: TelemetryClient,
    device_id: str,
    tenant_token: str,
) -> None:
    """查询最新遥测应同时得到摄氏温度和规则链转换的华氏温度。"""

    assert telemetry_upload_response.status_code == 200

    last_response: requests.Response | None = None
    last_body: dict = {}

    # 规则链可能需要很短的处理时间，最多等待约 3 秒。
    for _ in range(10):
        last_response = telemetry_client.get_latest_timeseries(
            device_id,
            ["temperature", "temperatureF"],
            tenant_token,
        )
        assert last_response.status_code == 200
        body = last_response.json()
        last_body = body if isinstance(body, dict) else {}

        temperature = _latest_numeric_value(last_body, "temperature")
        temperature_f = _latest_numeric_value(last_body, "temperatureF")
        if temperature == TEMPERATURE_C and temperature_f == TEMPERATURE_F:
            break
        time.sleep(0.3)

    assert _latest_numeric_value(last_body, "temperature") == TEMPERATURE_C
    assert _latest_numeric_value(last_body, "temperatureF") == TEMPERATURE_F

