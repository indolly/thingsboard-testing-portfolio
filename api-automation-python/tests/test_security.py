"""认证、敏感信息和角色越权的基础接口安全测试。"""

from uuid import uuid4

import pytest

from clients.auth_client import AuthClient, response_json_or_empty
from clients.device_client import DeviceClient
from config.settings import Settings


@pytest.fixture(scope="module")
def unassigned_security_device_id(
    device_client: DeviceClient,
    tenant_token: str,
    target_device_profile_id: str,
):
    """创建未分配给客户的临时设备，并在模块结束时自动删除。"""

    device_name = f"QA_SECURITY_UNASSIGNED_{uuid4().hex[:8]}"
    response = device_client.create(
        device_name,
        tenant_token,
        target_device_profile_id,
    )
    body = response_json_or_empty(response)
    device_id = body.get("id", {}).get("id")

    assert response.status_code == 200
    assert isinstance(device_id, str) and device_id

    yield device_id

    cleanup_response = device_client.delete(device_id, tenant_token)
    assert cleanup_response.status_code == 200


def test_security_001_current_user_without_jwt_is_rejected(
    auth_client: AuthClient,
) -> None:
    """未携带 JWT 不能读取当前用户身份。"""

    response = auth_client.get_current_user()
    body = response_json_or_empty(response)

    assert response.status_code == 401
    assert not body.get("email")
    assert not body.get("authority")


def test_security_002_tampered_valid_jwt_is_rejected(
    auth_client: AuthClient,
    tenant_token: str,
) -> None:
    """篡改有效 JWT 的签名后必须返回 401。"""

    header, payload, signature = tenant_token.split(".")
    replacement = "A" if signature[0] != "A" else "B"
    tampered_token = f"{header}.{payload}.{replacement}{signature[1:]}"
    response = auth_client.get_current_user(tampered_token)
    body = response_json_or_empty(response)

    assert response.status_code == 401
    assert not body.get("email")
    assert not body.get("authority")


def test_security_003_failed_login_does_not_echo_sensitive_input(
    auth_client: AuthClient,
    settings: Settings,
) -> None:
    """登录失败响应不能回显密码、返回令牌或暴露服务端堆栈。"""

    probe_password = f"{settings.tenant_password}_security_probe"
    response = auth_client.login(settings.tenant_username, probe_password)
    body = response_json_or_empty(response)
    response_text = response.text.lower()

    assert response.status_code == 401
    assert probe_password.lower() not in response_text
    assert not body.get("token")
    assert not body.get("refreshToken")
    assert "stacktrace" not in response_text
    assert "org.springframework" not in response_text


def test_security_004_device_credentials_without_jwt_are_rejected(
    device_client: DeviceClient,
    device_id: str,
) -> None:
    """未认证用户不能读取设备访问令牌。"""

    response = device_client.get_credentials(device_id)
    body = response_json_or_empty(response)

    assert response.status_code == 401
    assert not body.get("credentialsValue")


def test_security_005_customer_user_can_read_assigned_device_credentials(
    device_client: DeviceClient,
    customer_token: str,
    device_id: str,
    ensure_customer_assignments: None,
) -> None:
    """按 OpenAPI 权限定义，客户用户可读取已分配设备的凭据。"""

    response = device_client.get_credentials(device_id, customer_token)
    body = response_json_or_empty(response)

    assert response.status_code == 200
    assert body.get("deviceId", {}).get("id") == device_id
    assert body.get("credentialsType")
    assert body.get("credentialsId") or body.get("credentialsValue")


def test_security_006_customer_user_cannot_access_unassigned_device(
    device_client: DeviceClient,
    customer_token: str,
    unassigned_security_device_id: str,
) -> None:
    """客户用户不能利用已知 ID 读取未分配给自己的设备。"""

    response = device_client.get_by_id(
        unassigned_security_device_id,
        customer_token,
    )
    body = response_json_or_empty(response)

    assert response.status_code == 403
    assert not body.get("id")


def test_security_007_customer_user_cannot_read_unassigned_device_credentials(
    device_client: DeviceClient,
    customer_token: str,
    unassigned_security_device_id: str,
) -> None:
    """客户用户不能利用已知 ID 读取未分配设备的访问令牌。"""

    response = device_client.get_credentials(
        unassigned_security_device_id,
        customer_token,
    )
    body = response_json_or_empty(response)

    assert response.status_code == 403
    assert not body.get("credentialsValue")


def test_security_008_customer_user_cannot_search_tenant_device_directory(
    device_client: DeviceClient,
    settings: Settings,
    customer_token: str,
) -> None:
    """客户用户不能越权查询租户级设备目录。"""

    response = device_client.search_by_name(
        settings.device_name,
        customer_token,
    )
    body = response_json_or_empty(response)

    assert response.status_code == 403
    assert not body.get("data")
