"""Foundation every page object builds on."""

from playwright.sync_api import Page

from pages.components.nav_bar import NavBar
from utils.logger import get_logger


class BasePage:
    """Holds what every page shares: the Page handle, a logger, and the navbar."""

    # Subclasses set this to their route, e.g. "/auth/login"
    path = "/"

    def __init__(self, page: Page):
        self.page = page
        self.nav = NavBar(page)
        self.log = get_logger(self.__class__.__name__)

    def open(self):
        """Navigate straight to this page. base_url from pytest.ini supplies the host."""
        self.log.info(f"Opening {self.path}")
        self.page.goto(self.path)
        return self
