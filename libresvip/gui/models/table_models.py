import re
from typing import Any

from PySide6.QtCore import (
    QAbstractTableModel,
    QByteArray,
    QModelIndex,
    QPersistentModelIndex,
    Qt,
    Slot,
)

from __feature__ import snake_case, true_property  # isort:skip # noqa: F401

from libresvip.core.config import (
    LyricsReplacement,
    LyricsReplaceMode,
    settings,
)
from libresvip.extension.manager import plugin_manager

from . import AutoCaseObject


def _(text: str) -> str:
    return text


class PluginCadidatesTableModel(QAbstractTableModel, metaclass=AutoCaseObject):
    def __init__(self) -> None:
        super().__init__()
        self.column_names = [
            _("Applicable File Format"),
            _("Author"),
            _("Version"),
            "On/Off",
        ]
        self.plugin_candidates: list[dict[int, str]] = []
        self.reload_formats()

    def reload_formats(self) -> None:
        self.begin_remove_rows(QModelIndex(), 0, len(self.plugin_candidates) - 1)
        self.plugin_candidates.clear()
        self.end_remove_rows()
        self.begin_insert_rows(QModelIndex(), 0, len(plugin_manager.plugins.get("svs", {})) - 1)
        self.plugin_candidates = [
            *(
                {
                    0: plugin.info.file_format,
                    1: plugin.info.author,
                    2: plugin.version,
                    3: "checkbox-marked"
                    if plugin_id not in settings.disabled_plugins
                    else "checkbox-blank-outline",
                }
                for plugin_id, plugin in plugin_manager.plugins.get("svs", {}).items()
            ),
            *(
                {
                    0: plugin_id,
                    1: "?",
                    2: "?",
                    3: "checkbox-blank-outline",
                }
                for plugin_id in settings.disabled_plugins
            ),
        ]
        self.end_insert_rows()

    def row_count(self, parent: QModelIndex | QPersistentModelIndex = ...) -> int:  # type: ignore[assignment]
        return len(self.plugin_candidates)

    def column_count(self, parent: QModelIndex | QPersistentModelIndex = ...) -> int:  # type: ignore[assignment]
        return len(self.column_names)

    def header_data(
        self,
        section: int,
        orientation: Qt.Orientation,
        /,
        role: int = ...,  # type: ignore[assignment]
    ) -> str | None:
        if role != Qt.ItemDataRole.DisplayRole:
            return None

        if orientation == Qt.Orientation.Horizontal and 0 <= section < len(self.column_names):
            return self.column_names[section]
        return str(section + 1)

    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        /,
        role: int = ...,  # type: ignore[assignment]
    ) -> Any:
        if role == Qt.ItemDataRole.DisplayRole or (
            role == Qt.ItemDataRole.EditRole and index.column() == 3
        ):
            return self.plugin_candidates[index.row()][index.column()]
        return None

    def flags(self, index: QModelIndex | QPersistentModelIndex) -> Qt.ItemFlag:
        item_flags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        if index.column() == 3:
            item_flags |= Qt.ItemFlag.ItemIsEditable
        return item_flags

    def role_names(self) -> dict[int, QByteArray]:
        return {
            Qt.ItemDataRole.DisplayRole: QByteArray(b"display"),
            Qt.ItemDataRole.EditRole: QByteArray(b"value"),
        }


class LyricReplacementRulesTableModel(QAbstractTableModel, metaclass=AutoCaseObject):
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
            _("Case sensitive"),
            _("Actions"),
        ]

    def row_count(self, parent: QModelIndex | QPersistentModelIndex = ...) -> int:  # type: ignore[assignment]
        return len(settings.lyric_replace_rules[self.preset])

    def column_count(self, parent: QModelIndex | QPersistentModelIndex = ...) -> int:  # type: ignore[assignment]
        return len(self.column_names)

    def header_data(
        self,
        section: int,
        orientation: Qt.Orientation,
        /,
        role: int = ...,  # type: ignore[assignment]
    ) -> str | None:
        if role != Qt.ItemDataRole.DisplayRole:
            return None

        if orientation == Qt.Orientation.Horizontal and 0 <= section < len(self.column_names):
            return self.column_names[section]
        return str(section + 1)

    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        /,
        role: int = ...,  # type: ignore[assignment]
    ) -> Any:
        column_index = index.column()
        if role in [
            Qt.ItemDataRole.DisplayRole,
            Qt.ItemDataRole.EditRole,
        ] and 0 <= column_index < len(self.column_keys):
            prop = getattr(
                settings.lyric_replace_rules[self.preset][index.row()],
                self.column_keys[column_index],
            )
            if isinstance(prop, str):
                return prop
            elif isinstance(prop, re.RegexFlag):
                return prop.name
            elif isinstance(prop, LyricsReplaceMode):
                return prop.value
        return ""

    def set_data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        value: Any,
        /,
        role: int = ...,  # type: ignore[assignment]
    ) -> bool:
        key = self.column_keys[index.column()]
        row = index.row()
        rule = settings.lyric_replace_rules[self.preset][row]
        if key == "mode":
            return False
        elif key == "flags":
            flags = getattr(
                re.RegexFlag,
                "IGNORECASE" if value == "IGNORECASE" else "UNICODE",
            )
            setattr(rule, key, flags)
            value = flags.name
        else:
            setattr(rule, key, value)
        return True

    def flags(self, index: QModelIndex | QPersistentModelIndex) -> Qt.ItemFlag:
        item_flags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        column = index.column()
        if 0 < column < len(self.column_keys) and (column_key := self.column_keys[column]):
            editable = True
            if column_key in ["pattern_prefix", "pattern_suffix"]:
                row = index.row()
                if settings.lyric_replace_rules[self.preset][row].mode != LyricsReplaceMode.REGEX:
                    editable = False
            if editable:
                item_flags |= Qt.ItemFlag.ItemIsEditable
        return item_flags

    def role_names(self) -> dict[int, QByteArray]:
        return {
            Qt.ItemDataRole.DisplayRole: QByteArray(b"display"),
            Qt.ItemDataRole.EditRole: QByteArray(b"value"),
        }

    @Slot(str)
    def append(self, mode: str) -> None:
        settings.lyric_replace_rules[self.preset].append(
            LyricsReplacement(  # type: ignore[call-arg]
                mode=LyricsReplaceMode(mode), pattern_main="", replacement=""
            )
        )
        self.modelReset.emit()

    @Slot(int, int)
    def swap(self, old_index: int, new_index: int) -> None:
        if (
            not (0 <= old_index < len(settings.lyric_replace_rules[self.preset]))
            or not (0 <= new_index < len(settings.lyric_replace_rules[self.preset]))
            or (old_index + 1 != new_index)
        ):
            return
        self.begin_move_rows(QModelIndex(), old_index, old_index, QModelIndex(), new_index + 1)
        rule = settings.lyric_replace_rules[self.preset].pop(new_index)
        settings.lyric_replace_rules[self.preset].insert(old_index, rule)
        self.end_move_rows()

    @Slot(int)
    def delete(self, index: int) -> None:
        self.begin_remove_rows(QModelIndex(), index, index)
        settings.lyric_replace_rules[self.preset].pop(index)
        self.end_remove_rows()
