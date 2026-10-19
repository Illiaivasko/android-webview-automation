"""Page Object for 'What is my user agent?' detection page."""

import logging

from selenium.webdriver.common.by import By

from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class UserAgentPage(BasePage):
    """Encapsulates elements and actions on the User-Agent verification page."""

    PAGE_HEADING = (
        By.XPATH,
        "//h1[contains(., 'User Agent') or contains(., 'user agent')]",
    )
    DETECTED_VALUE = (By.CSS_SELECTOR, "#detected_value")
    BREADCRUMB_DETECT_LINK = (
        By.CSS_SELECTOR,
        "#breadcrumbs a[href='/detect/'], a[href='/detect/']",
    )

    def wait_for_page_loaded(self, timeout: float | None = None) -> "UserAgentPage":
        """Wait for the User-Agent verification page to load."""
        logger.info("Waiting for UserAgentPage to load...")
        self.wait_for_visible(self.PAGE_HEADING, timeout=timeout)
        self.wait_for_presence(self.DETECTED_VALUE, timeout=timeout)
        return self

    def get_user_agent(self, timeout: float | None = None) -> str:
        """Retrieve the detected User-Agent header string."""
        ua_string = self.get_text(self.DETECTED_VALUE, timeout=timeout)
        logger.info("Detected User-Agent: %s", ua_string)
        return ua_string

    def navigate_back_to_detect(self) -> None:
        """Return to the detect settings page via breadcrumb link or browser back."""
        logger.info("Navigating back to DetectSettingsPage via DOM element interaction...")
        try:
            self.safe_click(self.BREADCRUMB_DETECT_LINK, timeout=5.0)
        except Exception as exc:
            logger.warning(
                "Breadcrumb element click failed (%s), falling back to driver.back()",
                exc,
            )
            self.driver.back()
