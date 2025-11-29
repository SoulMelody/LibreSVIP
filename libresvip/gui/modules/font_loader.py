import json
from importlib.metadata import files

from PySide6.QtCore import QObject, Slot
from PySide6.QtGui import QFontDatabase

from __feature__ import snake_case, true_property  # isort:skip # noqa: F401


PACKAGE_FILES = files("ttkbootstrap_icons_mat")


class IconicFontLoader(QObject):
    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        glyphmap_file = next(each for each in PACKAGE_FILES if each.name == "glyphmap.json")  # type: ignore[union-attr]
        self.material_icons_glyphmap = {
            k: (("\\U" + v.zfill(8)) if len(v) > 4 else ("\\u" + v.zfill(4)))
            .encode("utf-8")
            .decode("unicode-escape")
            for k, v in json.loads(glyphmap_file.read_binary()).items()
        }
        material_icons_font_file = next(
            each
            for each in PACKAGE_FILES  # type: ignore[union-attr]
            if each.name == "materialdesignicons-webfont.ttf"
        )
        QFontDatabase.addApplicationFontFromData(material_icons_font_file.read_binary())

    @Slot(str, result=str)
    def icon(self, icon_name: str) -> str:
        font_family, _, icon_name = icon_name.partition(".")
        if font_family != "mdi7":
            return ""
        return self.material_icons_glyphmap.get(icon_name, "")
