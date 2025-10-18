import functools

from fonticon_mdi7 import MDI7
from PySide6.QtCore import QObject, QUrl, Slot

from __feature__ import snake_case, true_property  # isort:skip # noqa: F401


class IconicFontLoader(QObject):
    @Slot(str, result=str)
    def font_path(self, font_family: str) -> str:
        return QUrl.from_local_file(MDI7.__font_file__).to_string()

    @Slot(str, result=str)
    @functools.cache
    def icon(self, icon_name: str) -> str:
        font_family, _, icon_name = icon_name.partition(".")
        icon_name = icon_name.replace("-", "_")
        if font_family != "mdi7":
            return ""
        return getattr(MDI7, icon_name, "").partition(".")[-1]
