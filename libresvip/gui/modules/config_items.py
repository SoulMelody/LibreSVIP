import os

from qmlease import slot
from qtpy.QtCore import QObject


class ConfigItems(QObject):
    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)
        self._save_folder = ""

    @slot(result=str)
    def get_save_folder(self):
        return self._save_folder

    @slot(str, result=bool)
    def set_save_folder(self, value) -> bool:
        if os.path.exists(value) and os.path.isdir(value):
            self._save_folder = value
            return True
        return False
