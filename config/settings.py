"""Environment settings so URLs never get hardcoded in tests."""

import os

# The UI base URL is NOT here. It lives in pytest.ini as base_url, where
# pytest-playwright reads it and bakes it into every browser context.
# This file only holds config that our own code consumes directly.
# Environment variables win over the defaults here. That way CI or a
# local override can point the suite at a different environment
# without touching any code.
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.practicesoftwaretesting.com")

# There are no login credentials here on purpose. The suite registers
# its own throwaway user per run (see test_user in conftest.py) because
# the Toolshop locks any account after 3 failed logins and the seeded
# demo accounts are shared with everyone practicing against this site.
