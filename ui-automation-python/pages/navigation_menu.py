"""ThingsBoard 左侧导航菜单页对象。"""

from selenium.webdriver.common.by import By


class NavigationMenu:
    MENU_ITEMS = (
        By.CSS_SELECTOR,
        "mat-sidenav a, mat-sidenav button, tb-side-menu a, tb-side-menu button",
    )

    def __init__(self, driver):
        self.driver = driver

    def visible_item_texts(self) -> list[str]:
        return [
            " ".join(element.text.split())
            for element in self.driver.find_elements(*self.MENU_ITEMS)
            if element.is_displayed() and element.text.strip()
        ]

    def has_customer_management_entry(self) -> bool:
        customer_labels = ("客户", "Customers")
        return any(
            any(label in item for label in customer_labels)
            for item in self.visible_item_texts()
        )
