"""认证页面的最小 UI 冒烟测试。"""

import allure

from pages.login_page import LoginPage
from pages.user_menu import UserMenu


@allure.epic("ThingsBoard UI 自动化")
@allure.feature("认证")
@allure.story("租户管理员登录")
@allure.title("UI-AUTH-001 租户管理员使用有效账号登录成功")
def test_ui_auth_001_valid_tenant_login(browser, ui_settings):
    login_page = LoginPage(browser, ui_settings.base_url, ui_settings.timeout)

    with allure.step("打开 ThingsBoard 登录页"):
        login_page.open()

    with allure.step("输入有效的租户管理员账号和密码"):
        login_page.login(
            ui_settings.tenant_username,
            ui_settings.tenant_password,
        )

    with allure.step("验证登录成功并离开登录页"):
        login_page.wait_until_logged_in()
        assert "/login" not in browser.current_url


@allure.epic("ThingsBoard UI 自动化")
@allure.feature("认证")
@allure.story("租户管理员登录")
@allure.title("UI-AUTH-002 错误密码不能登录")
def test_ui_auth_002_invalid_password_is_rejected(browser, ui_settings):
    login_page = LoginPage(browser, ui_settings.base_url, ui_settings.timeout)

    with allure.step("打开 ThingsBoard 登录页"):
        login_page.open()

    with allure.step("使用正确账号和错误密码登录"):
        login_page.login(
            ui_settings.tenant_username,
            f"{ui_settings.tenant_password}-wrong",
        )

    with allure.step("验证页面拒绝登录并显示错误反馈"):
        login_page.wait_for_login_failure()
        assert "/login" in browser.current_url


@allure.epic("ThingsBoard UI 自动化")
@allure.feature("认证")
@allure.story("会话退出")
@allure.title("UI-AUTH-003 租户管理员注销后返回登录页")
def test_ui_auth_003_logout_ends_current_session(browser, ui_settings):
    login_page = LoginPage(browser, ui_settings.base_url, ui_settings.timeout)
    user_menu = UserMenu(browser, ui_settings.timeout)

    with allure.step("租户管理员登录 ThingsBoard"):
        login_page.open()
        login_page.login(
            ui_settings.tenant_username,
            ui_settings.tenant_password,
        )
        login_page.wait_until_logged_in()

    with allure.step("从顶部用户菜单执行注销"):
        user_menu.logout()

    with allure.step("验证当前会话结束并返回登录页"):
        assert "/login" in browser.current_url
