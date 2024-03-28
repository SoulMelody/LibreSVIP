import base64
import pathlib
from typing import Any, Optional

from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtQml import QmlElement, QmlSingleton

from __feature__ import snake_case, true_property  # isort:skip # noqa: F401

import libresvip
from libresvip.core.config import ConflictPolicy, DarkMode, save_settings, settings
from libresvip.core.constants import res_dir
from libresvip.extension.manager import plugin_manager
from libresvip.gui.models.list_models import ModelProxy
from libresvip.gui.models.table_models import PluginCadidatesTableModel

from .application import app

QML_IMPORT_NAME = "LibreSVIP"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QmlElement
@QmlSingleton
class ConfigItems(QObject):
    auto_set_output_extension_changed = Signal(bool)

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent=parent)
        self.folder_presets = ModelProxy({"path": ""})
        self.folder_presets.append_many(
            [{"path": self.posix_path(path)} for path in settings.folder_presets]
        )
        self.plugin_candidates = PluginCadidatesTableModel()
        app.aboutToQuit.connect(self.save_settings)

    def save_settings(self) -> None:
        settings.folder_presets = [pathlib.Path(item["path"]) for item in self.folder_presets.items]
        save_settings()

    @Slot(result=str)
    def icon_data(self) -> str:
        return f"data:image/x-icon;base64,{base64.b64encode((res_dir / 'libresvip.ico').read_bytes()).decode()}"

    @Slot(str, result="QVariant")
    def qget(self, name: str) -> Any:
        return getattr(self, name)

    @Slot(result=str)
    def get_version(self) -> str:
        return libresvip.__version__

    @Slot(result=str)
    def get_conflict_policy(self) -> str:
        return settings.conflict_policy.value

    @Slot(str, result=bool)
    def set_conflict_policy(self, policy: str) -> bool:
        try:
            conflict_policy = ConflictPolicy(policy)
            settings.conflict_policy = conflict_policy
        except ValueError:
            return False
        else:
            return True

    @Slot(result=str)
    def get_theme(self) -> str:
        return settings.dark_mode.value

    @Slot(str, result=bool)
    def set_theme(self, theme: str) -> bool:
        try:
            dark_mode = DarkMode(theme)
            settings.dark_mode = dark_mode
        except ValueError:
            return False
        else:
            return True

    @Slot(int, result=bool)
    def toggle_plugin(self, index: int) -> bool:
        key = plugin_manager._candidates[index][1].suffix
        if key in plugin_manager.plugin_registry and key not in settings.disabled_plugins:
            settings.disabled_plugins.append(key)
        elif key in settings.disabled_plugins:
            settings.disabled_plugins.remove(key)
        else:
            return False
        plugin_manager.import_plugins(reload=True)
        self.plugin_candidates.reload_formats()
        return True

    @Slot(str, result=bool)
    def enabled(self, key: str) -> bool:
        return key in plugin_manager.plugin_registry

    @Slot(str, result=bool)
    def get_bool(self, key: str) -> bool:
        return getattr(settings, key)

    @Slot(str, bool, result=bool)
    def set_bool(self, key: str, value: bool) -> bool:
        if hasattr(settings, key):
            setattr(settings, key, value)
            if key == "auto_set_output_extension":
                self.auto_set_output_extension_changed.emit(value)
            return True
        return False

    @staticmethod
    def posix_path(path: pathlib.Path) -> str:
        return str(path.as_posix())

    @Slot(result=str)
    def get_save_folder(self) -> str:
        return self.posix_path(settings.save_folder)

    @Slot(str, result=bool)
    def dir_valid(self, value: str) -> bool:
        path = pathlib.Path(value)
        return (not path.is_absolute() or path.exists()) and path.is_dir()

    @Slot(str)
    def set_save_folder(self, value: str) -> None:
        settings.save_folder = pathlib.Path(value)
