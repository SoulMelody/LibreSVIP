from __future__ import annotations

import dataclasses


@dataclasses.dataclass
class BaseTask:
    name: str | None = ""
    path: str | None = ""
    stem: str | None = ""
    ext: str | None = ""
    tmp_path: str | None = ""

    running: bool | None = False
    success: bool | None = None
    error: str | None = ""
    warning: str | None = ""
    child_tasks: list[BaseTask] = dataclasses.field(default_factory=list)
