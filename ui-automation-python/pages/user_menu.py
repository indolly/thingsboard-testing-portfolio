"""ThingsBoard 顶部用户菜单页对象。"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as conditions
from selenium.webdriver.support.ui import WebDriverWait


class UserMenu:
    MENU_BUTTON = (
        By.CSS_SELECTOR,
        "tb-user-menu button, tb-user-menu [role='button']",
    )
    LOGOUT_ITEM = (
        By.XPATH,
        "//div[contains(@class, 'cdk-overlay-container')]"
        "//button[.//mat-icon[normalize-space()='exit_to_app']"
        " or contains(normalize-space(.), '注销')"
        " or contains(normalize-space(.), 'Logout')]",
    )

    def __init__(self, driver, timeout: float):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def logout(self) -> None:
        menu_button = self.wait.until(
            conditions.element_to_be_clickable(self.MENU_BUTTON)
        )
        self.driver.execute_script("arguments[0].click();", menu_button)
        logout_item = self.wait.until(
            conditions.element_to_be_clickable(self.LOGOUT_ITEM)
        )
        self.driver.execute_script("arguments[0].click();", logout_item)
        self.wait.until(lambda driver: "/login" in driver.current_url)
        self.wait.until(
            conditions.visibility_of_element_located(
                (By.CSS_SELECTOR, "#username-input, input[name='username'], input[type='email']")
            )
        )
