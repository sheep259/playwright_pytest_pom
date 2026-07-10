"""Client for the user account endpoints."""

from playwright.sync_api import APIResponse

from api.base_client import BaseClient


class UsersApi(BaseClient):
    def register(self, user: dict) -> APIResponse:
        return self.post("/users/register", data=user)
