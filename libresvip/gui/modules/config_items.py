import pathlib

from qmlease import slot
from qtpy.QtCore import QObject

from libresvip.core.config import ConflictPolicy, DarkMode, save_settings, settings


class ConfigItems(QObject):
    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)

    @slot(result=str)
    def get_conflict_policy(self) -> str:
        return settings.conflict_policy.value

    @slot(str, result=bool)
    def set_conflict_policy(self, policy: str) -> bool:
        try:
            conflict_policy = ConflictPolicy(policy)
            settings.conflict_policy = conflict_policy
            save_settings()
            return True
        except ValueError:
            return False

    @slot(result=str)
    def get_theme(self) -> str:
        return settings.dark_mode.value

    @slot(str, result=bool)
    def set_theme(self, theme: str) -> bool:
        try:
            dark_mode = DarkMode(theme)
            settings.dark_mode = dark_mode
            save_settings()
            return True
        except ValueError:
            return False

    @slot(str, result=bool)
    def get_bool(self, key) -> bool:
        return getattr(settings, key)

    @slot(str, bool, result=bool)
    def set_bool(self, key, value) -> bool:
        if hasattr(settings, key):
            setattr(settings, key, value)
            save_settings()
            return True
        return False

    @slot(result=str)
    def get_save_folder(self):
        return str(settings.save_folder.as_posix())

    @slot(str, result=bool)
    def set_save_folder(self, value) -> bool:
        path = pathlib.Path(value)
        if path.exists() and path.is_dir():
            settings.save_folder = path
            save_settings()
            return True
        return False
