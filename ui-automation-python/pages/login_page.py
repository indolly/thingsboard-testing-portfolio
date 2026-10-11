"""ThingsBoard 登录页对象。"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as conditions
from selenium.webdriver.support.ui import WebDriverWait


class LoginPage:
    USERNAME = (By.CSS_SELECTOR, "#username-input, input[name='username'], input[type='email']")
    PASSWORD = (By.CSS_SELECTOR, "#password-input, input[name='password'], input[type='password']")
    SUBMIT = (By.CSS_SELECTOR, "button[type='submit']")
    ERROR_FEEDBACK = (
        By.CSS_SELECTOR,
        "mat-error, .mat-mdc-snack-bar-label, .mat-snack-bar-container, tb-snack-bar-component",
    )

    def __init__(self, driver, base_url: str, timeout: float):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, timeout)

    def open(self) -> None:
        self.driver.get(f"{self.base_url}/login")
        self.wait.until(conditions.visibility_of_element_located(self.USERNAME))
        self.wait.until(conditions.visibility_of_element_located(self.PASSWORD))

    def login(self, username: str, password: str) -> None:
        username_input = self.wait.until(
            conditions.element_to_be_clickable(self.USERNAME)
        )
        password_input = self.wait.until(
            conditions.element_to_be_clickable(self.PASSWORD)
        )
        username_input.clear()
        username_input.send_keys(username)
        password_input.clear()
        password_input.send_keys(password)
        self.wait.until(conditions.element_to_be_clickable(self.SUBMIT)).click()

    def wait_until_logged_in(self) -> None:
        self.wait.until(lambda driver: "/login" not in driver.current_url)

    def wait_for_login_failure(self) -> None:
        def failure_is_visible(driver) -> bool:
            if "/login" not in driver.current_url:
                return False
            elements = driver.find_elements(*self.ERROR_FEEDBACK)
            return any(element.is_displayed() for element in elements)

        self.wait.until(failure_is_visible)
