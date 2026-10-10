"""资产 QA_FACTORY_001 与设备 QA_TEMP_DEVICE_001 的关系测试。"""

from clients.auth_client import response_json_or_empty
from clients.relation_client import RelationClient


NONEXISTENT_ASSET_ID = "00000000-0000-0000-0000-000000000000"


def _is_target_relation(
    relation: dict,
    asset_id: str,
    device_id: str,
) -> bool:
    """判断返回对象是否为目标 Contains 关系。"""

    return (
        relation.get("from", {}).get("entityType") == "ASSET"
        and relation.get("from", {}).get("id") == asset_id
        and relation.get("to", {}).get("entityType") == "DEVICE"
        and relation.get("to", {}).get("id") == device_id
        and relation.get("type") == "Contains"
        and relation.get("typeGroup", "COMMON") == "COMMON"
    )


def test_relation_001_get_exact_contains_relation(
    relation_client: RelationClient,
    tenant_token: str,
    asset_id: str,
    device_id: str,
    target_relation: dict,
) -> None:
    """精确关系接口应返回资产到设备的 Contains 关系。"""

    response = relation_client.get_exact_relation(
        asset_id,
        device_id,
        tenant_token,
    )
    body = response_json_or_empty(response)

    assert response.status_code == 200
    assert _is_target_relation(body, asset_id, device_id)


def test_relation_002_asset_relations_include_device(
    relation_client: RelationClient,
    tenant_token: str,
    asset_id: str,
    device_id: str,
    target_relation: dict,
) -> None:
    """从工厂资产向外查询时，应包含目标温度设备。"""

    response = relation_client.get_relations_from_asset(asset_id, tenant_token)
    body = response.json()

    assert response.status_code == 200
    assert isinstance(body, list)
    assert any(
        _is_target_relation(relation, asset_id, device_id)
        for relation in body
    )


def test_relation_003_device_relations_include_asset(
    relation_client: RelationClient,
    tenant_token: str,
    asset_id: str,
    device_id: str,
    target_relation: dict,
) -> None:
    """从温度设备反向查询时，应找到所属工厂资产。"""

    response = relation_client.get_relations_to_device(device_id, tenant_token)
    body = response.json()

    assert response.status_code == 200
    assert isinstance(body, list)
    assert any(
        _is_target_relation(relation, asset_id, device_id)
        for relation in body
    )


def test_relation_004_nonexistent_asset_returns_404(
    relation_client: RelationClient,
    tenant_token: str,
) -> None:
    """从不存在的资产查询关系应返回 404，而不是空数组。"""

    response = relation_client.get_relations_from_asset(
        NONEXISTENT_ASSET_ID,
        tenant_token,
    )
    body = response_json_or_empty(response)

    assert response.status_code == 404
    assert isinstance(body.get("message"), str)
    assert body["message"].strip()


def test_relation_005_get_relations_without_jwt_returns_401(
    relation_client: RelationClient,
    asset_id: str,
) -> None:
    """不携带 JWT 查询真实资产关系应返回 401。"""

    response = relation_client.get_relations_from_asset(asset_id)
    body = response_json_or_empty(response)

    assert response.status_code == 401
    assert not body.get("from")
    assert not body.get("to")

