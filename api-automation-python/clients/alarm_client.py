"""封装 ThingsBoard 告警查询接口。"""

import requests

from clients.http_trace import TracedSession


class AlarmClient:
    def __init__(self, base_url: str, timeout: float = 10) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = TracedSession()
        self.session.headers.update({"Accept": "application/json"})

    @staticmethod
    def _jwt_header(token: str) -> dict[str, str]:
        return {"X-Authorization": f"Bearer {token}"}

    def find_device_alarms(
        self,
        device_id: str,
        token: str,
        alarm_type: str | None = None,
        search_status: str = "ANY",
    ) -> requests.Response:
        """查询设备的激活和已清除告警。"""

        params: dict[str, str | int] = {
            "searchStatus": search_status,
            "pageSize": 20,
            "page": 0,
            "sortProperty": "createdTime",
            "sortOrder": "DESC",
        }
        if alarm_type:
            params["textSearch"] = alarm_type

        return self.session.get(
            f"{self.base_url}/api/alarm/DEVICE/{device_id}",
            params=params,
            headers=self._jwt_header(token),
            timeout=self.timeout,
        )

    def get_by_id(
        self,
        alarm_id: str,
        token: str | None = None,
    ) -> requests.Response:
        """按告警 ID 查询详情；不传 token 时用于未认证场景。"""

        headers = self._jwt_header(token) if token else {}
        return self.session.get(
            f"{self.base_url}/api/alarm/{alarm_id}",
            headers=headers,
            timeout=self.timeout,
        )

    def clear(self, alarm_id: str, token: str) -> requests.Response:
        """手工清除告警，仅作为自动恢复失败后的测试环境兜底清理。"""

        return self.session.post(
            f"{self.base_url}/api/alarm/{alarm_id}/clear",
            headers=self._jwt_header(token),
            timeout=self.timeout,
        )

    def close(self) -> None:
        self.session.close()

