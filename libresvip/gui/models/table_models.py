import enum
from functools import cache
from gettext import gettext as _
from typing import Any, Optional

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from __feature__ import snake_case, true_property  # isort:skip # noqa: F401

from libresvip.core.config import settings
from libresvip.extension.manager import plugin_manager


class PluginCadidatesTableModel(QAbstractTableModel):
    def __init__(self) -> None:
        super().__init__()
        self.column_names = [_("Applicable File Format"), _("Author"), _("Version"), "On/Off"]
        self.plugin_candidates: list[dict[int, str]] = []
        self.reload_formats()

    def reload_formats(self) -> None:
        self.begin_remove_rows(QModelIndex(), 0, len(self.plugin_candidates) - 1)
        self.plugin_candidates.clear()
        self.end_remove_rows()
        self.begin_insert_rows(QModelIndex(), 0, len(plugin_manager._candidates) - 1)
        self.plugin_candidates = [
            {
                0: plugin.file_format,
                1: plugin.author,
                2: str(plugin.version),
                3: "checkbox-marked"
                if plugin.suffix not in settings.disabled_plugins
                else "checkbox-blank-outline",
            }
            for _path, plugin in plugin_manager._candidates
        ]
        self.end_insert_rows()

    def row_count(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.plugin_candidates)

    def column_count(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.column_names)

    def header_data(
        self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole
    ) -> Optional[str]:
        if role != Qt.ItemDataRole.DisplayRole:
            return None

        if orientation == Qt.Orientation.Horizontal and 0 <= section < len(self.column_names):
            return self.column_names[section]
        return str(section + 1)

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole) -> Any:
        if role == Qt.ItemDataRole.DisplayRole or (
            role == Qt.ItemDataRole.EditRole and index.column() == 3
        ):
            return self.plugin_candidates[index.row()][index.column()]
        return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        item_flags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        if index.column() == 3:
            item_flags |= Qt.ItemFlag.ItemIsEditable
        return item_flags

    @cache
    def role_names(self) -> dict[int, bytes]:
        return {Qt.ItemDataRole.DisplayRole: b"display", Qt.ItemDataRole.EditRole: b"value"}


class LyricReplacementRulesTableModel(QAbstractTableModel):
    def __init__(self, preset: str) -> None:
        super().__init__()
        self.preset = preset
        self.column_keys = [
            "mode",
            "pattern_prefix",
            "pattern_main",
            "pattern_suffix",
            "replacement",
            "flags",
        ]
        self.column_names = [
            _("Mode"),
            _("Prefix"),
            _("Pattern"),
            _("Suffix"),
            _("Replacement"),
            _("Flags"),
            _("Actions"),
        ]

    def row_count(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(settings.lyric_replace_rules[self.preset])

    def column_count(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.column_names)

    def header_data(
        self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole
    ) -> Optional[str]:
        if role != Qt.ItemDataRole.DisplayRole:
            return None

        if orientation == Qt.Orientation.Horizontal and 0 <= section < len(self.column_names):
            return self.column_names[section]
        return str(section + 1)

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole) -> Any:
        column_index = index.column()
        if role in [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole] and (
            0 <= column_index < len(self.column_keys)
        ):
            prop = getattr(
                settings.lyric_replace_rules[self.preset][index.row()],
                self.column_keys[column_index],
            )
            return str(prop.name) if isinstance(prop, enum.Enum) else prop
        return ""

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        item_flags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        if index.column():
            item_flags |= Qt.ItemFlag.ItemIsEditable
        return item_flags

    @cache
    def role_names(self) -> dict[int, bytes]:
        return {Qt.ItemDataRole.DisplayRole: b"display", Qt.ItemDataRole.EditRole: b"value"}
