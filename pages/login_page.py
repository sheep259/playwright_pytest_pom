"""Sign in page."""

from playwright.sync_api import Page

from pages.base_page import BasePage


class LoginPage(BasePage):
    path = "/auth/login"

    def __init__(self, page: Page):
        super().__init__(page)
        self.email_field = page.get_by_test_id("email")
        self.password_field = page.get_by_test_id("password")
        self.submit_button = page.get_by_test_id("login-submit")
        self.error_message = page.get_by_test_id("login-error")
        self.register_link = page.get_by_test_id("register-link")

    def login(self, email: str, password: str):
        """Fill the form and submit. The password stays out of the log on purpose."""
        self.log.info(f"Logging in as {email}")
        self.email_field.fill(email)
        self.password_field.fill(password)
        self.submit_button.click()
        return self
