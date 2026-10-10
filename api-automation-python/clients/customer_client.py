"""封装 ThingsBoard 客户实体及客户名下资源查询接口。"""

import requests

from clients.http_trace import TracedSession


class CustomerClient:
    def __init__(self, base_url: str, timeout: float = 10) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = TracedSession()
        self.session.headers.update({"Accept": "application/json"})

    @staticmethod
    def _jwt_header(token: str) -> dict[str, str]:
        return {"X-Authorization": f"Bearer {token}"}

    @staticmethod
    def _page_params(text_search: str | None = None) -> dict[str, str | int]:
        params: dict[str, str | int] = {
            "pageSize": 10,
            "page": 0,
            "sortProperty": "createdTime",
            "sortOrder": "DESC",
        }
        if text_search:
            params["textSearch"] = text_search
        return params

    def search_customers(self, title: str, token: str) -> requests.Response:
        """查询当前租户的客户列表。"""

        return self.session.get(
            f"{self.base_url}/api/customers",
            params=self._page_params(title),
            headers=self._jwt_header(token),
            timeout=self.timeout,
        )

    def create(self, title: str, token: str) -> requests.Response:
        """创建专用测试客户；仅在按标题查询不到时调用。"""

        return self.session.post(
            f"{self.base_url}/api/customer",
            json={"title": title},
            headers=self._jwt_header(token),
            timeout=self.timeout,
        )

    def assign_asset(
        self,
        customer_id: str,
        asset_id: str,
        token: str,
    ) -> requests.Response:
        """把测试资产分配给测试客户。"""

        return self.session.post(
            f"{self.base_url}/api/customer/{customer_id}/asset/{asset_id}",
            headers=self._jwt_header(token),
            timeout=self.timeout,
        )

    def assign_device(
        self,
        customer_id: str,
        device_id: str,
        token: str,
    ) -> requests.Response:
        """把测试设备分配给测试客户。"""

        return self.session.post(
            f"{self.base_url}/api/customer/{customer_id}/device/{device_id}",
            headers=self._jwt_header(token),
            timeout=self.timeout,
        )

    def get_by_id(
        self,
        customer_id: str,
        token: str | None = None,
    ) -> requests.Response:
        """按 customerId 查询详情。"""

        headers = self._jwt_header(token) if token else {}
        return self.session.get(
            f"{self.base_url}/api/customer/{customer_id}",
            headers=headers,
            timeout=self.timeout,
        )

    def get_customer_assets(
        self,
        customer_id: str,
        token: str,
    ) -> requests.Response:
        return self.session.get(
            f"{self.base_url}/api/customer/{customer_id}/assets",
            params=self._page_params(),
            headers=self._jwt_header(token),
            timeout=self.timeout,
        )

    def get_customer_devices(
        self,
        customer_id: str,
        token: str,
    ) -> requests.Response:
        return self.session.get(
            f"{self.base_url}/api/customer/{customer_id}/devices",
            params=self._page_params(),
            headers=self._jwt_header(token),
            timeout=self.timeout,
        )

    def get_customer_dashboards(
        self,
        customer_id: str,
        token: str,
    ) -> requests.Response:
        return self.session.get(
            f"{self.base_url}/api/customer/{customer_id}/dashboards",
            params=self._page_params(),
            headers=self._jwt_header(token),
            timeout=self.timeout,
        )

    def close(self) -> None:
        self.session.close()

