"""由 Postman AUTH-001～AUTH-004 迁移而来的认证接口测试。"""

from clients.auth_client import AuthClient, response_json_or_empty
from config.settings import Settings


def test_auth_001_valid_tenant_login_returns_token(
    auth_client: AuthClient,
    settings: Settings,
) -> None:
    """有效租户管理员登录应返回 200 和非空 JWT。"""

    response = auth_client.login(
        settings.tenant_username,
        settings.tenant_password,
    )
    body = response_json_or_empty(response)

    assert response.status_code == 200
    assert isinstance(body.get("token"), str)
    assert body["token"].strip()


def test_auth_002_invalid_password_returns_401_without_token(
    auth_client: AuthClient,
    settings: Settings,
) -> None:
    """错误密码应被拒绝，而且失败响应不能泄露 JWT。"""

    response = auth_client.login(
        settings.tenant_username,
        settings.tenant_password + "_definitely_wrong",
    )
    body = response_json_or_empty(response)

    assert response.status_code == 401
    assert not body.get("token")


def test_auth_003_valid_jwt_returns_current_tenant_admin(
    auth_client: AuthClient,
    settings: Settings,
    tenant_token: str,
) -> None:
    """有效 JWT 应能查询当前用户，且身份和账号正确。"""

    response = auth_client.get_current_user(tenant_token)
    body = response_json_or_empty(response)

    assert response.status_code == 200
    assert body.get("authority") == "TENANT_ADMIN"
    assert body.get("email") == settings.tenant_username


def test_auth_004_invalid_jwt_returns_401_without_user(
    auth_client: AuthClient,
) -> None:
    """伪造 JWT 应返回 401，而且不能返回当前用户数据。"""

    response = auth_client.get_current_user("invalid.jwt.token")
    body = response_json_or_empty(response)

    assert response.status_code == 401
    assert not body.get("email")
    assert not body.get("authority")

