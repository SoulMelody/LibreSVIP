import shutil

from qmlease import slot
from qtpy.QtCore import QObject


class FileOperations(QObject):
    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)

    @slot(str, str, result=bool)
    def move(self, src: str, dst: str) -> bool:
        try:
            shutil.move(src, dst)
            return True
        except Exception:
            return False
