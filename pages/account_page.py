"""My account landing page, where a successful login drops you."""

from playwright.sync_api import Page

from pages.base_page import BasePage


class AccountPage(BasePage):
    path = "/account"

    def __init__(self, page: Page):
        super().__init__(page)
        self.title = page.get_by_test_id("page-title")
