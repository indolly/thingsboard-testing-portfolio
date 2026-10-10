"""pytest 公共夹具：统一创建配置、客户端、JWT 和 Allure 业务标签。"""

import json
from pathlib import Path
import time

import allure
import pytest

from clients.auth_client import AuthClient, response_json_or_empty
from clients.alarm_client import AlarmClient
from clients.asset_client import AssetClient
from clients.device_client import DeviceClient
from clients.telemetry_client import TelemetryClient
from clients.relation_client import RelationClient
from clients.customer_client import CustomerClient
from clients.http_trace import SecretString, clear_api_trace, get_api_trace
from config.settings import Settings, get_settings


ALLURE_FEATURES = {
    "test_auth": "01 认证管理",
    "test_devices": "02 设备管理",
    "test_telemetry": "03 遥测管理",
    "test_alarms": "04 告警管理",
    "test_assets": "05 资产管理",
    "test_relations": "06 实体关系",
    "test_customers_permissions": "07 客户与权限",
}


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item) -> None:
    """每条用例开始前清空上一条用例的 HTTP 记录。"""

    clear_api_trace()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """仅当 setup/call/teardown 失败时附加脱敏后的 HTTP 交互。"""

    outcome = yield
    report = outcome.get_result()
    if not report.failed:
        return

    trace = get_api_trace()
    if trace:
        allure.attach(
            json.dumps(trace, ensure_ascii=False, indent=2),
            name=f"脱敏HTTP交互-{report.when}",
            attachment_type=allure.attachment_type.JSON,
        )


@pytest.fixture(autouse=True)
def allure_business_labels(request) -> None:
    """把 Python 文件映射为 Allure 的业务模块，并使用中文用例说明。"""

    module_name = request.node.module.__name__.split(".")[-1]
    feature = ALLURE_FEATURES.get(module_name, "其他接口")
    description = (request.node.function.__doc__ or request.node.name).strip()

    allure.dynamic.epic("ThingsBoard REST API 自动化")
    allure.dynamic.feature(feature)
    allure.dynamic.story(description)
    allure.dynamic.title(description)


def pytest_sessionfinish(session, exitstatus) -> None:
    """为 Allure 报告写入不含秘密的测试环境信息。"""

    results_dir = Path(__file__).resolve().parent / "allure-results"
    if not results_dir.exists():
        return

    try:
        settings = get_settings()
        environment_lines = [
            "Project=ThingsBoard REST API Tests",
            "Environment=Local",
            f"Base.URL={settings.base_url}",
            "Test.Framework=pytest",
            "Authentication=JWT and Device Access Token",
        ]
        (results_dir / "environment.properties").write_text(
            "\n".join(environment_lines) + "\n",
            encoding="utf-8",
        )
    except (OSError, RuntimeError):
        # 环境信息写入失败不能覆盖真实的测试执行结果。
        return


@pytest.fixture(scope="session")
def settings() -> Settings:
    """整个测试会话只读取一次环境配置。"""

    try:
        return get_settings()
    except RuntimeError as exc:
        pytest.exit(str(exc), returncode=2)


@pytest.fixture(scope="session")
def auth_client(settings: Settings):
    """复用 HTTP 连接，并在测试结束后正确关闭。"""

    client = AuthClient(settings.base_url, settings.request_timeout)
    yield client
    client.close()


@pytest.fixture(scope="session")
def tenant_token(auth_client: AuthClient, settings: Settings) -> str:
    """获取后续认证用例需要的有效 JWT；失败时立即给出原因。"""

    response = auth_client.login(
        settings.tenant_username,
        settings.tenant_password,
    )
    if response.status_code != 200:
        pytest.fail(
            f"前置登录失败：期望 200，实际 {response.status_code}，"
            f"响应：{response.text[:300]}",
        )

    token = response_json_or_empty(response).get("token")
    if not isinstance(token, str) or not token.strip():
        pytest.fail("前置登录响应未包含非空 token，后续认证用例无法执行。")
    return SecretString(token)


@pytest.fixture(scope="session")
def device_client(settings: Settings):
    """复用设备接口的 HTTP 连接。"""

    client = DeviceClient(settings.base_url, settings.request_timeout)
    yield client
    client.close()


@pytest.fixture(scope="session")
def target_device_profile_id(
    device_client: DeviceClient,
    settings: Settings,
    tenant_token: str,
) -> str:
    """查找规则链所依赖的设备配置档案；它属于测试基础设施。"""

    response = device_client.find_profile_by_name(
        settings.device_profile_name,
        tenant_token,
    )
    if response.status_code != 200:
        pytest.fail(
            f"设备配置档案查询失败：{response.status_code}，"
            f"响应：{response.text[:300]}"
        )
    data = response_json_or_empty(response).get("data")
    if not isinstance(data, list):
        pytest.fail("设备配置档案响应中的 data 不是数组。")
    profile = next(
        (
            item
            for item in data
            if item.get("name") == settings.device_profile_name
        ),
        None,
    )
    if not isinstance(profile, dict):
        pytest.fail(
            f"缺少测试基础设施设备配置档案："
            f"{settings.device_profile_name}。"
            "请先在平台配置该 profile 及其规则链。"
        )
    profile_id = profile.get("id", {}).get("id")
    if not isinstance(profile_id, str) or not profile_id:
        pytest.fail("设备配置档案没有有效的 id.id。")
    return profile_id


@pytest.fixture(scope="session")
def target_device(
    device_client: DeviceClient,
    settings: Settings,
    tenant_token: str,
    target_device_profile_id: str,
) -> dict:
    """搜索或创建目标设备，供需要 deviceId 的后续用例复用。"""

    response = device_client.search_by_name(settings.device_name, tenant_token)
    if response.status_code != 200:
        pytest.fail(
            f"设备前置查询失败：期望 200，实际 {response.status_code}，"
            f"响应：{response.text[:300]}"
        )

    body = response_json_or_empty(response)
    data = body.get("data")
    if not isinstance(data, list):
        pytest.fail("设备查询响应中的 data 不是数组。")

    device = next(
        (item for item in data if item.get("name") == settings.device_name),
        None,
    )
    if not isinstance(device, dict):
        create_response = device_client.create(
            settings.device_name,
            tenant_token,
            target_device_profile_id,
        )
        if create_response.status_code not in {200, 201}:
            pytest.fail(
                f"目标设备不存在且自动创建失败：{create_response.status_code}，"
                f"响应：{create_response.text[:300]}"
            )
        device = response_json_or_empty(create_response)

    actual_profile_id = device.get("deviceProfileId", {}).get("id")
    if actual_profile_id != target_device_profile_id:
        pytest.fail(
            f"测试设备 {settings.device_name} 未绑定"
            f" {settings.device_profile_name}。"
            "为避免自动修改现有设备配置，请在平台修正后重试。"
        )

    device_id = device.get("id", {}).get("id")
    if not isinstance(device_id, str) or not device_id:
        pytest.fail("目标设备没有有效的 id.id。")
    return device


@pytest.fixture(scope="session")
def device_id(target_device: dict) -> str:
    """从目标设备实体中提取 deviceId。"""

    return target_device["id"]["id"]


@pytest.fixture(scope="session")
def device_access_token(
    device_client: DeviceClient,
    tenant_token: str,
    device_id: str,
) -> str:
    """从目标设备凭据中自动读取访问令牌，避免手工复制过期 token。"""

    response = device_client.get_credentials(device_id, tenant_token)
    if response.status_code != 200:
        pytest.fail(
            f"读取设备凭据失败：{response.status_code}，"
            f"响应：{response.text[:300]}"
        )
    credentials_id = response_json_or_empty(response).get("credentialsId")
    if not isinstance(credentials_id, str) or not credentials_id:
        pytest.fail("设备凭据响应中没有非空 credentialsId。")
    return SecretString(credentials_id)


@pytest.fixture(scope="session")
def telemetry_client(settings: Settings):
    """复用遥测接口的 HTTP 连接。"""

    client = TelemetryClient(settings.base_url, settings.request_timeout)
    yield client
    client.close()


@pytest.fixture(scope="session")
def alarm_client(settings: Settings):
    """复用告警接口的 HTTP 连接。"""

    client = AlarmClient(settings.base_url, settings.request_timeout)
    yield client
    client.close()


@pytest.fixture(scope="session")
def target_alarm(
    alarm_client: AlarmClient,
    telemetry_client: TelemetryClient,
    settings: Settings,
    tenant_token: str,
    device_id: str,
    device_access_token: str,
) -> dict:
    """查询目标告警；不存在时自动触发并恢复一次以建立基线。"""

    response = alarm_client.find_device_alarms(
        device_id,
        tenant_token,
        settings.alarm_type,
    )
    if response.status_code != 200:
        pytest.fail(
            f"告警前置查询失败：期望 200，实际 {response.status_code}，"
            f"响应：{response.text[:300]}"
        )

    body = response_json_or_empty(response)
    data = body.get("data")
    if not isinstance(data, list):
        pytest.fail("告警查询响应中的 data 不是数组。")

    alarm = next(
        (item for item in data if item.get("type") == settings.alarm_type),
        None,
    )
    if not isinstance(alarm, dict):
        recovery_response = None
        try:
            trigger_response = telemetry_client.post_device_telemetry(
                device_access_token,
                {"temperature": settings.alarm_trigger_temperature},
            )
            if trigger_response.status_code != 200:
                pytest.fail(
                    f"自动触发告警的遥测上报失败："
                    f"{trigger_response.status_code}"
                )

            poll_interval = 0.5
            attempts = max(
                1,
                int(settings.alarm_wait_seconds / poll_interval),
            )
            for _ in range(attempts):
                active_response = alarm_client.find_device_alarms(
                    device_id,
                    tenant_token,
                    settings.alarm_type,
                    search_status="ACTIVE",
                )
                active_data = response_json_or_empty(active_response).get(
                    "data",
                    [],
                )
                if isinstance(active_data, list):
                    alarm = next(
                        (
                            item
                            for item in active_data
                            if item.get("type") == settings.alarm_type
                        ),
                        None,
                    )
                if isinstance(alarm, dict):
                    break
                time.sleep(poll_interval)
        finally:
            recovery_response = telemetry_client.post_device_telemetry(
                device_access_token,
                {"temperature": settings.alarm_recovery_temperature},
            )

        if recovery_response.status_code != 200:
            pytest.fail(
                f"自动恢复告警的遥测上报失败："
                f"{recovery_response.status_code}"
            )
        if not isinstance(alarm, dict):
            pytest.fail(
                f"在 {settings.alarm_wait_seconds} 秒内未自动生成"
                f" {settings.alarm_type} 告警。"
            )

    alarm_id = alarm.get("id", {}).get("id")
    if not isinstance(alarm_id, str) or not alarm_id:
        pytest.fail("目标告警没有有效的 id.id。")
    return alarm


@pytest.fixture(scope="session")
def alarm_id(target_alarm: dict) -> str:
    """从目标告警实体中提取 alarmId。"""

    return target_alarm["id"]["id"]


@pytest.fixture(scope="session")
def asset_client(settings: Settings):
    """复用资产接口的 HTTP 连接。"""

    client = AssetClient(settings.base_url, settings.request_timeout)
    yield client
    client.close()


@pytest.fixture(scope="session")
def target_asset(
    asset_client: AssetClient,
    settings: Settings,
    tenant_token: str,
) -> dict:
    """搜索目标资产，供关系测试复用 assetId。"""

    response = asset_client.search_by_name(settings.asset_name, tenant_token)
    if response.status_code != 200:
        pytest.fail(
            f"资产前置查询失败：期望 200，实际 {response.status_code}，"
            f"响应：{response.text[:300]}"
        )

    body = response_json_or_empty(response)
    data = body.get("data")
    if not isinstance(data, list):
        pytest.fail("资产查询响应中的 data 不是数组。")

    asset = next(
        (item for item in data if item.get("name") == settings.asset_name),
        None,
    )
    if not isinstance(asset, dict):
        create_response = asset_client.create(settings.asset_name, tenant_token)
        if create_response.status_code not in {200, 201}:
            pytest.fail(
                f"目标资产不存在且自动创建失败：{create_response.status_code}，"
                f"响应：{create_response.text[:300]}"
            )
        asset = response_json_or_empty(create_response)

    asset_id = asset.get("id", {}).get("id")
    if not isinstance(asset_id, str) or not asset_id:
        pytest.fail("目标资产没有有效的 id.id。")
    return asset


@pytest.fixture(scope="session")
def asset_id(target_asset: dict) -> str:
    """从目标资产实体中提取 assetId。"""

    return target_asset["id"]["id"]


@pytest.fixture(scope="session")
def relation_client(settings: Settings):
    """复用实体关系接口的 HTTP 连接。"""

    client = RelationClient(settings.base_url, settings.request_timeout)
    yield client
    client.close()


@pytest.fixture(scope="session")
def target_relation(
    relation_client: RelationClient,
    tenant_token: str,
    asset_id: str,
    device_id: str,
) -> dict:
    """确保测试资产到测试设备的 Contains 关系存在。"""

    response = relation_client.get_exact_relation(
        asset_id,
        device_id,
        tenant_token,
    )
    body = response_json_or_empty(response)
    if response.status_code == 200 and body.get("type") == "Contains":
        return body

    if response.status_code not in {200, 404}:
        pytest.fail(
            f"检查测试关系失败：{response.status_code}，"
            f"响应：{response.text[:300]}"
        )

    create_response = relation_client.create_contains_relation(
        asset_id,
        device_id,
        tenant_token,
    )
    if create_response.status_code not in {200, 201}:
        pytest.fail(
            f"测试关系不存在且自动创建失败：{create_response.status_code}，"
            f"响应：{create_response.text[:300]}"
        )
    return response_json_or_empty(create_response)


@pytest.fixture(scope="session")
def customer_client(settings: Settings):
    """复用客户接口的 HTTP 连接。"""

    client = CustomerClient(settings.base_url, settings.request_timeout)
    yield client
    client.close()


@pytest.fixture(scope="session")
def target_customer(
    customer_client: CustomerClient,
    settings: Settings,
    tenant_token: str,
) -> dict:
    """搜索目标客户，供后续权限用例复用 customerId。"""

    response = customer_client.search_customers(
        settings.customer_title,
        tenant_token,
    )
    if response.status_code != 200:
        pytest.fail(
            f"客户前置查询失败：期望 200，实际 {response.status_code}，"
            f"响应：{response.text[:300]}"
        )

    body = response_json_or_empty(response)
    data = body.get("data")
    if not isinstance(data, list):
        pytest.fail("客户查询响应中的 data 不是数组。")

    customer = next(
        (item for item in data if item.get("title") == settings.customer_title),
        None,
    )
    if not isinstance(customer, dict):
        create_response = customer_client.create(
            settings.customer_title,
            tenant_token,
        )
        if create_response.status_code not in {200, 201}:
            pytest.fail(
                f"目标客户不存在且自动创建失败：{create_response.status_code}，"
                f"响应：{create_response.text[:300]}"
            )
        customer = response_json_or_empty(create_response)

    customer_id = customer.get("id", {}).get("id")
    if not isinstance(customer_id, str) or not customer_id:
        pytest.fail("目标客户没有有效的 id.id。")
    return customer


@pytest.fixture(scope="session")
def customer_id(target_customer: dict) -> str:
    return target_customer["id"]["id"]


@pytest.fixture(scope="session")
def ensure_customer_assignments(
    customer_client: CustomerClient,
    tenant_token: str,
    customer_id: str,
    asset_id: str,
    device_id: str,
) -> None:
    """确保目标资产和设备均已分配给测试客户。"""

    assets_response = customer_client.get_customer_assets(
        customer_id,
        tenant_token,
    )
    assets = response_json_or_empty(assets_response).get("data", [])
    if assets_response.status_code != 200 or not isinstance(assets, list):
        pytest.fail(
            f"检查客户资产分配失败：{assets_response.status_code}，"
            f"响应：{assets_response.text[:300]}"
        )
    if not any(item.get("id", {}).get("id") == asset_id for item in assets):
        response = customer_client.assign_asset(customer_id, asset_id, tenant_token)
        if response.status_code not in {200, 201}:
            pytest.fail(
                f"自动分配测试资产失败：{response.status_code}，"
                f"响应：{response.text[:300]}"
            )

    devices_response = customer_client.get_customer_devices(
        customer_id,
        tenant_token,
    )
    devices = response_json_or_empty(devices_response).get("data", [])
    if devices_response.status_code != 200 or not isinstance(devices, list):
        pytest.fail(
            f"检查客户设备分配失败：{devices_response.status_code}，"
            f"响应：{devices_response.text[:300]}"
        )
    if not any(item.get("id", {}).get("id") == device_id for item in devices):
        response = customer_client.assign_device(
            customer_id,
            device_id,
            tenant_token,
        )
        if response.status_code not in {200, 201}:
            pytest.fail(
                f"自动分配测试设备失败：{response.status_code}，"
                f"响应：{response.text[:300]}"
            )


@pytest.fixture(scope="session")
def customer_token(auth_client: AuthClient, settings: Settings) -> str:
    """登录客户用户并返回其 JWT。"""

    if not settings.customer_password:
        pytest.fail(
            "Postman local JSON 中未找到 customerPassword/customerUserPassword。"
            "请把客户用户密码保存到相应变量。"
        )

    response = auth_client.login(
        settings.customer_username,
        settings.customer_password,
    )
    if response.status_code != 200:
        pytest.fail(
            f"客户用户前置登录失败：期望 200，实际 {response.status_code}，"
            f"响应：{response.text[:300]}"
        )

    token = response_json_or_empty(response).get("token")
    if not isinstance(token, str) or not token.strip():
        pytest.fail("客户用户登录响应未包含非空 token。")
    return SecretString(token)

