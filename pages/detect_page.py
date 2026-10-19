"""Page Object for WhatIsMyBrowser Detect Settings home page."""

import logging

from selenium.webdriver.common.by import By

from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class DetectSettingsPage(BasePage):
    """Encapsulates the root Detect Settings page elements and navigation actions."""

    MAIN_HEADING = (
        By.XPATH,
        "//h1[contains(., 'Detect') and contains(., 'Web Browser Settings')]",
    )
    JS_CHECK_LINK = (By.CSS_SELECTOR, "a[href*='/detect/is-javascript-enabled/']")
    USER_AGENT_LINK = (By.CSS_SELECTOR, "a[href*='/detect/what-is-my-user-agent/']")

    def wait_for_page_loaded(self, timeout: float | None = None) -> "DetectSettingsPage":
        """Wait for the Detect Settings home page DOM and heading to be visible."""
        logger.info("Waiting for DetectSettingsPage to load...")
        self.wait_for_visible(self.MAIN_HEADING, timeout=timeout)
        self.wait_for_presence(self.JS_CHECK_LINK, timeout=timeout)
        return self

    def click_javascript_check(self) -> None:
        """Click on 'Is JavaScript enabled?' link using live WebView element interaction."""
        logger.info("Clicking 'Is JavaScript enabled?' link...")
        self.safe_click(self.JS_CHECK_LINK, expected_url_part="is-javascript-enabled")

    def click_user_agent_check(self) -> None:
        """Click on 'What is my user agent?' link using live WebView element interaction."""
        logger.info("Clicking 'What is my user agent?' link...")
        self.safe_click(self.USER_AGENT_LINK, expected_url_part="what-is-my-user-agent")
