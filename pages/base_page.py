"""Base Page Object providing explicit wait wrappers and context switching."""

import logging
from pathlib import Path

from appium import webdriver
from config.settings import settings
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger(__name__)


class BasePage:
    """Foundational Page Object encapsulating driver interactions and WebView contexts."""

    def __init__(self, driver: webdriver.Remote):
        self.driver = driver
        self.default_timeout = settings.default_timeout
        self.poll_frequency = settings.poll_frequency

    def wait_for_webview_context(self, timeout: float | None = None) -> str:
        """Poll driver contexts until a WEBVIEW context is initialized."""
        effective_timeout = timeout or settings.webview_timeout

        def _find_webview(d) -> str | bool:
            available_contexts = d.contexts
            logger.debug("Available contexts: %s", available_contexts)
            for ctx in available_contexts:
                if "WEBVIEW" in ctx:
                    return ctx
            return False

        try:
            webview_context = WebDriverWait(
                self.driver,
                effective_timeout,
                poll_frequency=self.poll_frequency,
            ).until(_find_webview)
            logger.info("Found WebView context: %s", webview_context)
            return str(webview_context)
        except TimeoutException as exc:
            available = self.driver.contexts
            msg = (
                f"Timed out waiting {effective_timeout}s for WEBVIEW context. "
                f"Available: {available}"
            )
            raise TimeoutException(msg) from exc

    def switch_to_webview(self, timeout: float | None = None) -> str:
        """Switch driver to the active WebView context."""
        webview_ctx = self.wait_for_webview_context(timeout=timeout)
        self.driver.switch_to.context(webview_ctx)
        logger.info("Switched to WebView context: %s", webview_ctx)
        try:
            self.driver.execute_cdp_cmd("Network.enable", {})
            self.driver.execute_cdp_cmd(
                "Network.setBlockedURLs",
                {
                    "urls": [
                        "*googleads*",
                        "*googlesyndication*",
                        "*doubleclick*",
                        "*adservice.google*",
                    ]
                },
            )
            logger.info("Configured CDP URL blocking for ad services")
        except Exception as exc:
            logger.debug("CDP URL blocking not applicable: %s", exc)

        return webview_ctx

    def switch_to_native(self) -> None:
        """Switch driver back to NATIVE_APP context."""
        self.driver.switch_to.context("NATIVE_APP")
        logger.info("Switched to NATIVE_APP context")

    @property
    def current_context(self) -> str:
        """Return the current driver context."""
        return self.driver.current_context

    def wait_for_visible(
        self,
        locator: tuple[str, str],
        timeout: float | None = None,
    ) -> WebElement:
        """Explicitly wait until an element is visible in the DOM."""
        t = timeout or self.default_timeout
        return WebDriverWait(self.driver, t, poll_frequency=self.poll_frequency).until(
            ec.visibility_of_element_located(locator)
        )

    def wait_for_presence(
        self,
        locator: tuple[str, str],
        timeout: float | None = None,
    ) -> WebElement:
        """Explicitly wait until an element is present in the DOM."""
        t = timeout or self.default_timeout
        return WebDriverWait(self.driver, t, poll_frequency=self.poll_frequency).until(
            ec.presence_of_element_located(locator)
        )

    def wait_for_clickable(
        self,
        locator: tuple[str, str],
        timeout: float | None = None,
    ) -> WebElement:
        """Explicitly wait until an element is clickable."""
        t = timeout or self.default_timeout
        return WebDriverWait(self.driver, t, poll_frequency=self.poll_frequency).until(
            ec.element_to_be_clickable(locator)
        )

    def dismiss_google_vignette_if_present(self) -> None:
        """Dismiss Google Vignette interstitial ad if intercepted."""
        try:
            curr = self.driver.current_url
            if "#google_vignette" not in curr:
                return
            logger.info("Handling Google Vignette interstitial ad at %s...", curr)
            for iframe in self.driver.find_elements(
                By.CSS_SELECTOR, "iframe[id^='aswift'], iframe[name^='aswift']"
            ):
                try:
                    self.driver.switch_to.frame(iframe)
                    dismiss_btns = self.driver.find_elements(
                        By.CSS_SELECTOR, "#dismiss-button, div[aria-label='Close ad']"
                    )
                    if not dismiss_btns:
                        nested = self.driver.find_elements(By.CSS_SELECTOR, "iframe#ad_iframe")
                        if nested:
                            self.driver.switch_to.frame(nested[0])
                            dismiss_btns = self.driver.find_elements(
                                By.CSS_SELECTOR, "#dismiss-button, div[aria-label='Close ad']"
                            )
                    if dismiss_btns:
                        dismiss_btns[0].click()
                        logger.info("Dismissed Google Vignette via button click")
                        self.driver.switch_to.default_content()
                        return
                    self.driver.switch_to.default_content()
                except Exception:
                    self.driver.switch_to.default_content()
        except Exception as exc:
            logger.debug("Exception while attempting to dismiss vignette: %s", exc)

    def safe_click(
        self,
        locator: tuple[str, str],
        timeout: float | None = None,
        expected_url_part: str | None = None,
    ) -> None:
        """Wait for element to be clickable, click it, and verify navigation."""
        scroll_js = "arguments[0].scrollIntoView({block: 'center', inline: 'center'});"
        element = self.wait_for_clickable(locator, timeout=timeout)
        href = element.get_attribute("href")
        try:
            self.driver.execute_script(scroll_js, element)
            element.click()
            logger.info("Clicked element with locator %s", locator)
        except (StaleElementReferenceException, ElementClickInterceptedException):
            logger.warning("Click intercepted or element stale, retrying: %s", locator)
            refreshed = self.wait_for_clickable(locator, timeout=timeout)
            try:
                self.driver.execute_script(scroll_js, refreshed)
                refreshed.click()
            except Exception:
                logger.info("Standard click failed, attempting JS click on %s", locator)
                self.driver.execute_script("arguments[0].click();", refreshed)
        except Exception as exc:
            logger.info("Standard click threw %s, attempting JS click on %s", exc, locator)
            self.driver.execute_script("arguments[0].click();", element)

        if expected_url_part:
            try:
                WebDriverWait(self.driver, 5, poll_frequency=0.2).until(
                    lambda d: expected_url_part in d.current_url
                )
            except TimeoutException:
                curr = self.driver.current_url
                if "#google_vignette" in curr and href:
                    logger.info("Vignette ad detected (%s), navigating directly to %s", curr, href)
                    self.driver.get(href)

    def get_text(
        self,
        locator: tuple[str, str],
        timeout: float | None = None,
    ) -> str:
        """Wait for element to be visible and return its trimmed text."""
        element = self.wait_for_visible(locator, timeout=timeout)
        text = element.text.strip()
        logger.info("Retrieved text from %s: '%s'", locator, text)
        return text

    def take_screenshot(self, name: str) -> Path:
        """Capture screenshot and save to reports directory."""
        settings.screenshots_dir.mkdir(parents=True, exist_ok=True)
        file_path = settings.screenshots_dir / f"{name}.png"
        self.driver.save_screenshot(str(file_path))
        logger.info("Screenshot saved: %s", file_path)
        return file_path
