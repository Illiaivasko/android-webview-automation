"""Page Object Model (POM) package for Android WebView automation."""

from pages.base_page import BasePage
from pages.detect_page import DetectSettingsPage
from pages.js_status_page import JavaScriptStatusPage
from pages.user_agent_page import UserAgentPage

__all__ = [
    "BasePage",
    "DetectSettingsPage",
    "JavaScriptStatusPage",
    "UserAgentPage",
]
