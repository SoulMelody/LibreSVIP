"""Update checking and update-action orchestration for the mobile frontend."""

from __future__ import annotations

import json
import platform
from typing import TYPE_CHECKING, Any

import flet as ft
import flet_notifications as ftn
import httpx
from loguru import logger
from packaging.version import InvalidVersion, Version

import libresvip
from libresvip.utils.release_asset import android_abi, match_android_apk_asset
from libresvip.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    from libresvip.mobile.notifier import MobileNotifier

LATEST_RELEASE_URL = "https://api.github.com/repos/SoulMelody/LibreSVIP/releases/latest"
ACTION_DOWNLOAD_APK = "download_apk"
ACTION_OPEN_RELEASE = "open_release"
DOWNLOAD_TIMEOUT = 300


def is_newer_release(tag_name: str, current_version: str) -> bool:
    try:
        return Version(tag_name.removeprefix("v")) > Version(current_version)
    except InvalidVersion:
        logger.warning("Ignoring release with an invalid version tag: {}", tag_name)
        return False


async def fetch_latest_release() -> dict[str, Any] | None:
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            response = await client.get(
                LATEST_RELEASE_URL,
                headers={"Accept": "application/vnd.github+json"},
            )
            response.raise_for_status()
            release = response.json()
    except (httpx.HTTPError, ValueError):
        logger.exception("Unable to fetch the latest LibreSVIP release")
        return None
    return release if isinstance(release, dict) else None


def _release_assets(release: dict[str, Any]) -> list[dict[str, Any]]:
    assets = release.get("assets")
    if not isinstance(assets, list):
        return []
    return [asset for asset in assets if isinstance(asset, dict) and "name" in asset]


class UpdateChecker:
    """Checks GitHub for a newer release and routes the notification actions."""

    def __init__(self, page: ft.Page, notifier: MobileNotifier, launcher: ft.UrlLauncher) -> None:
        self.page = page
        self.notifier = notifier
        self.launcher = launcher
        self.is_android = page.platform == ft.PagePlatform.ANDROID
        self.notifier.action_handler = self.on_action
        self.notifier.tap_handler = self.on_tap

    async def check(self) -> None:
        release = await fetch_latest_release()
        if release is None:
            return
        tag_name = str(release.get("tag_name", ""))
        if not is_newer_release(tag_name, libresvip.__version__):
            return
        version = tag_name.removeprefix("v")
        release_url = str(release.get("html_url", ""))
        apk_asset = self._match_apk(release)
        actions = (
            [
                ftn.NotificationAction(id=ACTION_DOWNLOAD_APK, title=_("Download")),
                ftn.NotificationAction(id=ACTION_OPEN_RELEASE, title=_("Open release page")),
            ]
            if apk_asset is not None
            else [ftn.NotificationAction(id=ACTION_OPEN_RELEASE, title=_("Open release page"))]
        )
        payload = json.dumps(
            {
                "release_url": release_url,
                "apk_url": str(apk_asset.get("browser_download_url", "")) if apk_asset else "",
                "apk_name": str(apk_asset.get("name", "")) if apk_asset else "",
            }
        )
        await self.notifier.notify(
            _("New version available"),
            _("LibreSVIP {} is available.").format(version),
            actions=actions,
            payload=payload,
        )

    def _match_apk(self, release: dict[str, Any]) -> dict[str, Any] | None:
        if not self.is_android:
            return None
        from libresvip.mobile import android

        abi = android_abi(android.current_abi() or platform.machine())
        if abi is None:
            return None
        return match_android_apk_asset(_release_assets(release), abi)

    def on_action(self, event: ftn.NotificationActionEvent) -> None:
        self.page.run_task(self._handle, event.action_id, event.payload)

    def on_tap(self, event: ftn.NotificationEvent) -> None:
        self.page.run_task(self._handle, ACTION_OPEN_RELEASE, event.payload)

    async def _handle(self, action_id: str, payload: str | None) -> None:
        data = self._parse_payload(payload)
        if data is None:
            return
        if action_id == ACTION_DOWNLOAD_APK and data["apk_url"] and data["apk_name"]:
            self.page.run_thread(self._download_and_install, data["apk_url"], data["apk_name"])
            return
        await self._open_release(data["release_url"])

    @staticmethod
    def _parse_payload(payload: str | None) -> dict[str, str] | None:
        if not payload:
            return None
        try:
            raw = json.loads(payload)
        except ValueError:
            logger.exception("Unable to parse the notification payload")
            return None
        if not isinstance(raw, dict):
            return None
        return {
            "release_url": str(raw.get("release_url", "")),
            "apk_url": str(raw.get("apk_url", "")),
            "apk_name": str(raw.get("apk_name", "")),
        }

    async def _open_release(self, release_url: str) -> None:
        if not release_url:
            return
        try:
            await self.launcher.launch_url(release_url)
        except Exception:
            logger.exception("Unable to open the release page: {}", release_url)

    def _download_and_install(self, apk_url: str, apk_name: str) -> None:
        """Blocking worker: enqueue the download, then install on the event loop."""
        from libresvip.mobile import android

        try:
            download_id = android.enqueue_apk_download(apk_url, apk_name)
            uri = android.wait_for_downloaded_uri(download_id, DOWNLOAD_TIMEOUT)
        except Exception:
            logger.exception("Unable to download the APK: {}", apk_url)
            uri = None
        if uri is None:
            self.page.run_task(
                self.notifier.notify,
                _("Update failed"),
                _("Unable to download {}. Please try again later.").format(apk_name),
            )
            return
        self.page.run_task(self._install, uri)

    async def _install(self, uri: str) -> None:
        from libresvip.mobile import android

        try:
            android.install_apk(uri)
        except Exception:
            logger.exception("Unable to start the APK installation")
            await self.notifier.notify(
                _("Update failed"),
                _("Unable to start the installation. Please open the release page instead."),
            )
