import atexit
import base64
import pathlib
from typing import Any, Optional

from qmlease import slot
from qtpy.QtCore import QObject, Signal

import libresvip
from libresvip.core.config import ConflictPolicy, DarkMode, save_settings, settings
from libresvip.core.constants import res_dir

from .model_proxy import ModelProxy


class ConfigItems(QObject):
    auto_set_output_extension_changed = Signal(bool)

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent=parent)
        self.folder_presets = ModelProxy({"path": ""})
        self.folder_presets.append_many(
            [{"path": self.posix_path(path)} for path in settings.folder_presets]
        )
        atexit.register(self.save_settings)

    def save_settings(self) -> None:
        settings.folder_presets = [
            pathlib.Path(item["path"]) for item in self.folder_presets.items
        ]
        save_settings()

    @slot(result=str)
    def icon_data(self) -> str:
        return f"data:image/x-icon;base64,{base64.b64encode((res_dir / 'libresvip.ico').read_bytes()).decode()}"

    @slot(str, result=object)
    def qget(self, name: str) -> Any:
        return getattr(self, name)

    @slot(result=str)
    def get_version(self) -> str:
        return libresvip.__version__

    @slot(result=str)
    def get_conflict_policy(self) -> str:
        return settings.conflict_policy.value

    @slot(str, result=bool)
    def set_conflict_policy(self, policy: str) -> bool:
        try:
            conflict_policy = ConflictPolicy(policy)
            settings.conflict_policy = conflict_policy
        except ValueError:
            return False
        else:
            return True

    @slot(result=str)
    def get_theme(self) -> str:
        return settings.dark_mode.value

    @slot(str, result=bool)
    def set_theme(self, theme: str) -> bool:
        try:
            dark_mode = DarkMode(theme)
            settings.dark_mode = dark_mode
        except ValueError:
            return False
        else:
            return True

    @slot(str, result=bool)
    def get_bool(self, key: str) -> bool:
        return getattr(settings, key)

    @slot(str, bool, result=bool)
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

    @slot(result=str)
    def get_save_folder(self) -> str:
        return self.posix_path(settings.save_folder)

    @slot(str, result=bool)
    def dir_valid(self, value: str) -> bool:
        path = pathlib.Path(value)
        return (not path.is_absolute() or path.exists()) and path.is_dir()

    @slot(str)
    def set_save_folder(self, value: str) -> None:
        settings.save_folder = pathlib.Path(value)
