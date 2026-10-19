"""Page Object for 'Is JavaScript enabled?' detection page."""

import logging

from selenium.webdriver.common.by import By

from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class JavaScriptStatusPage(BasePage):
    """Encapsulates elements and actions on the JavaScript verification page."""

    PAGE_HEADING = (By.XPATH, "//h1[contains(., 'JavaScript')]")
    DETECTED_VALUE = (By.CSS_SELECTOR, "#detected_value")
    BREADCRUMB_DETECT_LINK = (
        By.CSS_SELECTOR,
        "#breadcrumbs a[href='/detect/'], a[href='/detect/']",
    )

    def wait_for_page_loaded(self, timeout: float | None = None) -> "JavaScriptStatusPage":
        """Wait for the JavaScript verification page to load."""
        logger.info("Waiting for JavaScriptStatusPage to load...")
        self.wait_for_visible(self.PAGE_HEADING, timeout=timeout)
        self.wait_for_presence(self.DETECTED_VALUE, timeout=timeout)
        return self

    def get_javascript_status(self, timeout: float | None = None) -> str:
        """Retrieve the detected JavaScript status (e.g. 'Yes' or 'No')."""
        status_text = self.get_text(self.DETECTED_VALUE, timeout=timeout)
        logger.info("Detected JavaScript status: %s", status_text)
        return status_text

    def is_javascript_enabled(self, timeout: float | None = None) -> bool:
        """Check if JavaScript is detected as enabled ('Yes')."""
        status = self.get_javascript_status(timeout=timeout)
        return status.strip().lower() == "yes"

    def navigate_back_to_detect(self) -> None:
        """Return to the detect settings page via breadcrumb link or browser back."""
        logger.info("Navigating back to DetectSettingsPage via DOM element interaction...")
        try:
            self.safe_click(
                self.BREADCRUMB_DETECT_LINK,
                timeout=10.0,
                expected_url_part="/detect/",
            )
        except Exception as exc:
            logger.warning(
                "Breadcrumb element click failed (%s), falling back to driver.back()",
                exc,
            )
            self.driver.back()
