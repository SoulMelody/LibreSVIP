import asyncio
import fnmatch
import platform
from functools import partial
from gettext import gettext as _
from typing import Optional, Sequence

import httpx
import qtinter
from desktop_notifier import Button, DesktopNotifier, Notification
from loguru import logger
from packaging.version import Version
from qmlease import slot
from qtpy.QtCore import QObject

import libresvip
from libresvip.core.config import settings
from libresvip.core.constants import PACKAGE_NAME, app_dir, res_dir

from .url_opener import open_path, open_url


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
                await self.notify_async(title=_("Downloading"), message=_("Please wait..."))
                with open(app_dir.user_downloads_path / filename, "wb") as f:
                    async with client.stream('GET', url) as response:
                        response.raise_for_status()
                        async for chunk in response.aiter_bytes():
                            f.write(chunk)
                            f.flush()
                open_path(app_dir.user_downloads_path)
            except httpx.HTTPError:
                await self.notify_async(
                    title=_("Error occurred while Downloading"),
                    message=_("Failed to download file {}. Please try again later.").format(filename),
                )

    @slot()
    @qtinter.asyncslot
    async def check_for_updates(self):
        async with httpx.AsyncClient(follow_redirects=True, timeout=self.request_timeout) as client:
            try:
                await self.clear_all_messages_async()
                await self.notify_async(title=_("Checking for Updates"), message=_("Please wait..."), timeout=self.request_timeout)
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
                                _("Open in Browser"),
                                partial(
                                    open_url,
                                    data["html_url"],
                                )
                            )
                        ]
                        if uname.machine == "AMD64":
                            arch = "x64"
                            asset = None
                            if uname.system == "Windows":
                                asset = next(
                                    (
                                        asset
                                        for asset in data["assets"]
                                        if fnmatch.fnmatch(asset["name"], f"{PACKAGE_NAME}-v*-win-{arch}.tar.xz")
                                    ),
                                    None,
                                )
                            elif uname.system == "Linux":
                                asset = next(
                                    (
                                        asset
                                        for asset in data["assets"]
                                        if fnmatch.fnmatch(asset["name"], f"{PACKAGE_NAME}-v*-linux-{arch}.tar.xz")
                                    ),
                                    None,
                                )
                            if asset:
                                buttons.append(
                                    Button(
                                        _("Download"),
                                        lambda : self.notifier._loop.create_task(
                                            self.download_release(
                                                asset["browser_download_url"],
                                                asset["name"]
                                            ),
                                        )
                                    ),
                                )
                        await self.notify_async(
                            title=_("Update Available"),
                            message=_("New version {} is available.").format(remote_version),
                            buttons=buttons,
                        )
                    else:
                        await self.notify_async(
                            title=_("No Updates"),
                            message=_("You are using the latest version {}.").format(local_version),
                        )
                else:
                    await self.notify_async(
                        title=_("Error occurred while Checking for Updates"),
                        message=_("Failed to check for updates. Please try again later."),
                    )
            except httpx.HTTPError:
                await self.notify_async(
                    title=_("Error occurred while Checking for Updates"),
                    message=_("Failed to check for updates. Please try again later."),
                )

    async def notify_async(
        self,
        title: str,
        message: str,
        buttons: Sequence[Button] = (),
        timeout: int = -1
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
