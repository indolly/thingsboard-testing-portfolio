"""封装 ThingsBoard 实体关系查询接口。"""

import requests

from clients.http_trace import TracedSession


class RelationClient:
    def __init__(self, base_url: str, timeout: float = 10) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = TracedSession()
        self.session.headers.update({"Accept": "application/json"})

    @staticmethod
    def _jwt_header(token: str) -> dict[str, str]:
        return {"X-Authorization": f"Bearer {token}"}

    def get_exact_relation(
        self,
        asset_id: str,
        device_id: str,
        token: str,
    ) -> requests.Response:
        """精确查询资产到设备的 Contains 关系。"""

        return self.session.get(
            f"{self.base_url}/api/relation",
            params={
                "fromId": asset_id,
                "fromType": "ASSET",
                "relationType": "Contains",
                "relationTypeGroup": "COMMON",
                "toId": device_id,
                "toType": "DEVICE",
            },
            headers=self._jwt_header(token),
            timeout=self.timeout,
        )

    def create_contains_relation(
        self,
        asset_id: str,
        device_id: str,
        token: str,
    ) -> requests.Response:
        """创建资产到设备的 COMMON/Contains 关系。"""

        return self.session.post(
            f"{self.base_url}/api/relation",
            json={
                "from": {"entityType": "ASSET", "id": asset_id},
                "to": {"entityType": "DEVICE", "id": device_id},
                "type": "Contains",
                "typeGroup": "COMMON",
            },
            headers=self._jwt_header(token),
            timeout=self.timeout,
        )

    def get_relations_from_asset(
        self,
        asset_id: str,
        token: str | None = None,
    ) -> requests.Response:
        """查询从指定资产出发的所有 COMMON 关系。"""

        headers = self._jwt_header(token) if token else {}
        return self.session.get(
            f"{self.base_url}/api/relations",
            params={
                "fromId": asset_id,
                "fromType": "ASSET",
                "relationTypeGroup": "COMMON",
            },
            headers=headers,
            timeout=self.timeout,
        )

    def get_relations_to_device(
        self,
        device_id: str,
        token: str,
    ) -> requests.Response:
        """反向查询指向指定设备的所有 COMMON 关系。"""

        return self.session.get(
            f"{self.base_url}/api/relations",
            params={
                "toId": device_id,
                "toType": "DEVICE",
                "relationTypeGroup": "COMMON",
            },
            headers=self._jwt_header(token),
            timeout=self.timeout,
        )

    def close(self) -> None:
        self.session.close()

