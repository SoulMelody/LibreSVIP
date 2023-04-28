from qmlease import app, slot
from qtpy.QtCore import QObject


class Clipboard(QObject):
    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)

    @slot(str)
    def set_clipboard(self, text):
        clipboard = app.clipboard()
        clipboard.setText(text)
