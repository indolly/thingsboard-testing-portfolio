"""资产实体接口测试；关系接口在下一组用例中单独验证。"""

from clients.asset_client import AssetClient
from clients.auth_client import response_json_or_empty
from config.settings import Settings


NONEXISTENT_ASSET_ID = "00000000-0000-0000-0000-000000000000"


def test_asset_001_search_asset_by_name(
    asset_client: AssetClient,
    settings: Settings,
    tenant_token: str,
    target_asset: dict,
) -> None:
    """资产列表接口应返回 QA_FACTORY_001 及非空 assetId。"""

    response = asset_client.search_by_name(settings.asset_name, tenant_token)
    body = response_json_or_empty(response)
    data = body.get("data")

    assert response.status_code == 200
    assert isinstance(data, list)

    asset = next(
        (item for item in data if item.get("name") == settings.asset_name),
        None,
    )
    assert asset is not None, f"未找到目标资产：{settings.asset_name}"
    assert isinstance(asset.get("id", {}).get("id"), str)
    assert asset["id"]["id"]


def test_asset_002_get_asset_by_id(
    asset_client: AssetClient,
    settings: Settings,
    tenant_token: str,
    asset_id: str,
) -> None:
    """使用查询得到的 assetId 应返回同一个资产的详情。"""

    response = asset_client.get_by_id(asset_id, tenant_token)
    body = response_json_or_empty(response)

    assert response.status_code == 200
    assert body.get("name") == settings.asset_name
    assert body.get("id", {}).get("id") == asset_id
    assert isinstance(body.get("assetProfileId", {}).get("id"), str)
    assert body["assetProfileId"]["id"]


def test_asset_003_nonexistent_asset_returns_404(
    asset_client: AssetClient,
    tenant_token: str,
) -> None:
    """格式正确但不存在的资产 ID 应返回 404 和提示信息。"""

    response = asset_client.get_by_id(NONEXISTENT_ASSET_ID, tenant_token)
    body = response_json_or_empty(response)

    assert response.status_code == 404
    assert not body.get("id")
    assert isinstance(body.get("message"), str)
    assert body["message"].strip()


def test_asset_004_get_asset_without_jwt_returns_401(
    asset_client: AssetClient,
    asset_id: str,
) -> None:
    """不携带 JWT 查询真实资产应被拒绝，且不能返回资产实体。"""

    response = asset_client.get_by_id(asset_id)
    body = response_json_or_empty(response)

    assert response.status_code == 401
    assert not body.get("id")
    assert not body.get("name")

