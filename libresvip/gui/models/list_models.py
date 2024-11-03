from __future__ import annotations

from functools import cache
from typing import TYPE_CHECKING, Any, Optional, Union

from PySide6.QtCore import (
    QAbstractListModel,
    QModelIndex,
    QObject,
    QStringListModel,
    Slot,
)

from __feature__ import snake_case, true_property  # isort:skip # noqa: F401

from libresvip.core.config import settings

if TYPE_CHECKING:
    from collections.abc import Iterator

    Item = dict[str, Any]
    Items = list[Item]
    Role2Name = dict[int, str]
    Name2Role = dict[str, int]
    RoleNames = Union[dict[str, Any], tuple[str, ...], list[str]]  # suggested


class ModelProxy(QAbstractListModel):
    """
    references:
        https://github.com/likianta/qmlease/blob/master/qmlease/qmlside/model/model.py
        https://pyblish.gitbooks.io/developer-guide/content/qml_and_python_interoperability.html
        https://stackoverflow.com/questions/54687953/declaring-a-qabstractlistmodel-as-a-property-in-pyside2
    """

    _defaults: dict[str, Any]  # see also `self._auto_complete`
    _items: Items
    _name_2_role: Name2Role
    _role_2_name: Role2Name

    def __init__(self, role_names: RoleNames) -> None:
        super().__init__(None)
        self._name_2_role = {x: i for i, x in enumerate(role_names)}
        self._role_2_name = dict(enumerate(role_names))
        self._items = []
        if isinstance(role_names, dict):
            self._defaults = role_names
        else:
            # trick: set default value to '' instead of None to improve
            # compatibility.
            self._defaults = {x: "" for x in role_names}

    @property
    def _role_names(self) -> tuple[str, ...]:
        return tuple(self._name_2_role.keys())

    @property
    def items(self) -> Items:
        return self._items

    def __len__(self) -> int:
        return len(self._items)

    def __bool__(self) -> bool:
        return bool(self._items)

    def __getitem__(self, index: int) -> Item:
        return self._items[index]

    def __iter__(self) -> Iterator[Item]:
        return iter(self._items)

    # -------------------------------------------------------------------------
    # api
    # tip: all params which named `item` or `items` accept partial dict.

    @Slot(dict)
    def append(self, item: Item) -> None:
        self.begin_insert_rows(QModelIndex(), self.row_count(), self.row_count())
        self._items.append(self._auto_complete(item))
        self.end_insert_rows()

    @Slot(list)
    def append_many(self, items: Items) -> None:
        self.begin_insert_rows(QModelIndex(), self.row_count(), self.row_count() + len(items) - 1)
        self._items.extend(map(self._auto_complete, items))
        self.end_insert_rows()

    @Slot(int, dict)
    def insert(self, index: int, item: Item) -> None:
        self.begin_insert_rows(QModelIndex(), index, index)
        self._items.insert(index, self._auto_complete(item))
        self.end_insert_rows()

    @Slot(int, list)
    def insert_many(self, index: int, items: Items) -> None:
        self.begin_insert_rows(QModelIndex(), index, index + len(items) - 1)
        self._items[index:index] = list(map(self._auto_complete, items))
        self.end_insert_rows()

    @Slot(result="QVariant")
    def pop(self) -> Item:
        self.begin_remove_rows(QModelIndex(), len(self._items) - 1, len(self._items) - 1)
        out = self._items.pop(0)
        self.end_remove_rows()
        return out

    @Slot(int, result="QVariant")
    def pop_many(self, count: int) -> Items:
        assert count > 0
        self.begin_remove_rows(QModelIndex(), len(self._items) - count, len(self._items) - 1)
        a, b = self._items[:-count], self._items[-count:]
        self._items = a
        self.end_remove_rows()
        return b

    @Slot(int)
    def delete(self, index: int) -> None:
        self.begin_remove_rows(QModelIndex(), index, index)
        self._items.pop(index)
        self.end_remove_rows()

    @Slot(int, int)
    def delete_many(self, index: int, count: int) -> None:
        assert count > 0
        self.begin_remove_rows(QModelIndex(), index, index + count - 1)
        a, _ = (
            self._items[:index] + self._items[index + count :],
            self._items[index : index + count],
        )
        self._items = a
        self.end_remove_rows()

    @Slot(int, int)
    def move(self, old_index: int, new_index: int) -> None:
        self.begin_move_rows(QModelIndex(), old_index, old_index, QModelIndex(), new_index)
        item = self._items.pop(old_index)
        self._items.insert(new_index, item)
        self.end_move_rows()

    @Slot(int, int, int)
    def move_many(self, old_index: int, new_index: int, count: int) -> None:
        assert count > 0
        self.begin_move_rows(
            QModelIndex(),
            old_index,
            old_index + count - 1,
            QModelIndex(),
            new_index,
        )
        items = self._items[old_index : old_index + count]
        self._items[old_index : old_index + count] = []
        self._items[new_index:new_index] = items
        self.end_move_rows()

    @Slot(int, result=bool)
    def move_up(self, index: int) -> bool:
        if index > 0:
            self.move(index, index - 1)
            return True
        return False

    @Slot(int, result=bool)
    def move_down(self, index: int) -> bool:
        if index < len(self._items) - 1:
            self.move(index, index + 1)
            return True
        return False

    @Slot()
    def clear(self) -> None:
        self.begin_remove_rows(QModelIndex(), 0, len(self._items) - 1)
        self._items.clear()
        self.end_remove_rows()

    @Slot(int, result="QVariant")
    def get(self, index: int) -> Item:
        return self._items[index]

    @Slot(int, result="QVariant")
    @Slot(int, int, result="QVariant")
    def get_many(
        self,
        start: Optional[int] = None,
        end: Optional[int] = None,  # TODO: shall we use `count` instead?
    ) -> Items:
        if start is not None and end is None:
            start, end = 0, start
        else:
            assert start is not None
            assert end is not None
        return self._items[start:end]

    @Slot(int, dict)
    def update(self, index: int, item: Item) -> None:
        self._items[index].update(item)
        # emit signal of `self.dataChanged` to notify qml side that some item
        # has been changed.
        # `dataChanged.emit` accepts two arguments:
        #   dataChanged.emit(QModelIndex start, QModelIndex end)
        # how to create QModelIndex instance: use `self.createIndex(row, col)`.
        # ref: https://blog.csdn.net/LaoYuanPython/article/details/102011031
        qindex = self.create_index(index, 0)
        self.dataChanged.emit(qindex, qindex, [self._name_2_role[x] for x in item])

    @Slot(int, list)
    def update_many(self, start: int, items: Items) -> None:
        if not items:
            return
        end = start + len(items)
        for old, new in zip(self._items[start:end], items):
            old.update(new)
        qindex_start = self.create_index(start, 0)
        qindex_end = self.create_index(end - 1, 0)
        self.dataChanged.emit(qindex_start, qindex_end)

    def _auto_complete(self, item: Item) -> Item:
        for k, v in self._defaults.items():
            if k not in item:
                item[k] = v
        return item

    # -------------------------------------------------------------------------
    # overrides

    def data(self, index: QModelIndex, role: int) -> Any:
        name = self._role_2_name[role]
        return self._items[index.row()].get(name, "")

    def set_data(self, index: QModelIndex, value: Any, role: int) -> bool:
        name = self._role_names[role]
        self._items[index.row()][name] = value
        self.dataChanged.emit(index, index)
        return True

    def row_count(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._items)

    @cache
    def role_names(self) -> dict[int, bytes]:
        # return self._role_2_name
        return {k: v.encode("utf-8") for k, v in self._role_2_name.items()}


class LyricReplacementPresetsModel(QStringListModel):
    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self.set_string_list(list(settings.lyric_replace_rules))

    @Slot(str)
    def append(self, value: str) -> None:
        settings.lyric_replace_rules.setdefault(value, [])
        self.set_string_list(list(settings.lyric_replace_rules))

    @Slot(str)
    def remove(self, value: str) -> None:
        settings.lyric_replace_rules.pop(value, None)
        self.set_string_list(list(settings.lyric_replace_rules))
