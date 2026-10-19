"""Pytest configuration, fixtures, and standalone HTML/video reporting."""

import base64
import logging
import time
from collections.abc import Generator
from typing import Any

import pytest
from appium import webdriver
from config.capabilities import get_driver_options
from config.settings import settings
from reports.html_reporter import generate_standalone_html_report

logger = logging.getLogger(__name__)
_EXECUTION_RESULTS: dict[str, Any] = {
    "status": "Unknown",
    "js_status": "Not executed",
    "user_agent": "Not executed",
    "duration_seconds": 0.0,
    "error_message": None,
    "screenshot_path": None,
    "video_path": "videos/test_execution.mp4",
    "device_info": {
        "platform_name": settings.platform_name,
        "platform_version": settings.platform_version,
        "device_name": settings.device_name,
        "automation_name": settings.automation_name,
        "app_package": settings.app_package,
        "app_activity": settings.app_activity,
        "appium_url": settings.appium_server_url,
    },
}


@pytest.fixture(scope="session")
def execution_results() -> dict[str, Any]:
    """Provide session-wide access to test results dictionary for reports."""
    return _EXECUTION_RESULTS


@pytest.fixture(scope="function")
def driver(
    request: pytest.FixtureRequest,
    execution_results: dict[str, Any],
) -> Generator[webdriver.Remote, None, None]:
    """Initialize Appium session, record screen, and manage teardown."""
    logger.info("Initializing Appium driver session at %s", settings.appium_server_url)
    options = get_driver_options()
    driver_instance = webdriver.Remote(
        command_executor=settings.appium_server_url,
        options=options,
    )

    try:
        driver_instance.start_recording_screen(
            video_size="1080x2424",
            time_limit=180,
            bit_rate=4000000,
        )
        logger.info("Appium screen recording successfully started")
    except Exception as exc:
        logger.warning("Screen recording could not be initialized: %s", exc)

    start_time = time.time()
    try:
        yield driver_instance
    finally:
        elapsed = time.time() - start_time
        execution_results["duration_seconds"] = round(elapsed, 2)

        try:
            video_b64 = driver_instance.stop_recording_screen()
            if video_b64:
                settings.videos_dir.mkdir(parents=True, exist_ok=True)
                target_video_file = settings.videos_dir / "test_execution.mp4"
                target_video_file.write_bytes(base64.b64decode(video_b64))
                logger.info(
                    "Saved screen recording to %s (%d bytes)",
                    target_video_file,
                    target_video_file.stat().st_size,
                )
                execution_results["video_path"] = "videos/test_execution.mp4"
        except Exception as exc:
            logger.warning("Could not capture or save screen recording: %s", exc)

        failed = getattr(request.node, "rep_call", None) and request.node.rep_call.failed
        if failed:
            try:
                settings.screenshots_dir.mkdir(parents=True, exist_ok=True)
                scr_file = settings.screenshots_dir / f"failure_{int(time.time())}.png"
                driver_instance.save_screenshot(str(scr_file))
                logger.info("Failure screenshot captured: %s", scr_file)
                execution_results["screenshot_path"] = f"screenshots/{scr_file.name}"
            except Exception as exc:
                logger.warning("Failed to capture error screenshot: %s", exc)

        try:
            driver_instance.quit()
            logger.info("Appium driver session closed cleanly")
        except Exception as exc:
            logger.debug("Exception during driver quit: %s", exc)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[None]):
    """Store test call outcome on node and inject video / screenshot into pytest-html."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)

    if rep.when == "call":
        _EXECUTION_RESULTS["status"] = "PASSED" if rep.passed else "FAILED"
        if rep.failed and rep.longreprtext:
            _EXECUTION_RESULTS["error_message"] = rep.longreprtext

        pytest_html = item.config.pluginmanager.getplugin("html")
        if pytest_html is not None:
            extra = getattr(rep, "extra", [])
            video_rel_path = _EXECUTION_RESULTS.get("video_path", "videos/test_execution.mp4")
            html_content = (
                '<div style="margin: 12px 0; font-family: -apple-system, sans-serif;">\n'
                f'    <a href="{video_rel_path}" target="_blank" style="color: #2563eb; '
                'font-weight: 600; text-decoration: none;">\n'
                "        View Screen Recording (MP4)\n"
                "    </a>\n"
                "</div>"
            )
            extra.append(pytest_html.extras.html(html_content))
            rep.extra = extra


def pytest_html_report_title(report: Any) -> None:
    """Set custom title for pytest-html report."""
    report.title = "Android WebView Automation — Test Execution Report"


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Generate standalone developer-grade HTML report at reports/report.html."""
    output_report_file = settings.reports_dir / "report.html"
    generate_standalone_html_report(_EXECUTION_RESULTS, output_report_file)
