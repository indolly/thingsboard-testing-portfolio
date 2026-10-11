"""ThingsBoard 设备列表页对象。"""

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as conditions
from selenium.webdriver.support.ui import WebDriverWait


class DevicesPage:
    PAGE_CONTAINER = (
        By.CSS_SELECTOR,
        "tb-device-table, tb-entity-table, mat-table, table",
    )
    SEARCH_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='search']"
        " | //button[.//mat-icon[normalize-space()='search']]"
        " | //button[contains(translate(@aria-label, 'SEARCH', 'search'), 'search')]"
        " | //button[contains(@aria-label, '搜索')]",
    )
    SEARCH_INPUT = (
        By.CSS_SELECTOR,
        "input[placeholder*='Search'], input[placeholder*='search'], "
        "input[placeholder*='搜索'], input[aria-label*='Search'], "
        "input[aria-label*='search'], input[aria-label*='搜索'], "
        "input.mat-mdc-input-element",
    )
    DETAILS_DRAWER = (By.CSS_SELECTOR, "mat-drawer.tb-details-drawer")
    DETAILS_TITLE = (
        By.CSS_SELECTOR,
        "mat-drawer.tb-details-drawer .tb-details-title-text",
    )

    def __init__(self, driver, base_url: str, timeout: float):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, timeout)

    def open(self) -> None:
        self.driver.get(f"{self.base_url}/entities/devices")
        self.wait.until(conditions.presence_of_element_located(self.PAGE_CONTAINER))

    def search(self, device_name: str) -> None:
        inputs = [
            element
            for element in self.driver.find_elements(*self.SEARCH_INPUT)
            if element.is_displayed()
        ]
        if not inputs:
            def visible_search_button(driver):
                for element in driver.find_elements(*self.SEARCH_BUTTON):
                    if element.is_displayed() and element.is_enabled():
                        return element
                return False

            search_button = self.wait.until(visible_search_button)
            self.driver.execute_script("arguments[0].click();", search_button)

        def visible_search_input(driver):
            for element in driver.find_elements(*self.SEARCH_INPUT):
                if element.is_displayed() and element.is_enabled():
                    return element
            return False

        search_input = self.wait.until(visible_search_input)
        search_input.send_keys(Keys.CONTROL, "a")
        search_input.send_keys(Keys.BACKSPACE)
        search_input.send_keys(device_name)

    def wait_for_device(self, device_name: str):
        locator = (
            By.XPATH,
            "//*[self::mat-row or self::tr or @role='row']"
            f"[.//*[normalize-space()={device_name!r}]]",
        )
        return self.wait.until(conditions.visibility_of_element_located(locator))

    def open_device_details(self, device_name: str) -> None:
        row = self.wait_for_device(device_name)
        name = row.find_element(
            By.XPATH,
            f".//*[normalize-space()={device_name!r}]",
        )
        self.driver.execute_script("arguments[0].click();", name)
        self.wait_for_device_details(device_name)

    def wait_for_device_details(self, device_name: str) -> None:
        self.wait.until(conditions.visibility_of_element_located(self.DETAILS_DRAWER))

        def expected_title_is_visible(driver):
            for element in driver.find_elements(*self.DETAILS_TITLE):
                if element.is_displayed() and element.text.strip() == device_name:
                    return True
            return False

        self.wait.until(expected_title_is_visible)

    def visible_detail_actions(self) -> set[str]:
        drawer = self.wait.until(
            conditions.visibility_of_element_located(self.DETAILS_DRAWER)
        )
        return {
            element.text.strip()
            for element in drawer.find_elements(By.CSS_SELECTOR, "button")
            if element.is_displayed() and element.text.strip()
        }
