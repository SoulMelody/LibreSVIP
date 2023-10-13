import asyncio
import fnmatch
import platform
from functools import partial
from typing import Optional, Sequence

import httpx
import qtinter
from desktop_notifier import Button, DesktopNotifier, Notification
from loguru import logger
from packaging.version import Version
from PySide6.QtCore import QObject, Slot
from PySide6.QtQml import QmlElement, QmlSingleton

import libresvip
from libresvip.core.config import settings
from libresvip.core.constants import PACKAGE_NAME, app_dir, res_dir

from .url_opener import open_path, open_url

QML_IMPORT_NAME = "LibreSVIP"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QmlElement
@QmlSingleton
class Notifier(QObject):
    def __init__(self):
        super().__init__()
        self.request_timeout = 30
        try:
            self.notifier = DesktopNotifier(
                app_name=PACKAGE_NAME, app_icon=res_dir / "libresvip.ico"
            )
            self.notifier._loop = asyncio.get_event_loop()
        except Exception:
            self.notifier = None
        if settings.auto_check_for_updates:
            self.check_for_updates()

    async def download_release(self, url: str, filename: str):
        app_dir.user_downloads_path.mkdir(parents=True, exist_ok=True)
        async with httpx.AsyncClient(follow_redirects=True, verify=False) as client:
            try:
                await self.clear_all_messages_async()
                await self.notify_async(
                    title=self.tr("Downloading"), message=self.tr("Please wait...")
                )
                with (app_dir.user_downloads_path / filename).open("wb") as f:
                    async with client.stream("GET", url) as response:
                        response.raise_for_status()
                        async for chunk in response.aiter_bytes():
                            f.write(chunk)
                            f.flush()
                open_path(app_dir.user_downloads_path)
            except httpx.HTTPError:
                await self.notify_async(
                    title=self.tr("Error occurred while Downloading"),
                    message=self.tr(
                        "Failed to download file {}. Please try again later."
                    ).format(filename),
                )

    @Slot()
    @qtinter.asyncslot
    async def check_for_updates(self):
        failed = False
        async with httpx.AsyncClient(
            follow_redirects=True, timeout=self.request_timeout
        ) as client:
            try:
                await self.clear_all_messages_async()
                await self.notify_async(
                    title=self.tr("Checking for Updates"),
                    message=self.tr("Please wait..."),
                    timeout=self.request_timeout,
                )
                resp = await client.get(
                    "https://api.github.com/repos/SoulMelody/LibreSVIP/releases/latest"
                )
                if resp.status_code == 200:
                    data = resp.json()
                    local_version = Version(libresvip.__version__)
                    remote_version = Version(data["tag_name"].removeprefix("v"))
                    if remote_version > local_version:
                        uname = platform.uname()
                        buttons = [
                            Button(
                                self.tr("Open in Browser"),
                                partial(
                                    open_url,
                                    data["html_url"],
                                ),
                            )
                        ]
                        if uname.machine.endswith("64"):
                            arch = uname.machine.lower()
                            asset = None
                            if uname.system == "Windows":
                                asset = next(
                                    (
                                        asset
                                        for asset in data["assets"]
                                        if fnmatch.fnmatch(
                                            asset["name"], f"LibreSVIP-*.win-{arch}.zip"
                                        )
                                    ),
                                    None,
                                )
                            elif uname.system == "Linux":
                                asset = next(
                                    (
                                        asset
                                        for asset in data["assets"]
                                        if fnmatch.fnmatch(
                                            asset["name"],
                                            f"LibreSVIP-*.linux-{arch}.tar.gz",
                                        )
                                    ),
                                    None,
                                )
                            if asset:
                                buttons.append(
                                    Button(
                                        self.tr("Download"),
                                        lambda: self.notifier._loop.create_task(
                                            self.download_release(
                                                asset["browser_download_url"],
                                                asset["name"],
                                            ),
                                        ),
                                    ),
                                )
                        await self.notify_async(
                            title=self.tr("Update Available"),
                            message=self.tr("New version {} is available.").format(
                                remote_version
                            ),
                            buttons=buttons,
                        )
                    else:
                        await self.notify_async(
                            title=self.tr("No Updates"),
                            message=self.tr(
                                "You are using the latest version {}."
                            ).format(local_version),
                        )
                else:
                    failed = True
            except httpx.HTTPError:
                failed = True
            if failed:
                await self.notify_async(
                    title=self.tr("Error occurred while Checking for Updates"),
                    message=self.tr(
                        "Failed to check for updates. Please try again later."
                    ),
                )

    async def notify_async(
        self,
        title: str,
        message: str,
        buttons: Sequence[Button] = (),
        timeout: int = -1,
    ) -> Optional[Notification]:
        try:
            return await self.notifier.send(
                title=title, message=message, buttons=buttons, timeout=timeout
            )
        except Exception as e:
            logger.error(e)

    async def clear_all_messages_async(self):
        try:
            if len(self.notifier.current_notifications):
                await self.notifier.clear_all()
        except Exception as e:
            logger.error(e)
