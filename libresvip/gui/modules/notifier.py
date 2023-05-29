from desktop_notifier import DesktopNotifier
from qmlease import slot
from qtpy.QtCore import QObject

from libresvip.core.constants import PACKAGE_NAME, res_dir


class Notifier(QObject):
    def __init__(self):
        super().__init__()
        try:
            self.notifier = DesktopNotifier(PACKAGE_NAME, res_dir / "libresvip.ico")
        except Exception:
            self.notifier = None

    @slot(str, str)
    def notify(self, title, message):
        if self.notifier:
            self.notifier.send_sync(title=title, message=message)
