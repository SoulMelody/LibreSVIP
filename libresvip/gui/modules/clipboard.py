from qmlease import app, slot
from qtpy.QtCore import QObject


class Clipboard(QObject):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.clipboard = app.clipboard()

    @slot(str, result=bool)
    def set_clipboard(self, text):
        self.clipboard.setText(text)
        return True
