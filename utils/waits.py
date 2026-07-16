"""Polling helper for outcomes that no single locator can express.

Playwright's expect() retries one locator against one condition. Some
oracles need more, like "every price in the grid is ascending". This is
the same retry-until-true idea for arbitrary conditions.
"""

import time


def wait_until(condition, description: str, timeout: float = 10.0, interval: float = 0.25):
    """Retry condition() until it returns something truthy, or fail loudly."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        result = condition()
        if result:
            return result
        time.sleep(interval)
    raise AssertionError(f"Timed out after {timeout}s waiting until {description}")
