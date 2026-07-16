"""Home page: the product grid plus the search, sort, and filter sidebar."""

from playwright.sync_api import Page, expect

from pages.base_page import BasePage
from pages.product_page import ProductPage


class HomePage(BasePage):
    path = "/"

    def __init__(self, page: Page):
        super().__init__(page)

        # Sidebar controls
        self.search_box = page.get_by_placeholder("Search")
        self.search_button = page.get_by_role("button", name="Search", exact=True)
        self.reset_search_button = page.get_by_test_id("search-reset")
        self.sort_dropdown = page.get_by_test_id("sort")

        # Search state markers the app flips on and off
        self.search_caption = page.get_by_test_id("search-caption")
        self.search_completed = page.get_by_test_id("search_completed")
        self.no_results_message = page.get_by_test_id("no-results")

        # Product grid. Attribute prefix CSS because every card's hook
        # embeds its product id: data-test="product-<id>"
        self.product_cards = page.locator("a[data-test^='product-']")
        self.product_names = page.get_by_test_id("product-name")
        self.product_prices = page.get_by_test_id("product-price")

    def open(self):
        super().open()
        # The grid fills in async, so do not hand the page over until
        # at least one product card is actually there
        expect(self.product_cards.first).to_be_visible()
        return self

    def search(self, term: str):
        """Run a search and hand back the API response it triggered,
        same pattern as sort_by. Lets tests assert the grid against
        exactly what the search endpoint returned."""
        self.log.info(f"Searching for '{term}'")
        self.search_box.fill(term)
        with self.page.expect_response(lambda r: "/products/search" in r.url and r.ok) as response_info:
            self.search_button.click()
        # This marker appears once the results have rendered
        expect(self.search_completed).to_be_visible()
        return response_info.value

    def reset_search(self):
        self.log.info("Resetting search")
        self.reset_search_button.click()
        expect(self.search_caption).not_to_be_visible()
        return self

    def sort_by(self, option_label: str):
        """Pick a sort option. Deliberately does NOT wait on a network
        response: whether sorting even fires an API call is an
        implementation detail that differs between deployments (newer
        builds sort server-side, older builds re-order the grid client
        side with no request at all). Tests poll the visible outcome.
        """
        self.log.info(f"Sorting products by '{option_label}'")
        self.sort_dropdown.select_option(label=option_label)
        return self

    def filter_by_category(self, category_name: str):
        """Tick a category checkbox. Same deal as sort_by: no network
        wait, the visible outcome is the contract."""
        self.log.info(f"Filtering by category '{category_name}'")
        self.page.get_by_role("checkbox", name=category_name).check()
        return self

    def visible_product_names(self) -> list[str]:
        return self.product_names.all_inner_texts()

    def visible_prices(self) -> list[float]:
        return [
            float(text.replace("$", "").strip())
            for text in self.product_prices.all_inner_texts()
        ]

    def open_product(self, name: str) -> ProductPage:
        """Click the product card that contains the given name."""
        self.log.info(f"Opening product '{name}'")
        # XPath on purpose: we know the h5 with the name and need the
        # card link WRAPPING it. Climbing to an ancestor is exactly
        # what XPath is for.
        self.page.locator(f"xpath=//a[.//h5[@data-test='product-name' and normalize-space()='{name}']]").click()
        return ProductPage(self.page)
