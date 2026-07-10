"""Smoke checks that prove the framework plumbing works end to end."""

import re

import pytest
from playwright.sync_api import Page, expect

from utils.logger import get_logger

logger = get_logger("tests.smoke")


@pytest.mark.smoke
@pytest.mark.ui
def test_home_page_loads(page: Page):
    """Verify the home page is up and the framework plumbing works end to end."""
    logger.info("Opening the Toolshop home page")
    page.goto("/")

    expect(page).to_have_title(re.compile("Practice Software Testing"))

    # Semantic locator: find the sign in link by its role and accessible name
    expect(page.get_by_role("link", name="Sign in")).to_be_visible()
    logger.info("Home page is up and the Sign in link is visible")
