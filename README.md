# Mason Garza: Playwright + Pytest Test Automation Framework

## Overview:
This project is a UI and API test automation framework built with Python, Pytest, and Playwright. It targets [Practice Software Testing](https://practicesoftwaretesting.com), a modern Angular e-commerce application ("Toolshop") built specifically for test automation practice, along with its documented [REST API](https://api.practicesoftwaretesting.com/api/documentation).

What this framework demonstrates:
- **Page Object Model (POM)** with a shared `BasePage` every page inherits from, plus a `NavBar` component object that pages compose. Inheritance for "is a page", composition for "has a navbar".
- **Same abstraction applied to API testing**: one client class per API area (`AuthApi`, `ProductsApi`) built on a `BaseClient` that wraps Playwright's `APIRequestContext` with logging and bearer auth.
- **Tiered locator strategy**: semantic locators (`get_by_role`, `get_by_placeholder`) first, `data-test` id hooks where accessible names change at runtime, and CSS/XPath only where they are genuinely the right tool.
- **Cross-browser execution** on Chromium, Firefox, and WebKit with a single flag.
- **Custom run-scoped file logging**
- **Self-contained HTML report**
- **Screenshot-on-Failure**: full-page screenshots embedded directly into the report on failure.
- **Zero hard sleeps**: All waiting is done with web-first assertions and response waits, so the suite is as fast as the site allows and no faster.

The suite currently runs 20 tests (11 UI, 9 API) green across all three browser engines.

## Getting Started:
1. Clone the repository:
```bash
git clone https://github.com/MasonGarza7/playwright_pytest_pom.git
cd playwright_pytest_pom
```
2. Download and install Python 3.11+ from the [official website](https://www.python.org/downloads/) (developed on 3.11.9)
3. Reproduce the environment:
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m playwright install
```

## Running Tests:
Run all tests (headless Chromium by default):
```bash
pytest
```

Run a single test script:
```bash
pytest tests/ui/test_login.py
```

Run a single test within a script:
```bash
pytest "tests/ui/test_login.py::TestLogin::test_valid_login"
```

Run by marker (markers are defined in `pytest.ini`):
```bash
pytest -m smoke
pytest -m ui
pytest -m api
```

Useful flags, combinable with everything above:
```bash
# verbose: list every test and its result
pytest -v     

# Opens observable browser(s)
pytest --headed  

# pause 1000ms (1 second) after each Playwright action                                              
pytest --headed --slowmo 1000                                  

# swap the browser
pytest --browser firefox  

# all three browsers in one run
pytest --browser chromium --browser firefox --browser webkit  

# point the UI suite at another environment
pytest --base-url https://other-env.com                        
```

Flag and marker notes:
- `--headed` opens real browser windows instead of running headlessly. Chromium opens maximized (see **Reasonings**), Firefox and WebKit run at a fixed 1280x800 because they have no maximize support.
- `--slowmo <ms>` slows every Playwright operation down. Combined with `--headed`, it is the easiest way to actually watch what a test does.
- `--browser <name>` can be passed multiple times and each UI test will run once per engine. API tests are browser-independent and always run exactly once.
- `-m <marker>` filters by suite: `smoke` is the fast "is everything alive" check, `ui` is everything browser-driven, `api` is request-level only.

## Project Structure:
```bash
playwright_pytest_pom/
├── .venv/                    # Local Python virtual environment (not committed)
├── api/                      # API client classes, the request-side twin of pages/
│   ├── auth_api.py           # Client for the auth endpoints (login, /users/me)
│   ├── base_client.py        # Base class wrapping APIRequestContext with logging and bearer auth
│   ├── products_api.py       # Client for the product catalog endpoints
│   └── users_api.py          # Client for the user account endpoints (registration)
├── config/
│   └── settings.py           # API base URL, overridable via env vars
├── pages/                    # Page objects, one class per page
│   ├── components/
│   │   └── nav_bar.py        # Navbar component object, composed into every page via BasePage
│   ├── account_page.py       # My account landing page
│   ├── base_page.py          # Base class: Page handle, logger, navbar, and open() navigation
│   ├── home_page.py          # Product grid plus the search/sort/filter sidebar
│   ├── login_page.py         # Sign in form
│   └── product_page.py       # Product detail page with add-to-cart
├── results/                  # All run output lands here (auto-generated, not committed)
│   ├── logs/                 # One timestamped log file per test run
│   ├── screenshots/          # Full-page screenshots captured on UI test failures
│   └── report.html           # Self-contained pytest-html report (regenerated every run)
├── tests/
│   ├── api/                  # Request-level tests, no browser involved
│   │   ├── conftest.py       # API fixtures: APIRequestContext, client objects, auth token
│   │   ├── test_auth.py      # Token issuing and token gating
│   │   └── test_products.py  # Catalog contract, pagination, search, 404 behavior
│   └── ui/                   # Browser-driven tests
│       ├── test_login.py     # Valid login, invalid credentials error, sign out
│       ├── test_products.py  # Price sorting, category filter, detail page, add to cart
│       ├── test_search.py    # Matching results, no-results message, search reset
│       └── test_smoke.py     # Fast check that the framework plumbing works end to end
├── utils/
│   └── logger.py             # Run-scoped file logger shared by pages, clients, and hooks
├── conftest.py               # Global fixtures and hooks: browser windowing, page object fixtures,
│                             # per-run test user registration, screenshot-on-failure
├── pytest.ini                # Pytest config: discovery, markers, base URL, reporting, live logging
└── requirements.txt          # Frozen dependencies for reproducing the environment
```

## Logging:
Every test run gets ONE timestamped log file at `results/logs/test_run_TIMESTAMP.log`. Any module in the project grabs a named logger with `get_logger(name)` from `utils/logger.py`.

- Every test is automatically wrapped in STARTING and ENDING markers by an autouse fixture in `conftest.py`. The ENDING line includes the real outcome (PASSED/FAILED/SKIPPED) pulled from pytest's own test report, and if a test has a docstring, its text is included in the STARTING line as the test's description. This lives in one fixture instead of two hand-written lines per test, so no test can forget its markers and the ENDING line still appears when a test fails, which is exactly when the log matters.
- Between those markers, page objects log every action they take (opening pages, searching, sorting, adding to cart) and API clients log every request with its status code, so a failed run's log reads like a story of what happened.
- The same log lines also stream to the console live during the run. That console output is handled by pytest live logging (`log_cli` in `pytest.ini`) rather than a second handler on the logger, which prevents double-printing and keeps pytest's `caplog` assertions working.
- The default level is INFO. Override it per run without touching code:
```bash
$env:LOG_LEVEL="DEBUG"; pytest
```

This logger started from a template I had used in previous projects and was upgraded along the way:
- One shared file handler instead of a new `FileHandler` per named logger. The old approach worked, but it silently left a pile of open file handles all pointed at the same file.
- The log level was hardcoded before. It now reads `LOG_LEVEL` from the environment.
- The old logger was file-only with no console output. Console logging is now handled by pytest itself, as described above.

## Reporting:
- Every run regenerates `results/report.html` (wired up through `addopts` in `pytest.ini`, so plain `pytest` always produces it).
- The report is **self-contained**: styles, results, captured log output, and failure screenshots all live inside the single HTML file. It can be attached to a ticket or emailed and it still works, no folder of assets required.
- Drag and drop it into any browser to view it. Each failure shows the assertion error, the log lines from that test, and the embedded screenshot.
- Note the difference in output behavior: a NEW log file is created for every run, while the report is OVERWRITTEN every run. The HTML report is the polished artifact of the latest run; the logs folder is the history.

## Screenshot on Failure:
- A `pytest_runtest_makereport` hook wrapper in `conftest.py` inspects every test result as it is produced.
- When a UI test's body fails, the hook grabs that test's `page` fixture, captures a **full-page** screenshot (not just the visible viewport), and saves it with a timestamped name to `results/screenshots/`.
- The image is then base64-encoded and attached to that test's entry in the HTML report, so the report shows exactly what the page looked like at the moment of failure.
- API tests are skipped automatically, they have no `page` fixture and nothing to screenshot. A crashed browser is also handled: if the screenshot itself fails, the run logs a warning instead of dying inside the reporting hook.

## Reasonings:
- **Why semantic locators first**: Playwright's own docs recommend role/label/placeholder locators because they track what a user actually perceives, and they double as a quiet accessibility audit. If `get_by_role("link", name="Sign in")` stops working, either the UI changed or its accessibility regressed. Both are worth knowing.

- **Why `get_by_test_id()` is retargeted to `data-test`**: The Toolshop ships `data-test` hooks on nearly everything, but Playwright's default test-id attribute is `data-testid`. One line in `conftest.py` (`playwright.selectors.set_test_id_attribute("data-test")`) makes `get_by_test_id("login-error")` work everywhere, which reads far better than raw CSS attribute strings scattered through the page objects.

- **Why test-id locators are used at all when semantic locators are preferred**: Some elements have accessible names that change at runtime. The navbar user menu shows whoever is logged in, and the cart badge shows a count. Locating those by name would make the locator depend on test data. The `data-test` hook is the stable identity in those cases.

- **Why there is exactly one XPath in the project**: In `home_page.py`, `open_product()` knows the `h5` holding the product name but needs to click the card link WRAPPING it. Climbing from a known child to its ancestor is the one job CSS cannot do and XPath exists for. Everywhere else, semantic or test-id locators win.

- **Why there are no `sleep()` calls anywhere**: Hard waits are either too long (slow suite) or too short (flaky suite), and usually both on different days. Waiting is done with web-first assertions like `expect(...).to_be_visible()` that retry until a timeout, and with `expect_response()` wrapped around actions like sorting that trigger API refetches. The sort and filter helpers go one step further: they return the API response they triggered, and the test asserts the grid against that response's data with a retrying `expect`. That closes the gap between the response arriving and Angular repainting the grid (a race that surfaced as a real flake during development), and it doubles as a check that the UI renders exactly what the API returned.

- **Why the global assertion timeout is 10 seconds**: The demo site is public and slows down under load. A WebKit run once failed purely because the account page took longer than the default 5 seconds to render, then passed in 5 seconds on rerun, which is the signature of a flake rather than a bug. Passing assertions return the instant their condition is met, so the test moves on instantly. Only genuine failures wait the full 10 seconds.

- **Why headed Chromium opens maximized but headless runs use a fixed 1280x800 viewport**: Chromium accepts `--start-maximized` at launch, but only takes effect when `no_viewport` stops Playwright from forcing its own context size. Firefox and WebKit have no maximize equivalent, so they get the fixed viewport. Headless runs get the fixed viewport too, because with no real window to maximize, `no_viewport` falls back to a small default that flips the site into its responsive mobile layout and changes what is on screen.

- **Why the UI base URL is in `pytest.ini` but the API base URL is in `config/settings.py`**: They have different consumers. The `base_url` ini value is read by pytest-playwright and baked into every browser context, which is what lets tests call `page.goto("/")` and be overridden at runtime with `--base-url`. The `APIRequestContext` for API tests is created manually in a fixture, so nothing reads the ini value for it; it takes its base URL from `settings.py` instead. 

- **Why the API token fixture is function-scoped instead of session-scoped**: The API issues tokens that expire in 300 seconds. A session-scoped token would be marginally faster today and would start producing unexplainable 401s the day the suite grows past five minutes. Requesting a fresh token per test trades a few milliseconds for scalability. 

- **Why the suite registers its own user per run instead of using the seeded demo account**: The suite originally logged in as the site's public `customer@` demo account, until a run started failing with HTTP 423 Locked. Investigating showed the Toolshop locks ANY account after 3 failed login attempts, and the demo account is shared with everyone on the internet practicing against this site. The fix is self-sufficiency: a session fixture registers a unique throwaway user through the API at the start of every run, and all login tests use it. As a second layer, the invalid-credentials tests (UI and API) deliberately use a nonexistent email, which returns the same 401 contract but can never lock a real account. A single cross-browser run of a wrong-password test against a real account would hit the lockout threshold by itself.

- **Why tests create their data through the API, not the UI**: Registering the test user happens with one `POST /users/register` call in a fixture instead of driving the registration form. Setup through the API is faster and less fragile, and it keeps each UI test focused on the one behavior it exists to verify. The UI registration form is a feature to test in its own right, separately from every login test using it as a prerequisite.

- **Why the test folders contain `__init__.py` files**: `tests/ui/` and `tests/api/` both have a `test_products.py`. Without `__init__.py` files, pytest imports both as the same bare module name `test_products` and refuses to collect. Making the test directories packages gives each file a unique dotted path (`tests.ui.test_products`).

- **Why failure screenshots are embedded in the report instead of linked**: A report that references image files by path breaks the moment it is shared without the folder next to it. Base64-embedding trades a larger file size for a single-file artifact that can be attached to a bug ticket as-is. A traditional linking approach could be implemented if file size became an issue. But at that point, the real issue is how many tests are failing. 

## Roadmap:
- [x] Framework architecture, logging, HTML report, screenshot on failure
- [x] Page objects and UI suites (login, search, sort, filter, product detail, cart)
- [x] API suite (auth tokens, catalog contract, negative cases)
- [x] GitHub Actions CI: API suite runs on every push (the public site's Cloudflare bot protection challenges datacenter IPs, so the UI suite stays local until the app is self-hosted in the pipeline)
- [ ] Publish the HTML report as a CI build artifact
- [ ] Docker: self-host the Toolshop inside the pipeline and bring the UI suite into CI
