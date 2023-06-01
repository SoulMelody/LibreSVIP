from loguru import logger
from qmlease import slot
from qtpy.QtCore import QObject

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

    @slot(str, str)
    def notify(self, title, message):
        try:
            if self.notifier:
                self.notifier.send(title=title, message=message)
            elif self.notification:
                self.notification.title = title
                self.notification.message = message

                self.notification.send()
        except Exception as e:
            logger.error(e)
