"""Product search from the home page sidebar."""

import pytest
from playwright.sync_api import expect


@pytest.mark.ui
class TestSearch:
    def test_search_returns_matching_products(self, home_page):
        """Verify search hits are relevant and the grid renders exactly what the API returned."""
        response = home_page.search("Pliers")

        hits = response.json()["data"]
        assert hits, "Expected at least one result for 'Pliers'"

        # Relevance check on name OR description. Which fields search
        # matches differs between deployments: the public site matches
        # names, newer builds run fulltext over descriptions too. The
        # real contract is that every hit mentions the term SOMEWHERE.
        for product in hits:
            haystack = f"{product['name']} {product['description'] or ''}".lower()
            assert "pliers" in haystack, (
                f"'{product['name']}' mentions the search term nowhere"
            )

        # And the grid must render exactly what the API returned
        expect(home_page.product_names).to_have_text([p["name"] for p in hits])

    def test_search_with_no_matches_shows_message(self, home_page):
        """Verify a search with no hits shows the no-results message."""
        # A nonsense token on purpose. A phrase like "definitely not a
        # tool" is not safe here: fulltext search tokenizes words and
        # happily matches "tool" all over a tool shop.
        home_page.search("zzzznothing")

        expect(home_page.no_results_message).to_be_visible()
        expect(home_page.no_results_message).to_have_text("There are no products found.")

    def test_reset_search_restores_the_catalog(self, home_page):
        """Verify resetting a search brings the full catalog back."""
        home_page.search("Pliers")
        home_page.reset_search()

        expect(home_page.search_caption).not_to_be_visible()
        expect(home_page.product_cards.first).to_be_visible()
