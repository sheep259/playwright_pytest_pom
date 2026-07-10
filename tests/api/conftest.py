"""Fixtures for the API suite. The shared APIRequestContext and the
run's registered test user live in the root conftest, since UI tests
use them for setup too."""

import pytest

from api.auth_api import AuthApi
from api.products_api import ProductsApi


@pytest.fixture
def auth_api(api_context) -> AuthApi:
    return AuthApi(api_context)


@pytest.fixture
def products_api(api_context) -> ProductsApi:
    return ProductsApi(api_context)


@pytest.fixture
def user_token(auth_api, test_user) -> str:
    # Function scoped on purpose. The API hands out 5 minute tokens
    # (expires_in: 300), so caching one for a whole session is asking
    # for mystery 401s the moment the suite grows.
    return auth_api.token_for(test_user["email"], test_user["password"])
