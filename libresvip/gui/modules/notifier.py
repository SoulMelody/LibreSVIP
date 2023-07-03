import httpx
import qtinter
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
            from desktop_notifier import DesktopNotifier

            self.notifier = DesktopNotifier(
                app_name=PACKAGE_NAME, app_icon=res_dir / "libresvip.ico"
            )
            self.notification = None
        except Exception:
            from notifypy import Notify

            self.notification = Notify(
                default_notification_application_name=PACKAGE_NAME,
                default_notification_icon=res_dir / "libresvip.ico",
            )
            self.notifier = None
        if settings.auto_check_for_updates:
            self.check_for_updates()

    @slot()
    @qtinter.asyncslot
    async def check_for_updates(self):
        await self.notify_async(title="Checking for Updates", message="Please wait...")
        client = httpx.AsyncClient(follow_redirects=True, timeout=30)
        try:
            resp = await client.get(
                "https://api.github.com/repos/SoulMelody/LibreSVIP/releases/latest"
            )
            if resp.status_code == 200:
                data = resp.json()
                local_version = Version(libresvip.__version__)
                remote_version = Version(data["tag_name"].removeprefix("v"))
                if remote_version > local_version:
                    await self.notify_async(
                        title="Update Available",
                        message=f"New version {remote_version} is available.",
                    )
                else:
                    await self.notify_async(
                        title="No Updates",
                        message=f"You are using the latest version {local_version}.",
                    )
        except httpx.HTTPError:
            await self.notify_async(
                title="Error",
                message="Failed to check for updates. Please try again later.",
            )

    async def notify_async(self, title, message):
        try:
            if self.notifier:
                await self.notifier.send(title=title, message=message)
            elif self.notification:
                self.notification.title = title
                self.notification.message = message

                self.notification.send()
        except Exception as e:
            logger.error(e)

    @slot(str, str)
    def notify(self, title, message):
        try:
            if self.notifier:
                self.notifier.send_sync(title=title, message=message)
            elif self.notification:
                self.notification.title = title
                self.notification.message = message

                self.notification.send()
        except Exception as e:
            logger.error(e)
