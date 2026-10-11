"""UI 自动化公共夹具和失败证据。"""

from pathlib import Path
import re

import allure
import pytest
from selenium import webdriver

from config.settings import get_ui_settings


PROJECT_ROOT = Path(__file__).resolve().parent
SCREENSHOT_DIR = PROJECT_ROOT / "reports" / "screenshots"


@pytest.fixture(scope="session")
def ui_settings():
    return get_ui_settings()


@pytest.fixture
def browser(request, ui_settings):
    if ui_settings.browser == "edge":
        options = webdriver.EdgeOptions()
        if ui_settings.headless:
            options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
        driver = webdriver.Edge(options=options)
    else:
        options = webdriver.ChromeOptions()
        if ui_settings.headless:
            options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu")
        driver = webdriver.Chrome(options=options)

    driver.set_page_load_timeout(ui_settings.timeout)
    yield driver

    report = getattr(request.node, "rep_call", None)
    if report is not None and report.failed:
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", request.node.nodeid)
        screenshot_path = SCREENSHOT_DIR / f"{safe_name}.png"
        driver.save_screenshot(str(screenshot_path))
        allure.attach.file(
            str(screenshot_path),
            name="失败页面截图",
            attachment_type=allure.attachment_type.PNG,
        )
        allure.attach(
            driver.current_url,
            name="失败页面地址",
            attachment_type=allure.attachment_type.TEXT,
        )
    driver.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)
