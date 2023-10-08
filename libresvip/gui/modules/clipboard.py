from qtpy.QtCore import QObject, Slot
from qtpy.QtGui import QGuiApplication
from qtpy.QtQml import QmlElement, QmlSingleton

QML_IMPORT_NAME = "LibreSVIP"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QmlElement
@QmlSingleton
class Clipboard(QObject):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.clipboard = QGuiApplication.clipboard()

    @Slot(str, result=bool)
    def set_clipboard(self, text):
        self.clipboard.setText(text)
        return True
