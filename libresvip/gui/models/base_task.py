from __future__ import annotations

import dataclasses
from typing import Optional


@dataclasses.dataclass
class BaseTask:
    name: Optional[str] = ""
    path: Optional[str] = ""
    stem: Optional[str] = ""
    ext: Optional[str] = ""
    tmp_path: Optional[str] = ""

    running: Optional[bool] = False
    success: Optional[bool] = None
    error: Optional[str] = ""
    warning: Optional[str] = ""
    child_tasks: list[BaseTask] = dataclasses.field(default_factory=list)
    parent: Optional[BaseTask] = None

    def add_child(self, child: BaseTask) -> None:
        child.parent = self
        self.child_tasks.append(child)
