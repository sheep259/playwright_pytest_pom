"""Product grid sorting and filtering, plus the product detail page."""

import pytest
from playwright.sync_api import expect


@pytest.mark.ui
class TestProductGrid:
    def test_sort_by_price_low_to_high(self, home_page):
        """Verify sorting by price low to high orders the grid ascending."""
        response = home_page.sort_by("Price (Low - High)")

        # Sync point: retry until the grid shows exactly what the sort
        # call returned, THEN read prices off it safely
        expected_names = [product["name"] for product in response.json()["data"]]
        expect(home_page.product_names).to_have_text(expected_names)

        prices = home_page.visible_prices()
        assert prices, "Expected the grid to have products after sorting"
        assert prices == sorted(prices), f"Prices are not ascending: {prices}"

    def test_filter_by_category(self, home_page):
        """Verify the Hammer category filter only leaves hammers in the grid."""
        response = home_page.filter_by_category("Hammer")

        expected_names = [product["name"] for product in response.json()["data"]]
        expect(home_page.product_names).to_have_text(expected_names)

        assert expected_names, "Expected at least one product in the Hammer category"
        assert all("hammer" in name.lower() for name in expected_names), (
            f"Got products outside the Hammer category: {expected_names}"
        )


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
