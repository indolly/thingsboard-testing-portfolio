"""封装 ThingsBoard 设备查询接口。"""

import requests

from clients.http_trace import TracedSession


class DeviceClient:
    def __init__(self, base_url: str, timeout: float = 10) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = TracedSession()
        self.session.headers.update({"Accept": "application/json"})

    @staticmethod
    def _jwt_header(token: str) -> dict[str, str]:
        return {"X-Authorization": f"Bearer {token}"}

    def search_by_name(self, name: str, token: str) -> requests.Response:
        """按名称搜索租户下的设备列表。"""

        return self.session.get(
            f"{self.base_url}/api/tenant/devices",
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

    def find_profile_by_name(
        self,
        profile_name: str,
        token: str,
    ) -> requests.Response:
        """按名称查询设备配置档案。"""

        return self.session.get(
            f"{self.base_url}/api/deviceProfiles",
            params={
                "pageSize": 10,
                "page": 0,
                "textSearch": profile_name,
                "sortProperty": "createdTime",
                "sortOrder": "DESC",
            },
            headers=self._jwt_header(token),
            timeout=self.timeout,
        )

    def create(
        self,
        name: str,
        token: str,
        device_profile_id: str,
    ) -> requests.Response:
        """创建专用测试设备；仅在按名称查询不到时调用。"""

        return self.session.post(
            f"{self.base_url}/api/device",
            json={
                "name": name,
                "type": "default",
                "deviceProfileId": {
                    "entityType": "DEVICE_PROFILE",
                    "id": device_profile_id,
                },
            },
            headers=self._jwt_header(token),
            timeout=self.timeout,
        )

    def get_credentials(self, device_id: str, token: str) -> requests.Response:
        """读取设备凭据，用于取得该测试设备自己的访问令牌。"""

        return self.session.get(
            f"{self.base_url}/api/device/{device_id}/credentials",
            headers=self._jwt_header(token),
            timeout=self.timeout,
        )

    def get_by_id(
        self,
        device_id: str,
        token: str | None = None,
    ) -> requests.Response:
        """按设备 ID 查询详情；token 为空时用于验证未认证访问。"""

        headers = self._jwt_header(token) if token else {}
        return self.session.get(
            f"{self.base_url}/api/device/{device_id}",
            headers=headers,
            timeout=self.timeout,
        )

    def close(self) -> None:
        self.session.close()

