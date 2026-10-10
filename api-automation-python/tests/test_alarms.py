"""告警查询、权限以及高温触发和恢复接口测试。"""

import time

import pytest

from clients.alarm_client import AlarmClient
from clients.auth_client import response_json_or_empty
from clients.telemetry_client import TelemetryClient
from config.settings import Settings


NONEXISTENT_ALARM_ID = "00000000-0000-0000-0000-000000000000"
VALID_ALARM_STATUSES = {
    "ACTIVE_UNACK",
    "ACTIVE_ACK",
    "CLEARED_UNACK",
    "CLEARED_ACK",
}


def test_alarm_001_find_device_alarm(
    alarm_client: AlarmClient,
    settings: Settings,
    tenant_token: str,
    device_id: str,
    target_alarm: dict,
) -> None:
    """设备告警列表应包含目标告警及有效 alarmId。"""

    response = alarm_client.find_device_alarms(
        device_id,
        tenant_token,
        settings.alarm_type,
    )
    body = response_json_or_empty(response)
    data = body.get("data")

    assert response.status_code == 200
    assert isinstance(data, list)

    alarm = next(
        (item for item in data if item.get("type") == settings.alarm_type),
        None,
    )
    assert alarm is not None, f"未找到目标告警：{settings.alarm_type}"
    assert isinstance(alarm.get("id", {}).get("id"), str)
    assert alarm["id"]["id"]
    assert alarm.get("originator", {}).get("id") == device_id
    assert alarm.get("severity") == settings.alarm_severity
    assert alarm.get("status") in VALID_ALARM_STATUSES


def test_alarm_002_get_alarm_by_id(
    alarm_client: AlarmClient,
    settings: Settings,
    tenant_token: str,
    device_id: str,
    alarm_id: str,
) -> None:
    """使用列表中取得的 alarmId 应返回同一条告警详情。"""

    response = alarm_client.get_by_id(alarm_id, tenant_token)
    body = response_json_or_empty(response)

    assert response.status_code == 200
    assert body.get("id", {}).get("id") == alarm_id
    assert body.get("type") == settings.alarm_type
    assert body.get("originator", {}).get("id") == device_id
    assert body.get("severity") == settings.alarm_severity
    assert body.get("status") in VALID_ALARM_STATUSES


def test_alarm_003_nonexistent_alarm_returns_404(
    alarm_client: AlarmClient,
    tenant_token: str,
) -> None:
    """格式正确但不存在的告警 ID 应返回 404 和提示信息。"""

    response = alarm_client.get_by_id(NONEXISTENT_ALARM_ID, tenant_token)
    body = response_json_or_empty(response)

    assert response.status_code == 404
    assert not body.get("id")
    assert isinstance(body.get("message"), str)
    assert body["message"].strip()


def test_alarm_004_get_alarm_without_jwt_returns_401(
    alarm_client: AlarmClient,
    alarm_id: str,
) -> None:
    """不携带 JWT 查询真实告警应被拒绝，且不能返回告警实体。"""

    response = alarm_client.get_by_id(alarm_id)
    body = response_json_or_empty(response)

    assert response.status_code == 401
    assert not body.get("id")
    assert not body.get("type")


def test_alarm_005_high_temperature_triggers_and_normal_temperature_clears(
    alarm_client: AlarmClient,
    telemetry_client: TelemetryClient,
    settings: Settings,
    device_access_token: str,
    device_id: str,
    tenant_token: str,
) -> None:
    """高温应触发告警，正常温度应恢复并清除同一告警。"""

    active_alarm: dict | None = None
    recovery_response = None
    poll_interval = 0.5
    attempts = max(1, int(settings.alarm_wait_seconds / poll_interval))

    try:
        trigger_response = telemetry_client.post_device_telemetry(
            device_access_token,
            {"temperature": settings.alarm_trigger_temperature},
        )
        assert trigger_response.status_code == 200

        for _ in range(attempts):
            response = alarm_client.find_device_alarms(
                device_id,
                tenant_token,
                settings.alarm_type,
                search_status="ACTIVE",
            )
            assert response.status_code == 200
            data = response_json_or_empty(response).get("data", [])
            if isinstance(data, list):
                active_alarm = next(
                    (
                        item
                        for item in data
                        if item.get("type") == settings.alarm_type
                        and item.get("originator", {}).get("id") == device_id
                        and str(item.get("status", "")).startswith("ACTIVE")
                    ),
                    None,
                )
            if active_alarm:
                break
            time.sleep(poll_interval)

        assert active_alarm is not None, (
            f"在 {settings.alarm_wait_seconds} 秒内没有产生"
            f" {settings.alarm_type} 激活告警"
        )
    finally:
        # 即使触发阶段断言失败，也尽量把设备恢复到正常温度。
        recovery_response = telemetry_client.post_device_telemetry(
            device_access_token,
            {"temperature": settings.alarm_recovery_temperature},
        )

    assert recovery_response.status_code == 200
    alarm_id = active_alarm["id"]["id"]
    cleared_alarm: dict = {}
    latest_temperature: float | None = None

    for _ in range(attempts):
        telemetry_response = telemetry_client.get_latest_timeseries(
            device_id,
            ["temperature"],
            tenant_token,
        )
        assert telemetry_response.status_code == 200
        telemetry_body = response_json_or_empty(telemetry_response)
        points = telemetry_body.get("temperature", [])
        if isinstance(points, list) and points:
            try:
                latest_temperature = float(points[0].get("value"))
            except (TypeError, ValueError):
                latest_temperature = None

        alarm_response = alarm_client.get_by_id(alarm_id, tenant_token)
        assert alarm_response.status_code == 200
        cleared_alarm = response_json_or_empty(alarm_response)
        is_cleared = str(cleared_alarm.get("status", "")).startswith(
            "CLEARED"
        )
        telemetry_recovered = (
            latest_temperature == settings.alarm_recovery_temperature
        )
        if telemetry_recovered and is_cleared:
            break
        time.sleep(poll_interval)

    final_status = str(cleared_alarm.get("status", ""))
    if not final_status.startswith("CLEARED"):
        # 自动清除失败时仍清理测试环境，但保持用例失败以暴露规则问题。
        manual_clear_response = alarm_client.clear(alarm_id, tenant_token)
        pytest.fail(
            f"恢复遥测已保存为 {latest_temperature}，但告警在 "
            f"{settings.alarm_wait_seconds} 秒内仍为 {final_status}。"
            f"已执行手工清理，返回 {manual_clear_response.status_code}。"
            "请检查设备配置档案中的 Clear alarm rule。"
        )

    assert latest_temperature == settings.alarm_recovery_temperature

