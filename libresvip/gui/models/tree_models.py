import json
from typing import Any, Optional

from PySide6.QtCore import QAbstractItemModel, QModelIndex, QObject, Qt

from __feature__ import snake_case, true_property  # isort:skip # noqa: F401

from libresvip.gui.models.base_task import BaseTask


class TasksTreeModel(QAbstractItemModel):
    name_role: int = Qt.ItemDataRole.UserRole + 1
    path_role: int = Qt.ItemDataRole.UserRole + 2
    stem_role: int = Qt.ItemDataRole.UserRole + 3
    ext_role: int = Qt.ItemDataRole.UserRole + 4
    running_role: int = Qt.ItemDataRole.UserRole + 5

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self.root = BaseTask()
        root_task = BaseTask(name="Export")
        self.root.add_child(root_task)
        self.main_index = self.index(0, 0, QModelIndex())

    def role_names(self) -> dict[int, bytes]:
        return {
            self.name_role: b"name",
            self.path_role: b"path",
            self.stem_role: b"stem",
            self.ext_role: b"ext",
            self.running_role: b"running",
            Qt.ItemDataRole.DisplayRole: b"display",
        }

    def get_item(self, index: QModelIndex) -> BaseTask:
        if index.is_valid() and (item := index.internal_pointer()):
            return item

        return self.root

    def index(self, row: int, column: int, parent: QModelIndex) -> QModelIndex:
        if not self.has_index(row, column, parent):
            return QModelIndex()

        parent_item = self.get_item(parent)
        child_item = parent_item.child_tasks[row]

        return self.create_index(row, column, child_item) if child_item else QModelIndex()

    def row_count(self, parent: QModelIndex = QModelIndex()) -> int:
        parent_item = parent.internal_pointer() if parent.is_valid() else self.root

        return len(parent_item.child_tasks)

    def column_count(self, index: QModelIndex = QModelIndex()) -> int:
        return 5

    def data(
        self, index: QModelIndex, role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole
    ) -> Optional[Any]:
        if not index.is_valid():
            return None

        item = index.internal_pointer()
        if item.parent is None or not 0 <= index.row() < len(item.parent.child_tasks):
            return None

        if role == self.name_role:
            return item.name
        elif role == self.path_role:
            return item.path
        elif role == self.stem_role:
            return item.stem
        elif role == self.ext_role:
            return item.ext
        elif role == self.running_role:
            return json.dumps(item.running)

        return None

    def header_data(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole,
    ) -> Optional[str]:
        if role != Qt.ItemDataRole.DisplayRole:
            return None

        if orientation == Qt.Orientation.Horizontal:
            return {
                0: "Name",
                1: "Path",
                2: "Stem",
                3: "Ext",
                4: "Running",
            }[section]

        return None

    def append_many(self, items: list[BaseTask]) -> None:
        root_task = self.main_index.internal_pointer()
        row = len(root_task.child_tasks)
        count = len(items)
        super().begin_insert_rows(self.main_index, row, row + count - 1)
        for item in items:
            root_task.add_child(item)
        super().end_insert_rows()

    def remove_rows(self, row: int, count: int, parent: QModelIndex = QModelIndex()) -> bool:
        return True

    def set_data(
        self, index: QModelIndex, value: Any, role: Qt.ItemDataRole = Qt.ItemDataRole.EditRole
    ) -> bool:
        return False

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable

    def parent(self, index: QModelIndex) -> QModelIndex:
        item = self.get_item(index)
        parent_item = item.parent

        if parent_item is None or parent_item == self.root:
            return QModelIndex()

        return self.create_index(parent_item.child_tasks.index(item), 0, parent_item)
