"""End-to-end test suite for Android WebView browser settings detection."""

import logging
from typing import Any

from appium import webdriver
from pages.detect_page import DetectSettingsPage
from pages.js_status_page import JavaScriptStatusPage
from pages.user_agent_page import UserAgentPage

logger = logging.getLogger(__name__)


def test_detect_webview_browser_settings(
    driver: webdriver.Remote,
    execution_results: dict[str, Any],
) -> None:
    """Verify Android WebView displays JavaScript enabled and extracts User-Agent string.

    Test Lifecycle:
    1. Wait for Android app to load WhatIsMyBrowser.com and switch to WEBVIEW context.
    2. Click 'Is JavaScript enabled?' via live DOM interaction.
    3. Assert detected JavaScript status is 'Yes'.
    4. Navigate back to Detect Settings home via breadcrumb DOM link.
    5. Click 'What is my user agent?' via live DOM interaction.
    6. Extract and assert non-empty User-Agent string.
    """
    logger.info("Step 1: Initialize POM and switch to WebView context")
    detect_page = DetectSettingsPage(driver)
    active_context = detect_page.switch_to_webview()
    assert "WEBVIEW" in active_context, (
        f"Expected to be in a WEBVIEW context, but got: {active_context}"
    )

    detect_page.wait_for_page_loaded()
    logger.info("DetectSettingsPage loaded successfully in context: %s", active_context)

    logger.info("Step 2: Navigate to JavaScript detection page via DOM element")
    detect_page.click_javascript_check()

    js_page = JavaScriptStatusPage(driver).wait_for_page_loaded()
    js_status = js_page.get_javascript_status()
    execution_results["js_status"] = js_status
    logger.info("Extracted JavaScript status: %s", js_status)

    assert js_page.is_javascript_enabled(), (
        f"Expected JavaScript to be enabled ('Yes'), but detected: '{js_status}'"
    )

    logger.info("Step 3: Navigate back to Detect Settings home page")
    js_page.navigate_back_to_detect()
    detect_page.wait_for_page_loaded()

    logger.info("Step 4: Navigate to User-Agent page via DOM element")
    detect_page.click_user_agent_check()

    ua_page = UserAgentPage(driver).wait_for_page_loaded()
    ua_string = ua_page.get_user_agent()
    execution_results["user_agent"] = ua_string
    logger.info("Extracted User-Agent header: %s", ua_string)

    assert ua_string and len(ua_string.strip()) > 0, "Detected User-Agent string is empty!"
    assert any(
        token in ua_string for token in ("Mozilla", "AppleWebKit", "Chrome", "Android", "Mobile")
    ), f"Extracted User-Agent does not appear to be a valid browser UA: '{ua_string}'"

    logger.info("Step 5: Test completed successfully")
