"""Sign in behavior, the happy path and the sad ones."""

import re

import pytest
from playwright.sync_api import expect

from pages.account_page import AccountPage


@pytest.mark.ui
class TestLogin:
    def test_valid_login(self, login_page, test_user):
        """Verify a registered user can sign in and lands on My account."""
        login_page.login(test_user["email"], test_user["password"])

        account = AccountPage(login_page.page)
        expect(account.page).to_have_url(re.compile("/account"))
        expect(account.title).to_have_text("My account")

    def test_invalid_credentials_show_error(self, login_page):
        """Verify bad credentials show an error and stay on the login page."""
        # Nonexistent email on purpose, same reasoning as the API twin
        # of this test: 3 failed logins lock a real account (HTTP 423)
        login_page.login("no.such.user@example.com", "notthepassword")

        expect(login_page.error_message).to_have_text("Invalid email or password")
        # And we better still be on the login page
        expect(login_page.page).to_have_url(re.compile("/auth/login"))

    def test_sign_out_returns_to_signed_out_state(self, login_page, test_user):
        """Verify signing out brings back the signed-out navbar state."""
        login_page.login(test_user["email"], test_user["password"])
        account = AccountPage(login_page.page)
        expect(account.title).to_have_text("My account")

        account.nav.sign_out()

        expect(account.nav.sign_in_link).to_be_visible()
