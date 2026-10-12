"""Product endpoints: listing, detail, search, and the error contract."""

import pytest


@pytest.mark.api
class TestProductCatalog:
    def test_list_is_paginated_and_has_products(self, products_api):
        """Verify the product list is paginated and not empty."""
        response = products_api.list()

        assert response.status == 200
        body = response.json()
        assert body["current_page"] == 1
        assert len(body["data"]) > 0

    def test_every_listed_product_has_the_core_fields(self, products_api):
        """Verify every listed product satisfies the core field contract."""
        products = products_api.list().json()["data"]

        for product in products:
            assert product["id"], "Found a product without an id"
            assert product["name"], f"Product {product['id']} has no name"
            assert product["price"] > 0, f"'{product['name']}' has price {product['price']}"
            assert isinstance(product["in_stock"], bool)

    def test_detail_matches_the_listing(self, products_api):
        """Verify the detail endpoint agrees with the listing endpoint."""
        listed = products_api.list().json()["data"][0]

        response = products_api.get_by_id(listed["id"])

        assert response.status == 200
        detail = response.json()
        assert detail["name"] == listed["name"]
        assert detail["price"] == listed["price"]

    def test_unknown_product_gets_404(self, products_api):
        """Verify unknown product ids get the documented 404 message."""
        response = products_api.get_by_id("does-not-exist")

        assert response.status == 404
        assert response.json()["message"] == "Requested item not found"

    def test_search_only_returns_matches(self, products_api):
        """Verify every search hit mentions the term in its name or description."""
        response = products_api.search("pliers")

        assert response.status == 200
        hits = response.json()["data"]
        assert hits, "Expected search hits for 'pliers'"

        # Name OR description on purpose. The public deployment matches
        # names, newer builds run fulltext over descriptions too. Every
        # hit mentioning the term somewhere is the deployment-agnostic
        # contract, and a true leak still fails.
        for product in hits:
            haystack = f"{product['name']} {product['description'] or ''}".lower()
            assert "pliers" in haystack, (
                f"'{product['name']}' matches neither by name nor description"
            )

    @pytest.mark.parametrize("term", ["pliers", "hammer", "saw"])
    def test_search_terms_only_return_matching_products(self, products_api, term):
        """Verify each search term only returns products mentioning it."""
        response = products_api.search(term)

        assert response.status == 200
        hits = response.json()["data"]
        assert hits, f"Expected search hits for '{term}'"

        for product in hits:
            haystack = f"{product['name']} {product['description'] or ''}".lower()
            assert term in haystack,(
                f"'{product['name']}' matches neither by name nor description"
            )

    def test_search_no_results_returns_empty_list(self, products_api):
        """Verify a search with no hits returns 200 and an empty list."""
        response = products_api.search("thisworddoesnotexist12345")
        assert response.status == 200
        hits = response.json()["data"]
        assert hits == [], f"Expected no hits, got {hits}"
