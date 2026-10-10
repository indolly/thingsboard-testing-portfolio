"""封装 ThingsBoard 资产查询接口。"""

import requests

from clients.http_trace import TracedSession


class AssetClient:
    def __init__(self, base_url: str, timeout: float = 10) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = TracedSession()
        self.session.headers.update({"Accept": "application/json"})

    @staticmethod
    def _jwt_header(token: str) -> dict[str, str]:
        return {"X-Authorization": f"Bearer {token}"}

    def search_by_name(self, name: str, token: str) -> requests.Response:
        """按名称搜索租户下的资产列表。"""

        return self.session.get(
            f"{self.base_url}/api/tenant/assets",
            params={
                "pageSize": 10,
                "page": 0,
                "textSearch": name,
                "sortProperty": "createdTime",
                "sortOrder": "DESC",
            },
            headers=self._jwt_header(token),
            timeout=self.timeout,
        )

    def create(self, name: str, token: str) -> requests.Response:
        """创建专用测试资产；仅在按名称查询不到时调用。"""

        return self.session.post(
            f"{self.base_url}/api/asset",
            json={"name": name, "type": "default"},
            headers=self._jwt_header(token),
            timeout=self.timeout,
        )

    def get_by_id(
        self,
        asset_id: str,
        token: str | None = None,
    ) -> requests.Response:
        """按资产 ID 查询详情；token 为空时用于未认证场景。"""

        headers = self._jwt_header(token) if token else {}
        return self.session.get(
            f"{self.base_url}/api/asset/{asset_id}",
            headers=headers,
            timeout=self.timeout,
        )

    def close(self) -> None:
        self.session.close()

