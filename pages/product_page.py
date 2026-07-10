"""Product detail page. No fixed path, you land here from a product card."""

from playwright.sync_api import Page

from pages.base_page import BasePage


class ProductPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.name = page.get_by_test_id("product-name")
        self.unit_price = page.get_by_test_id("unit-price")
        self.description = page.get_by_test_id("product-description")
        self.quantity_field = page.get_by_test_id("quantity")
        self.increase_quantity_button = page.get_by_test_id("increase-quantity")
        self.decrease_quantity_button = page.get_by_test_id("decrease-quantity")
        self.add_to_cart_button = page.get_by_test_id("add-to-cart")
        self.add_to_favorites_button = page.get_by_test_id("add-to-favorites")

        # The toast markup ships without a test hook, so CSS it is
        self.toast_message = page.locator(".toast-message")

    def add_to_cart(self):
        self.log.info(f"Adding '{self.name.inner_text()}' to the cart")
        self.add_to_cart_button.click()
        return self
