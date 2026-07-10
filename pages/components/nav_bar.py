"""The top navigation bar, present on every page of the site.

Pages compose this instead of re-declaring the same locators over and
over. If the navbar changes, this is the only file that cares.
"""

from playwright.sync_api import Page


class NavBar:
    def __init__(self, page: Page):
        self.page = page

        # The menu itself is semantic, so roles and names do the work
        menu = page.get_by_role("menubar", name="Main menu")
        self.home_link = menu.get_by_role("link", name="Home")
        self.contact_link = menu.get_by_role("link", name="Contact")
        self.sign_in_link = menu.get_by_role("link", name="Sign in")
        self.categories_button = menu.get_by_role("button", name="Categories")

        # These only exist in certain states and their accessible names
        # change at runtime (the user menu shows whoever is logged in,
        # the cart shows a count), so the data-test hooks are the stable
        # choice here.
        self.user_menu = page.get_by_test_id("nav-menu")
        self.sign_out_link = page.get_by_test_id("nav-sign-out")
        self.cart_link = page.get_by_test_id("nav-cart")
        self.cart_quantity = page.get_by_test_id("cart-quantity")

    def sign_out(self):
        self.user_menu.click()
        self.sign_out_link.click()
