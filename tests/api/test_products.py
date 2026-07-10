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
        """Verify product search does not leak non-matching products."""
        response = products_api.search("pliers")

        assert response.status == 200
        names = [product["name"] for product in response.json()["data"]]
        assert names, "Expected search hits for 'pliers'"
        assert all("pliers" in name.lower() for name in names), (
            f"Search leaked non-matching products: {names}"
        )
