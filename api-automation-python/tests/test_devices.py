"""由 Postman DEVICE-001～DEVICE-004 迁移而来的设备接口测试。"""

from clients.auth_client import response_json_or_empty
from clients.device_client import DeviceClient
from config.settings import Settings


NONEXISTENT_DEVICE_ID = "00000000-0000-0000-0000-000000000000"


def test_device_001_search_device_by_name(
    device_client: DeviceClient,
    settings: Settings,
    tenant_token: str,
    target_device: dict,
) -> None:
    """设备列表接口应返回目标设备及非空 ID。"""

    response = device_client.search_by_name(settings.device_name, tenant_token)
    body = response_json_or_empty(response)
    data = body.get("data")

    assert response.status_code == 200
    assert isinstance(data, list)

    device = next(
        (item for item in data if item.get("name") == settings.device_name),
        None,
    )
    assert device is not None, f"未找到目标设备：{settings.device_name}"
    assert isinstance(device.get("id", {}).get("id"), str)
    assert device["id"]["id"]


def test_device_002_get_device_by_id(
    device_client: DeviceClient,
    settings: Settings,
    tenant_token: str,
    device_id: str,
) -> None:
    """使用查询得到的 deviceId 应返回同一台设备的完整详情。"""

    response = device_client.get_by_id(device_id, tenant_token)
    body = response_json_or_empty(response)

    assert response.status_code == 200
    assert body.get("name") == settings.device_name
    assert body.get("id", {}).get("id") == device_id
    assert isinstance(body.get("deviceProfileId", {}).get("id"), str)
    assert body["deviceProfileId"]["id"]


def test_device_003_nonexistent_device_returns_404(
    device_client: DeviceClient,
    tenant_token: str,
) -> None:
    """格式正确但不存在的设备 ID 应返回 404 和提示信息。"""

    response = device_client.get_by_id(NONEXISTENT_DEVICE_ID, tenant_token)
    body = response_json_or_empty(response)

    assert response.status_code == 404
    assert not body.get("id")
    assert isinstance(body.get("message"), str)
    assert body["message"].strip()


def test_device_004_get_device_without_jwt_returns_401(
    device_client: DeviceClient,
    device_id: str,
) -> None:
    """不携带 JWT 查询真实设备应被拒绝，且不能返回设备实体。"""

    response = device_client.get_by_id(device_id)
    body = response_json_or_empty(response)

    assert response.status_code == 401
    assert not body.get("id")
    assert not body.get("name")

