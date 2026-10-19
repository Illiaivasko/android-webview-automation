"""Runtime settings and environment configuration using Pydantic Settings."""

from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppiumSettings(BaseSettings):
    """Appium server and test configuration parameters."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    appium_server_url: str = "http://127.0.0.1:4723"

    platform_name: str = "Android"
    automation_name: str = "UiAutomator2"
    device_name: str = "Pixel 9 (emulator-5554)"
    udid: str | None = "emulator-5554"
    platform_version: str | None = "17"

    app_package: str = "com.trident.webviewgen.demo"
    app_activity: str = "com.trident.webviewgen.demo.MainActivity"
    app_path: str = Field(
        default=str(Path(__file__).parent.parent / "app" / "app-debug.apk"),
        validation_alias=AliasChoices("app_path", "apk_path"),
    )

    default_timeout: float = 60.0
    webview_timeout: float = 60.0
    page_load_timeout: float = 60.0
    poll_frequency: float = 0.5

    reports_dir: Path = Path(__file__).parent.parent / "reports"
    videos_dir: Path = Path(__file__).parent.parent / "reports" / "videos"
    screenshots_dir: Path = Path(__file__).parent.parent / "reports" / "screenshots"


settings = AppiumSettings()
