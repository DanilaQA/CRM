from __future__ import annotations

from dataclasses import dataclass

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver


@dataclass(frozen=True)
class LoginLocators:
    username_or_email: tuple[str, str] = (By.CSS_SELECTOR, 'input[type="text"], input[type="email"], input[name*="login" i], input[name*="email" i]')
    password: tuple[str, str] = (By.CSS_SELECTOR, 'input[type="password"]')
    submit_button: tuple[str, str] = (By.CSS_SELECTOR, 'button[type="submit"], button')
    form_alert: tuple[str, str] = (
        By.CSS_SELECTOR,
        '[role="alert"], .alert, .error, .mat-error, .mat-mdc-form-field-error, '
        '[class*="error" i], [class*="invalid" i], [class*="message" i], '
        'small, .hint, .form-error, .validation',
    )


class LoginPage:
    URL = 'https://app.sbercrm.com/#/login'

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.locators = LoginLocators()

    def open(self) -> None:
        self.driver.get(self.URL)

    def username_input(self):
        return self.driver.find_element(*self.locators.username_or_email)

    def password_input(self):
        return self.driver.find_element(*self.locators.password)

    def submit(self):
        return self.driver.find_element(*self.locators.submit_button)

    def alerts(self):
        return self.driver.find_elements(*self.locators.form_alert)

    def login(self, username: str = '', password: str = '') -> None:
        username_field = self.username_input()
        password_field = self.password_input()
        username_field.clear()
        username_field.send_keys(username)
        password_field.clear()
        password_field.send_keys(password)
        self.submit().click()

    def alert_texts(self) -> list[str]:
        return [el.text.strip() for el in self.alerts() if el.text.strip()]
