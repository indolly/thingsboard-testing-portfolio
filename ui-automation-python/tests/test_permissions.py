"""客户用户在设备页面的 UI 权限边界测试。"""

import allure

from pages.devices_page import DevicesPage
from pages.login_page import LoginPage
from pages.navigation_menu import NavigationMenu


@allure.epic("ThingsBoard UI 自动化")
@allure.feature("权限控制")
@allure.story("客户用户设备权限")
@allure.title("UI-PERM-001 客户用户可查看已分配设备且无客户管理入口")
def test_ui_perm_001_customer_user_has_limited_device_access(browser, ui_settings):
    login_page = LoginPage(browser, ui_settings.base_url, ui_settings.timeout)
    devices_page = DevicesPage(browser, ui_settings.base_url, ui_settings.timeout)
    navigation_menu = NavigationMenu(browser)

    with allure.step("客户用户登录 ThingsBoard"):
        login_page.open()
        login_page.login(
            ui_settings.customer_username,
            ui_settings.customer_password,
        )
        login_page.wait_until_logged_in()

    with allure.step("查询已分配的目标设备"):
        devices_page.open()
        devices_page.search(ui_settings.device_name)
        devices_page.wait_for_device(ui_settings.device_name)

    with allure.step("验证客户用户看不到租户级客户管理入口"):
        assert not navigation_menu.has_customer_management_entry(), (
            "客户用户不应看到客户管理入口，实际菜单："
            f"{navigation_menu.visible_item_texts()}"
        )
