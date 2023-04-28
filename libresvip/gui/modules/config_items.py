import pathlib

from qmlease import slot
from qtpy.QtCore import QObject

from libresvip.core.config import save_settings, settings


class ConfigItems(QObject):
    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)

    @slot(result=str)
    def get_save_folder(self):
        return str(settings.save_folder)

    @slot(str, result=bool)
    def set_save_folder(self, value) -> bool:
        path = pathlib.Path(value)
        if path.exists() and path.is_dir():
            settings.save_folder = path
            save_settings()
            return True
        return False
