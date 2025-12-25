from PySide6.QtCore import QObject, Slot

from __feature__ import snake_case, true_property  # isort:skip # noqa: F401

from libresvip.utils.text import shorten_error_message

from .application import app


class Clipboard(QObject):
    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent=parent)
        self.clipboard = app.clipboard()

    @Slot(str, result=bool)
    def set_clipboard(self, text: str) -> bool:
        self.clipboard.set_text(text)
        return True

    @Slot(str, result=str)
    def shorten_error_message(self, msg: str) -> str:
        return shorten_error_message(msg)
