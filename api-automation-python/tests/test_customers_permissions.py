"""客户实体、资源分配和客户用户权限边界测试。"""

from clients.auth_client import AuthClient, response_json_or_empty
from clients.customer_client import CustomerClient
from clients.device_client import DeviceClient
from config.settings import Settings


def _page_data(response) -> list:
    body = response_json_or_empty(response)
    data = body.get("data")
    assert isinstance(data, list)
    return data


def test_customer_001_search_customer_by_title(
    customer_client: CustomerClient,
    settings: Settings,
    tenant_token: str,
    target_customer: dict,
) -> None:
    """租户管理员应能按标题找到 QA_CUSTOMER_001。"""

    response = customer_client.search_customers(
        settings.customer_title,
        tenant_token,
    )
    data = _page_data(response)

    assert response.status_code == 200
    customer = next(
        (item for item in data if item.get("title") == settings.customer_title),
        None,
    )
    assert customer is not None
    assert customer.get("id", {}).get("id")


def test_customer_002_get_customer_by_id(
    customer_client: CustomerClient,
    settings: Settings,
    tenant_token: str,
    customer_id: str,
) -> None:
    """按 customerId 应返回同一个客户。"""

    response = customer_client.get_by_id(customer_id, tenant_token)
    body = response_json_or_empty(response)

    assert response.status_code == 200
    assert body.get("id", {}).get("id") == customer_id
    assert body.get("title") == settings.customer_title


def test_customer_003_customer_assets_include_target_asset(
    customer_client: CustomerClient,
    tenant_token: str,
    customer_id: str,
    asset_id: str,
    ensure_customer_assignments: None,
) -> None:
    """客户名下资产列表应包含已分配工厂资产。"""

    response = customer_client.get_customer_assets(customer_id, tenant_token)
    data = _page_data(response)

    assert response.status_code == 200
    assert any(item.get("id", {}).get("id") == asset_id for item in data)


def test_customer_004_customer_devices_include_target_device(
    customer_client: CustomerClient,
    tenant_token: str,
    customer_id: str,
    device_id: str,
    ensure_customer_assignments: None,
) -> None:
    """客户名下设备列表应包含已分配温度设备。"""

    response = customer_client.get_customer_devices(customer_id, tenant_token)
    data = _page_data(response)

    assert response.status_code == 200
    assert any(item.get("id", {}).get("id") == device_id for item in data)


def test_customer_005_customer_dashboards_response_is_page(
    customer_client: CustomerClient,
    tenant_token: str,
    customer_id: str,
) -> None:
    """客户仪表板接口应返回合法分页结构，允许 data 为空。"""

    response = customer_client.get_customer_dashboards(customer_id, tenant_token)
    data = _page_data(response)

    assert response.status_code == 200
    assert isinstance(data, list)


def test_customer_006_get_customer_without_jwt_returns_401(
    customer_client: CustomerClient,
    customer_id: str,
) -> None:
    """未认证用户不能读取客户详情。"""

    response = customer_client.get_by_id(customer_id)
    body = response_json_or_empty(response)

    assert response.status_code == 401
    assert not body.get("id")
    assert not body.get("title")


def test_customer_007_customer_user_can_login(
    auth_client: AuthClient,
    settings: Settings,
) -> None:
    """有效客户用户账号应返回 200 和非空 JWT。"""

    assert settings.customer_password, (
        "Postman local JSON 中缺少 customerPassword/customerUserPassword"
    )
    response = auth_client.login(
        settings.customer_username,
        settings.customer_password,
    )
    body = response_json_or_empty(response)

    assert response.status_code == 200
    assert isinstance(body.get("token"), str)
    assert body["token"].strip()


def test_customer_008_current_user_is_customer_user(
    auth_client: AuthClient,
    settings: Settings,
    customer_token: str,
    customer_id: str,
) -> None:
    """客户 JWT 对应的角色、邮箱和 customerId 应正确。"""

    response = auth_client.get_current_user(customer_token)
    body = response_json_or_empty(response)

    assert response.status_code == 200
    assert body.get("authority") == "CUSTOMER_USER"
    assert body.get("email") == settings.customer_username
    assert body.get("customerId", {}).get("id") == customer_id


def test_customer_009_customer_user_can_access_assigned_device(
    device_client: DeviceClient,
    customer_token: str,
    device_id: str,
    settings: Settings,
    ensure_customer_assignments: None,
) -> None:
    """客户用户应能读取分配给自己的设备。"""

    response = device_client.get_by_id(device_id, customer_token)
    body = response_json_or_empty(response)

    assert response.status_code == 200
    assert body.get("id", {}).get("id") == device_id
    assert body.get("name") == settings.device_name


def test_customer_010_customer_user_cannot_list_customers(
    customer_client: CustomerClient,
    settings: Settings,
    customer_token: str,
) -> None:
    """客户用户不能读取租户的全部客户列表，应返回 403。"""

    response = customer_client.search_customers(
        settings.customer_title,
        customer_token,
    )
    body = response_json_or_empty(response)

    assert response.status_code == 403
    assert not body.get("data")

