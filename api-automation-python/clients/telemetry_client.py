"""封装 ThingsBoard 设备遥测上报和服务端遥测查询接口。"""

from collections.abc import Iterable
from typing import Any

import requests

from clients.http_trace import TracedSession


class TelemetryClient:
    def __init__(self, base_url: str, timeout: float = 10) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = TracedSession()
        self.session.headers.update({"Accept": "application/json"})

    def post_device_telemetry(
        self,
        device_token: str,
        values: dict[str, Any],
    ) -> requests.Response:
        """设备使用访问令牌上报遥测，不使用租户 JWT。"""

        return self.session.post(
            f"{self.base_url}/api/v1/{device_token}/telemetry",
            json=values,
            timeout=self.timeout,
        )

    def get_latest_timeseries(
        self,
        device_id: str,
        keys: Iterable[str],
        tenant_token: str,
    ) -> requests.Response:
        """租户管理员使用 JWT 查询指定设备的最新遥测。"""

        return self.session.get(
            f"{self.base_url}/api/plugins/telemetry/DEVICE/"
            f"{device_id}/values/timeseries",
            params={"keys": ",".join(keys)},
            headers={"X-Authorization": f"Bearer {tenant_token}"},
            timeout=self.timeout,
        )

    def close(self) -> None:
        self.session.close()

