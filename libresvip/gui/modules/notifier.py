from desktop_notifier import DesktopNotifier
from qmlease import slot
from qtpy.QtCore import QObject

from libresvip.core.constants import PACKAGE_NAME, pkg_dir


class Notifier(QObject):
    def __init__(self):
        super().__init__()
        self.notifier = DesktopNotifier(PACKAGE_NAME, pkg_dir / "libresvip.ico")

    @slot(str, str)
    def notify(self, title, message):
        self.notifier.send_sync(title=title, message=message)
