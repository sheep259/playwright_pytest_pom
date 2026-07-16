"""Product grid sorting and filtering, plus the product detail page."""

import pytest
from playwright.sync_api import expect

from utils.waits import wait_until


@pytest.mark.ui
class TestProductGrid:
    def test_sort_by_price_low_to_high(self, home_page):
        """Verify sorting by price low to high orders the grid ascending."""
        home_page.sort_by("Price (Low - High)")

        # Poll the outcome instead of intercepting a network call. HOW
        # the grid gets sorted differs between deployments, WHAT the
        # user ends up seeing is the contract.
        def grid_shows_ascending_prices():
            prices = home_page.visible_prices()
            return bool(prices) and prices == sorted(prices)

        wait_until(grid_shows_ascending_prices, "the grid shows ascending prices")

    def test_filter_by_category(self, home_page):
        """Verify the Hammer category filter only leaves hammers in the grid."""
        home_page.filter_by_category("Hammer")

        def only_hammers_remain():
            names = home_page.visible_product_names()
            return bool(names) and all("hammer" in name.lower() for name in names)

        wait_until(only_hammers_remain, "only Hammer products remain in the grid")


@pytest.mark.ui
class TestProductDetail:
    def test_detail_page_matches_the_grid_card(self, home_page):
        """Verify a detail page shows the same name and price as its grid card."""
        name = home_page.visible_product_names()[0]
        grid_price = home_page.visible_prices()[0]

        product = home_page.open_product(name)

        expect(product.name).to_have_text(name)
        expect(product.unit_price).to_contain_text(f"{grid_price:.2f}")

    def test_add_product_to_cart(self, home_page):
        """Verify adding to the cart shows the toast and updates the cart badge."""
        product = home_page.open_product("Combination Pliers")
        product.add_to_cart()

        expect(product.toast_message).to_have_text("Product added to shopping cart.")
        expect(product.nav.cart_quantity).to_have_text("1")
