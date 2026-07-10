"""Auth endpoints: token issuing and token gating."""

import pytest

from api.auth_api import AuthApi


@pytest.mark.api
class TestLoginEndpoint:
    def test_valid_login_returns_bearer_token(self, auth_api, test_user):
        """Verify a valid login returns a usable bearer token."""
        response = auth_api.login(test_user["email"], test_user["password"])

        assert response.status == 200
        body = response.json()
        assert body["token_type"] == "bearer"
        assert body["access_token"], "Expected a non-empty access token"
        assert body["expires_in"] > 0

    def test_invalid_credentials_get_401(self, auth_api):
        """Verify invalid credentials get the 401 Unauthorized contract."""
        # Nonexistent email on purpose. Wrong passwords against a REAL
        # account lock it after 3 tries (HTTP 423), so this is the only
        # safe way to exercise the 401 contract repeatedly.
        response = auth_api.login("no.such.user@example.com", "notthepassword")

        assert response.status == 401
        assert response.json() == {"error": "Unauthorized"}


@pytest.mark.api
class TestProtectedEndpoints:
    def test_me_returns_the_logged_in_user(self, api_context, user_token, test_user):
        """Verify /users/me identifies the holder of the token."""
        response = AuthApi(api_context, token=user_token).me()

        assert response.status == 200
        assert response.json()["email"] == test_user["email"]

    def test_me_without_a_token_gets_401(self, auth_api):
        """Verify /users/me is gated behind authentication."""
        response = auth_api.me()

        assert response.status == 401
        assert response.json()["message"] == "Unauthorized"
