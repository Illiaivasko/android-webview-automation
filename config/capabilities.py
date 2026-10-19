"""Appium UiAutomator2 capability options builder."""

from appium.options.android import UiAutomator2Options

from config.settings import settings


def get_driver_options() -> UiAutomator2Options:
    """Build and return UiAutomator2Options configured for Android WebView testing."""
    options = UiAutomator2Options()

    options.platform_name = settings.platform_name
    options.automation_name = settings.automation_name
    options.device_name = settings.device_name

    if settings.udid:
        options.udid = settings.udid
    if settings.platform_version:
        options.platform_version = settings.platform_version

    options.app = settings.app_path
    options.app_package = settings.app_package
    options.app_activity = settings.app_activity

    options.auto_grant_permissions = True
    options.no_reset = False

    options.set_capability("appium:chromedriverAutodownload", True)
    options.set_capability("appium:ensureWebviewsHavePages", True)
    options.set_capability("appium:enableWebviewDetailsCollection", True)
    options.set_capability("appium:nativeWebScreenshot", True)

    return options
