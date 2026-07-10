"""Client for the auth endpoints."""

from playwright.sync_api import APIResponse

from api.base_client import BaseClient


class AuthApi(BaseClient):
    def login(self, email: str, password: str) -> APIResponse:
        # The password rides in the payload but never hits the log,
        # BaseClient only logs method, URL, and status
        return self.post("/users/login", data={"email": email, "password": password})

    def token_for(self, email: str, password: str) -> str:
        """Login that hard-fails unless it worked. Meant for fixtures."""
        response = self.login(email, password)
        assert response.ok, f"Login as {email} failed with status {response.status}"
        return response.json()["access_token"]

    def me(self) -> APIResponse:
        return self.get("/users/me")
