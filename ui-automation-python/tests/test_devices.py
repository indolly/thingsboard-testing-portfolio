"""设备管理页面的核心 UI 测试。"""

import allure

from pages.devices_page import DevicesPage
from pages.login_page import LoginPage


@allure.epic("ThingsBoard UI 自动化")
@allure.feature("设备管理")
@allure.story("查询设备")
@allure.title("UI-DEVICE-001 租户管理员可以搜索目标设备")
def test_ui_device_001_tenant_can_search_target_device(browser, ui_settings):
    login_page = LoginPage(browser, ui_settings.base_url, ui_settings.timeout)
    devices_page = DevicesPage(browser, ui_settings.base_url, ui_settings.timeout)

    with allure.step("租户管理员登录 ThingsBoard"):
        login_page.open()
        login_page.login(
            ui_settings.tenant_username,
            ui_settings.tenant_password,
        )
        login_page.wait_until_logged_in()

    with allure.step("打开设备管理页面"):
        devices_page.open()

    with allure.step(f"搜索设备 {ui_settings.device_name}"):
        devices_page.search(ui_settings.device_name)

    with allure.step("验证目标设备出现在结果列表"):
        devices_page.wait_for_device(ui_settings.device_name)


@allure.epic("ThingsBoard UI 自动化")
@allure.feature("设备管理")
@allure.story("设备详情")
@allure.title("UI-DEVICE-002 租户管理员可以打开目标设备详情")
def test_ui_device_002_tenant_can_open_target_device_details(browser, ui_settings):
    login_page = LoginPage(browser, ui_settings.base_url, ui_settings.timeout)
    devices_page = DevicesPage(browser, ui_settings.base_url, ui_settings.timeout)

    with allure.step("租户管理员登录 ThingsBoard"):
        login_page.open()
        login_page.login(
            ui_settings.tenant_username,
            ui_settings.tenant_password,
        )
        login_page.wait_until_logged_in()

    with allure.step(f"搜索设备 {ui_settings.device_name}"):
        devices_page.open()
        devices_page.search(ui_settings.device_name)
        devices_page.wait_for_device(ui_settings.device_name)

    with allure.step("打开设备详情并核对详情标题"):
        devices_page.open_device_details(ui_settings.device_name)
        devices_page.wait_for_device_details(ui_settings.device_name)
