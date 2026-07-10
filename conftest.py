"""Shared fixtures and hooks for the whole suite."""

import base64
import uuid
from datetime import datetime
from pathlib import Path

import pytest
from playwright.sync_api import expect
from pytest_html import extras as html_extras

from api.users_api import UsersApi
from config import settings
from pages.home_page import HomePage
from pages.login_page import LoginPage
from utils.logger import get_logger

logger = get_logger("conftest")

SCREENSHOT_DIR = Path(__file__).resolve().parent / "results" / "screenshots"

# Each test's phase reports get stashed here so fixtures can read outcomes
PHASE_REPORT_KEY = pytest.StashKey[dict]()


# Fixtures

@pytest.fixture(scope="session", autouse=True)
def use_data_test_attribute(playwright):
    # The Toolshop ships data-test hooks, not Playwright's data-testid
    # default. One line here and get_by_test_id() works everywhere.
    playwright.selectors.set_test_id_attribute("data-test")


@pytest.fixture(scope="session", autouse=True)
def raise_assertion_timeout():
    # The public demo site slows down under load. 10s of headroom kills
    # the false alarms, and passing assertions return the moment the
    # condition is met, so green runs pay nothing for it.
    expect.set_options(timeout=10_000)


@pytest.fixture(autouse=True)
def log_test_boundaries(request):
    """STARTING and ENDING markers around every test, with the real outcome.

    Doing this here instead of inside each test means no test can forget
    its markers, and the ENDING line still shows up when a test fails,
    which is exactly when the log matters.
    """
    test = request.node
    description = (test.function.__doc__ or "").strip()
    logger.info(f"STARTING {test.name}" + (f": {description}" if description else ""))

    yield

    call_report = test.stash.get(PHASE_REPORT_KEY, {}).get("call")
    if call_report is None:
        outcome = "NO RESULT (setup failed?)"
    else:
        outcome = call_report.outcome.upper()
    logger.info(f"ENDING {test.name}: {outcome}")


@pytest.fixture
def home_page(page) -> HomePage:
    """Home page, already opened with the product grid loaded."""
    return HomePage(page).open()


@pytest.fixture
def login_page(page) -> LoginPage:
    """Sign in page, already opened."""
    return LoginPage(page).open()


@pytest.fixture(scope="session")
def api_context(playwright):
    """One APIRequestContext for the whole run, shared by API tests and setup."""
    context = playwright.request.new_context(base_url=settings.API_BASE_URL)
    yield context
    context.dispose()


@pytest.fixture(scope="session")
def test_user(api_context) -> dict:
    """Register a throwaway user for this run and hand back its details.

    The Toolshop locks ANY account after 3 failed logins (HTTP 423), and
    the seeded demo accounts are shared with the whole internet. Owning
    our own user means nobody else's failed logins can break this suite.
    """
    user = {
        "first_name": "Toolshop",
        "last_name": "Tester",
        "address": {
            "street": "123 Automation Way",
            "city": "Testville",
            "state": "TX",
            "country": "US",
            "postal_code": "75001",
        },
        "phone": "5555555555",
        "dob": "1990-01-01",
        "email": f"test.user.{uuid.uuid4().hex[:10]}@example.com",
        "password": "SuperTester#2026",
    }
    response = UsersApi(api_context).register(user)
    assert response.status == 201, (
        f"Could not register the run's test user: {response.status} {response.text()}"
    )
    return user


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """Pass --start-maximized to Chromium at launch. Only Chromium honors it."""
    return {**browser_type_launch_args, "args": ["--start-maximized"]}


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, browser_name, pytestconfig):
    """
    Maximize headed Chromium, give everything else a fixed 1280x800 viewport.

    Chromium only maximizes if no_viewport stops Playwright from forcing
    its own size onto the context. Firefox and WebKit have no maximize
    equivalent, so they get the fixed size. So do ALL headless runs: with
    no real window to maximize, no_viewport falls back to a small default
    that flips the site into its mobile layout.
    """
    if browser_name == "chromium" and pytestconfig.getoption("--headed"):
        return {**browser_context_args, "no_viewport": True}
    return {**browser_context_args, "viewport": {"width": 1280, "height": 800}}


# Hooks

@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item, call):
    """Screenshot on failure, embedded straight into the HTML report."""
    report = yield

    # Stash every phase report so log_test_boundaries can read the outcome
    item.stash.setdefault(PHASE_REPORT_KEY, {})[report.when] = report

    # Only care about the test body failing, not setup/teardown hiccups
    if report.when != "call" or not report.failed:
        return report

    # API tests never touch a browser, so there is nothing to screenshot
    page = item.funcargs.get("page")
    if page is None:
        return report

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = SCREENSHOT_DIR / f"{item.name}_{timestamp}.png"

    try:
        page.screenshot(path=str(screenshot_path), full_page=True)
    except Exception as exc:
        # A crashed browser should not take the report down with it
        logger.warning(f"Could not capture screenshot for {item.name}: {exc}")
        return report

    logger.info(f"Failure screenshot saved: {screenshot_path}")

    # Base64 so the image lives INSIDE the self-contained report file.
    # A plain file path would break the moment the report gets shared.
    encoded = base64.b64encode(screenshot_path.read_bytes()).decode()
    report.extras = getattr(report, "extras", []) + [html_extras.image(encoded)]

    return report
