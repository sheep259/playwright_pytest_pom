"""Client for the product catalog endpoints."""

from playwright.sync_api import APIResponse

from api.base_client import BaseClient


class ProductsApi(BaseClient):
    def list(self, **params) -> APIResponse:
        return self.get("/products", params=params or None)

    def get_by_id(self, product_id: str) -> APIResponse:
        return self.get(f"/products/{product_id}")

    def search(self, query: str) -> APIResponse:
        return self.get("/products/search", params={"q": query})
