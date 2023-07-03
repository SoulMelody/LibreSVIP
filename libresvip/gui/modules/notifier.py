from gettext import gettext as _
from typing import Optional

import httpx
import qtinter
from desktop_notifier import DesktopNotifier, Notification
from loguru import logger
from qmlease import slot
from qtpy.QtCore import QObject
from setuptools.extern.packaging.version import Version

import libresvip
from libresvip.core.config import settings
from libresvip.core.constants import PACKAGE_NAME, res_dir


class Notifier(QObject):
    def __init__(self):
        super().__init__()
        try:
            self.notifier = DesktopNotifier(
                app_name=PACKAGE_NAME, app_icon=res_dir / "libresvip.ico"
            )
        except Exception:
            self.notifier = None
        if settings.auto_check_for_updates:
            self.check_for_updates()

    @slot()
    @qtinter.asyncslot
    async def check_for_updates(self):
        client = httpx.AsyncClient(follow_redirects=True, timeout=30)
        try:
            await self.clear_all_messages_async()
            waiting_notification = await self.notify_async(title=_("Checking for Updates"), message=_("Please wait..."))
            resp = await client.get(
                "https://api.github.com/repos/SoulMelody/LibreSVIP/releases/latest"
            )
            if waiting_notification:
                await self.clear_message_async(waiting_notification)
            if resp.status_code == 200:
                data = resp.json()
                local_version = Version(libresvip.__version__)
                remote_version = Version(data["tag_name"].removeprefix("v"))
                if remote_version > local_version:
                    await self.notify_async(
                        title=_("Update Available"),
                        message=_("New version {} is available.").format(remote_version),
                    )
                else:
                    await self.notify_async(
                        title=_("No Updates"),
                        message=_("You are using the latest version {}.").format(local_version),
                    )
        except httpx.HTTPError:
            await self.notify_async(
                title=_("Error occurred while Checking for Updates"),
                message=_("Failed to check for updates. Please try again later."),
            )

    async def notify_async(self, title, message) -> Optional[Notification]:
        try:
            return await self.notifier.send(title=title, message=message)
        except Exception as e:
            logger.error(e)

    async def clear_message_async(self, notification: Notification):
        try:
            await self.notifier.clear(notification)
        except Exception as e:
            logger.error(e)

    async def clear_all_messages_async(self):
        try:
            await self.notifier.clear_all()
        except Exception as e:
            logger.error(e)
