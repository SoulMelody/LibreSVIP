import asyncio
import fnmatch
import platform
import time
from collections.abc import Awaitable, Sequence
from functools import partial
from typing import TYPE_CHECKING, Optional

import httpx
from desktop_notifier import Button, DesktopNotifier, Notification
from loguru import logger
from packaging.version import Version
from PySide6.QtCore import QObject, QTimer, Slot
from PySide6.QtQml import QmlElement

from __feature__ import snake_case, true_property  # isort:skip # noqa: F401

import libresvip
from libresvip.core.compat import as_file
from libresvip.core.constants import PACKAGE_NAME, app_dir, res_dir
from libresvip.utils.translation import gettext_lazy as _

from .application import app, event_loop
from .url_opener import open_path, open_url

if TYPE_CHECKING:
    from contextlib import AbstractContextManager
    from pathlib import Path

QML_IMPORT_NAME = "LibreSVIP"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QmlElement
class Notifier(QObject):
    def __init__(self) -> None:
        super().__init__()
        self.request_timeout = 30
        self.last_notify_time: Optional[float] = None
        try:
            icon_path: AbstractContextManager[Path] = as_file(res_dir / "libresvip.ico")
            app.aboutToQuit.connect(lambda: icon_path.__exit__(None, None, None))
            self.notifier = DesktopNotifier(app_name=PACKAGE_NAME, app_icon=icon_path.__enter__())
            self.notifier._loop = event_loop
        except Exception:
            self.notifier = None

    async def download_release(self, url: str, filename: str) -> None:
        app_dir.user_downloads_path.mkdir(parents=True, exist_ok=True)
        async with httpx.AsyncClient(follow_redirects=True, verify=False) as client:
            try:
                await self.clear_all_messages_async()
                await self.notify_async(title=_("Downloading"), message=_("Please wait..."))
                with (app_dir.user_downloads_path / filename).open("wb") as f:
                    async with client.stream("GET", url) as response:
                        response.raise_for_status()
                        async for chunk in response.aiter_bytes():
                            f.write(chunk)
                            f.flush()
                open_path(app_dir.user_downloads_path)
            except httpx.HTTPError:
                await self.notify_async(
                    title=_("Error occurred while Downloading"),
                    message=_("Failed to download file {}. Please try again later.").format(
                        filename
                    ),
                )

    async def _check_for_updates(self) -> None:
        failed = False
        logger.info("Checking for updates...")
        async with httpx.AsyncClient(
            follow_redirects=True, timeout=self.request_timeout, verify=False
        ) as client:
            try:
                await self.clear_all_messages_async()
                await self.notify_async(
                    title=_("Checking for Updates"),
                    message=_("Please wait..."),
                    send_timeout=self.request_timeout,
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
                        arch = uname.machine.lower()
                        buttons = [
                            Button(
                                _("Open in Browser"),
                                partial(
                                    open_url,
                                    data["html_url"],
                                ),
                            )
                        ]
                        if arch.endswith("64"):
                            asset = None
                            if "aarch" in arch and uname.system != "Linux":
                                pass
                            elif uname.system == "Windows":
                                python_compiler = platform.python_compiler()
                                if python_compiler.startswith("GCC") and "arm" not in arch:
                                    asset = next(
                                        (
                                            asset
                                            for asset in data["assets"]
                                            if fnmatch.fnmatch(
                                                asset["name"],
                                                "LibreSVIP-*.msys2-*.7z",
                                            )
                                        ),
                                        None,
                                    )
                                else:
                                    asset = next(
                                        (
                                            asset
                                            for asset in data["assets"]
                                            if fnmatch.fnmatch(
                                                asset["name"],
                                                f"LibreSVIP-*.win-{arch}.*",
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
                            elif uname.system == "Darwin":
                                asset = next(
                                    (
                                        asset
                                        for asset in data["assets"]
                                        if fnmatch.fnmatch(
                                            asset["name"],
                                            f"LibreSVIP-*.macos-{arch}.dmg",
                                        )
                                    ),
                                    None,
                                )
                            if asset:
                                buttons.append(
                                    Button(
                                        _("Download"),
                                        lambda: self.notifier._loop.create_task(
                                            self.download_release(
                                                asset["browser_download_url"],
                                                asset["name"],
                                            ),
                                        ),
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
                    failed = True
            except httpx.HTTPError:
                failed = True
            if failed:
                await self.notify_async(
                    title=_("Error occurred while Checking for Updates"),
                    message=_("Failed to check for updates. Please try again later."),
                )

    @Slot(result=None)
    def check_for_updates(self) -> None:
        timer = QTimer(self)
        timer.interval = 100

        def ensure_running_loop() -> None:
            if event_loop.is_running():
                event_loop.create_task(self._check_for_updates())
                timer.stop()

        timer.timeout.connect(ensure_running_loop)
        timer.start()

    async def notify_async(
        self,
        title: str,
        message: str,
        buttons: Sequence[Button] = (),
        send_timeout: int = -1,
    ) -> Optional[Awaitable[Notification]]:
        try:
            if self.last_notify_time is None:
                pass
            elif (elapsed := time.time() - self.last_notify_time) < 1:
                await asyncio.sleep(1 - elapsed)
            self.last_notify_time = time.time()
            return await self.notifier.send(
                title=title,
                message=message,
                buttons=buttons,
                timeout=send_timeout,
            )
        except Exception as e:
            logger.exception(e)

    async def clear_all_messages_async(self) -> None:
        try:
            if len(self.notifier.current_notifications):
                await self.notifier.clear_all()
        except Exception as e:
            logger.exception(e)

    @Slot(str)
    def open_link(self, url: str) -> None:
        open_url(url)
