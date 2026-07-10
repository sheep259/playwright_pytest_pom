"""Product search from the home page sidebar."""

import pytest
from playwright.sync_api import expect


@pytest.mark.ui
class TestSearch:
    def test_search_returns_matching_products(self, home_page):
        """Verify searching only returns products matching the term."""
        home_page.search("Pliers")

        names = home_page.visible_product_names()
        assert names, "Expected at least one result for 'Pliers'"
        assert all("pliers" in name.lower() for name in names), (
            f"Got results that do not match the search term: {names}"
        )

    def test_search_with_no_matches_shows_message(self, home_page):
        """Verify a search with no hits shows the no-results message."""
        home_page.search("definitely not a tool")

        expect(home_page.no_results_message).to_be_visible()
        expect(home_page.no_results_message).to_have_text("There are no products found.")

    def test_reset_search_restores_the_catalog(self, home_page):
        """Verify resetting a search brings the full catalog back."""
        home_page.search("Pliers")
        home_page.reset_search()

        expect(home_page.search_caption).not_to_be_visible()
        expect(home_page.product_cards.first).to_be_visible()
