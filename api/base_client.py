"""Thin foundation for API clients, the request-side twin of BasePage."""

from playwright.sync_api import APIRequestContext, APIResponse

from utils.logger import get_logger


class BaseClient:
    """Wraps an APIRequestContext with logging and optional bearer auth."""

    def __init__(self, context: APIRequestContext, token: str | None = None):
        self.context = context
        self.log = get_logger(self.__class__.__name__)
        self._headers = {"Authorization": f"Bearer {token}"} if token else {}

    def get(self, url: str, **kwargs) -> APIResponse:
        response = self.context.get(url, headers=self._headers, **kwargs)
        self.log.info(f"GET {url} -> {response.status}")
        return response

    def post(self, url: str, **kwargs) -> APIResponse:
        response = self.context.post(url, headers=self._headers, **kwargs)
        self.log.info(f"POST {url} -> {response.status}")
        return response
