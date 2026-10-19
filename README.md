# Android WebView Automation Test Suite

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Appium 2.x](https://img.shields.io/badge/Appium-2.x-purple.svg)](https://appium.io/)
[![UiAutomator2](https://img.shields.io/badge/Driver-UiAutomator2-brightgreen.svg)](https://github.com/appium/appium-uiautomator2-driver)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

Automated end-to-end test suite for Android hybrid applications, built with Python, Appium 2, and Pytest.

The project validates browser detection capabilities inside an Android WebView container using the Page Object Model, dynamic explicit synchronization, and automated screen recording.

---

## Test Scenarios

The suite verifies browser detection parameters inside the embedded WebView:

- **JavaScript Detection**: navigates to the JavaScript status page, verifies that JavaScript execution is active (`Yes`), and navigates back using breadcrumb links.
- **User-Agent Validation**: navigates to the user agent inspection page, extracts the client string, and validates that it conforms to the target Android platform signature.

---

## Quickstart

### 1. Prerequisites
- **Python 3.11+** and **[uv](https://docs.astral.sh/uv/)** package manager
- **Android SDK** with an active emulator (`API 30+`) or physical device connected via `adb`
- **Appium 2.x** with `uiautomator2` driver:
  ```bash
  npm install -g appium
  appium driver install uiautomator2
  ```

### 2. Installation and Dependency Sync
```bash
# Clone the repository and install locked dependencies via uv
cd android-webview-automation
make install
```

### 3. Run Test Suite
```bash
# 1. Start Appium server (in a separate terminal)
make appium
# or: appium --allow-insecure chromedriver_autodownload

# 2. Execute test suite and generate HTML report
make test
```

### 4. View Test Report and Video Recording
```bash
# Opens reports/report.html in your default web browser
make report
```

> [!NOTE]
> A pre-generated demonstration report with recorded video is available at [`reports/report.html`](reports/report.html). It can be opened directly in any browser without booting an emulator.

---

## Architecture and Page Object Model

The codebase uses the Page Object Model to separate page locators, synchronization logic, and test assertions:

```
android-webview-automation/
├── app/
│   └── app-debug.apk          # Application Under Test binary
├── config/
│   ├── capabilities.py        # UiAutomator2Options builder
│   └── settings.py            # Pydantic Settings (env overrides, timeouts)
├── pages/
│   ├── base_page.py           # Context switching, explicit waits, screenshot helpers
│   ├── detect_page.py         # Home page elements & actions
│   ├── js_status_page.py      # JavaScript detection page & breadcrumb navigation
│   └── user_agent_page.py     # User-Agent inspector page
├── tests/
│   ├── conftest.py            # Fixtures: Appium session, screen recording, HTML reporting
│   └── test_webview_browser.py # End-to-end verification scenario
├── reports/
│   ├── report.html            # Standalone offline-viewable test report
│   └── videos/
│       └── test_execution.mp4 # Full MP4 session screen recording
├── Makefile                   # Test execution and linting shortcuts
└── pyproject.toml             # uv, pytest, and ruff configurations
```

### Page Objects Breakdown

1. **`BasePage` (`pages/base_page.py`)**:
   - Manages dynamic polling and context switching between `NATIVE_APP` and `WEBVIEW_*`.
   - Wraps Selenium explicit waits (`WebDriverWait`, `expected_conditions`) for visibility, presence, and clickability.
   - Implements `safe_click()` with automatic recovery against `StaleElementReferenceException`.
   - Zero `time.sleep()` calls across the entire framework.

2. **`DetectSettingsPage` (`pages/detect_page.py`)**:
   - Encapsulates root page locators (`a[href*='/detect/is-javascript-enabled/']`, `a[href*='/detect/what-is-my-user-agent/']`).
   - Ensures all page transitions are performed strictly by clicking DOM elements (no direct `driver.get()` calls).

3. **`JavaScriptStatusPage` (`pages/js_status_page.py`)**:
   - Locates and extracts text from `#detected_value`.
   - Returns boolean evaluation (`status == "Yes"`).
   - Performs clean return navigation via the breadcrumb element (`nav.breadcrumbs a[href='/detect/']`).

4. **`UserAgentPage` (`pages/user_agent_page.py`)**:
   - Locates `#detected_value` and retrieves the active browser User-Agent header.

---

## Configuration and Environment Overrides

All settings are strongly typed using Pydantic Settings (`config/settings.py`) and can be overridden via environment variables or a `.env` file:

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `APPIUM_SERVER_URL` | `http://127.0.0.1:4723` | Appium 2.x HTTP listener endpoint |
| `DEVICE_NAME` | `Android Emulator` | Target emulator or real device name |
| `UDID` | `None` (auto-detect) | Android device UDID (optional) |
| `PLATFORM_VERSION` | `None` (auto-detect) | Target Android OS version (optional) |
| `APP_PATH` | `app/app-debug.apk` | Path to target APK file (alias: `APK_PATH`) |
| `DEFAULT_TIMEOUT` | `60.0` | Explicit wait timeout for DOM elements (sec) |
| `WEBVIEW_TIMEOUT` | `60.0` | Max wait time for WebView context initialization (sec) |
| `PAGE_LOAD_TIMEOUT` | `60.0` | Page load timeout within WebView (sec) |
| `POLL_FREQUENCY` | `0.5` | Polling frequency for explicit waits (sec) |

Example override:
```bash
APPIUM_SERVER_URL="http://hub-cloud.com:4723" DEVICE_NAME="Pixel_9_API_37" make test
```

---

## Screen Recording and HTML Reporting

1. **Native Screen Capture**: During test setup, `driver.start_recording_screen()` begins recording the emulator display at native `1080x2424` resolution (4 Mbps H.264).
2. **Graceful Teardown**: Upon test completion or failure, the MP4 byte stream is decoded and saved to `reports/videos/test_execution.mp4`.
3. **Offline Standalone Report**: `reports/report.html` is generated with:
   - Overall test status (`PASSED` / `FAILED`) badge.
   - Verified parameters table (JavaScript Enabled: Yes, User-Agent string, Duration: 21.5s).
   - Target device & environment specifications table (Android 17, Pixel 9).
   - Embedded HTML5 `<video controls>` player with a direct download button.
   - Failure screenshots (captured automatically if any assertion fails).

---

## Code Quality and Linting

The project follows strict linting, formatting, and typing rules enforced by **Ruff**:

```bash
# Run code formatting check and linter
make lint

# Auto-format codebase
make fmt

# Run all checks (lint + test suite)
make check
```
