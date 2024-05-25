import functools

from fonticon_mdi7 import MDI7
from PySide6.QtCore import QObject, QUrl, Slot
from PySide6.QtQml import QmlElement

from __feature__ import snake_case, true_property  # isort:skip # noqa: F401

QML_IMPORT_NAME = "LibreSVIP"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QmlElement
class IconicFontLoader(QObject):
    @Slot(str, result=str)
    def font_path(self, font_family: str) -> str:
        return QUrl.from_local_file(MDI7.__font_file__).to_string()

    @Slot(str, result=str)
    @functools.cache
    def icon(self, icon_name: str) -> str:
        font_family, _, icon_name = icon_name.partition(".")
        icon_name = icon_name.replace("-", "_")
        return getattr(MDI7, icon_name, "").partition(".")[-1]
