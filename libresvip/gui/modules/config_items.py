from __future__ import annotations

import base64
import dataclasses
import pathlib
from typing import Any, Optional

from PySide6.QtCore import Property, QObject, Signal, Slot
from PySide6.QtQml import QmlElement

from __feature__ import snake_case, true_property  # isort:skip # noqa: F401

import libresvip
from libresvip.core.config import (
    ConflictPolicy,
    DarkMode,
    LibreSvipSettings,
    save_settings,
    settings,
)
from libresvip.core.constants import res_dir
from libresvip.extension.manager import plugin_manager
from libresvip.gui.models.list_models import (
    LyricReplacementPresetsModel,
    ModelProxy,
)
from libresvip.gui.models.table_models import LyricReplacementRulesTableModel

from .application import app

QML_IMPORT_NAME = "LibreSVIP"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


def base_prop_factory(attrs: dict[str, Any], field_name: str, field_type: type) -> None:
    signal = Signal(field_type, name=f"{field_name}_changed")

    def _getter(self: QObject) -> Any:
        return getattr(settings, field_name)

    def _setter(self: QObject, value: Any) -> None:
        setattr(settings, field_name, value)
        getattr(self, f"{field_name}_changed").emit(value)

    attrs[field_name] = Property(field_type, _getter, _setter, notify=signal)
    attrs[f"{field_name}_changed"] = signal


class AutoBindBaseConfigMetaObject(type(QObject)):  # type: ignore[misc]
    def __new__(cls, name: str, bases: tuple[type], attrs: dict[str, Any]) -> type[QObject]:
        for field in dataclasses.fields(LibreSvipSettings):  # type: ignore[arg-type]
            if field.type == "bool":
                base_prop_factory(attrs, field.name, bool)
            elif field.type == "int":
                base_prop_factory(attrs, field.name, int)
        return super().__new__(cls, name, bases, attrs)


@QmlElement
class ConfigItems(QObject, metaclass=AutoBindBaseConfigMetaObject):
    save_folder_changed = Signal(str)
    conflict_policy_changed = Signal(str)
    theme_changed = Signal(str)

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent=parent)
        self.folder_presets = ModelProxy({"path": ""})
        self.folder_presets.append_many(
            [{"path": self.posix_path(path)} for path in settings.folder_presets]
        )
        self.lyric_replacement_presets = LyricReplacementPresetsModel()
        app.aboutToQuit.connect(self.save_settings)

    def save_settings(self) -> None:
        settings.folder_presets = [pathlib.Path(item["path"]) for item in self.folder_presets.items]
        save_settings()

    @Property(str, constant=True)
    def icon_data(self) -> str:
        return f"data:image/x-icon;base64,{base64.b64encode((res_dir / 'libresvip.ico').read_bytes()).decode()}"

    @Property(str, constant=True)
    def version(self) -> str:
        return libresvip.__version__

    @Slot(str, result="QVariant")
    def qget(self, name: str) -> Any:
        return getattr(self, name)

    @Slot(str, result="QVariant")
    def rules_for_preset(self, preset: str) -> Any:
        self.result = LyricReplacementRulesTableModel(preset)
        return self.result

    def get_save_folder(self) -> str:
        return self.posix_path(settings.save_folder)

    def set_save_folder(self, value: str) -> None:
        settings.save_folder = pathlib.Path(value)
        self.save_folder_changed.emit(self.get_save_folder())

    save_folder = Property(str, get_save_folder, set_save_folder, notify=save_folder_changed)

    def get_conflict_policy(self) -> str:
        return settings.conflict_policy.value

    def set_conflict_policy(self, policy: str) -> None:
        conflict_policy = ConflictPolicy(policy)
        settings.conflict_policy = conflict_policy
        self.conflict_policy_changed.emit(policy)

    conflict_policy = Property(
        str,
        get_conflict_policy,
        set_conflict_policy,
        notify=conflict_policy_changed,
    )

    def get_theme(self) -> str:
        return settings.dark_mode.value

    def set_theme(self, theme: str) -> None:
        dark_mode = DarkMode(theme)
        settings.dark_mode = dark_mode
        self.theme_changed.emit(theme)

    theme = Property(str, get_theme, set_theme, notify=theme_changed)

    @Slot(str, result=bool)
    def enabled(self, key: str) -> bool:
        return key in plugin_manager.plugin_registry

    @staticmethod
    def posix_path(path: pathlib.Path) -> str:
        return str(path.as_posix())

    @Slot(str, result=bool)
    def dir_valid(self, value: str) -> bool:
        path = pathlib.Path(value)
        return (not path.is_absolute() or path.exists()) and path.is_dir()
