from __future__ import annotations

import contextlib
import dataclasses
import enum
import pathlib
import traceback
from typing import Any, get_args, get_type_hints

import more_itertools
from loguru import logger
from pydantic_core import PydanticUndefined
from pydantic_extra_types.color import Color
from PySide6.QtCore import (
    Property,
    QAbstractListModel,
    QModelIndex,
    QObject,
    QRunnable,
    Qt,
    QThreadPool,
    QTimer,
    Signal,
    Slot,
)
from upath import UPath

from libresvip.extension.vendor import pluginlib

from __feature__ import snake_case, true_property  # isort:skip # noqa: F401

from libresvip.core.config import ConversionMode, get_ui_settings, settings
from libresvip.core.warning_types import CatchWarnings
from libresvip.extension.base import ReadOnlyConverterMixin, WriteOnlyConverterMixin
from libresvip.extension.manager import middleware_manager, plugin_manager
from libresvip.gui.models.base_task import BaseTask
from libresvip.gui.models.list_models import ModelProxy
from libresvip.gui.models.table_models import PluginCadidatesTableModel
from libresvip.model.base import BaseComplexModel, BaseModel, Project
from libresvip.utils.text import supported_charset_names, uuid_str

from .url_opener import open_path

readonly_plugin_ids = [
    identifier
    for identifier, plugin in plugin_manager.plugins.get("svs", {}).items()
    if issubclass(plugin, ReadOnlyConverterMixin)
]
writeonly_plugin_ids = [
    identifier
    for identifier, plugin in plugin_manager.plugins.get("svs", {}).items()
    if issubclass(plugin, WriteOnlyConverterMixin)
]


class ConversionWorkerSignals(QObject):
    result = Signal(int, dict)


class ConversionWorker(QRunnable):
    def __init__(
        self,
        index: int,
        input_path: str,
        output_path: str,
        input_format: str,
        output_format: str,
        input_options: dict[str, Any],
        output_options: dict[str, Any],
        middleware_options: dict[str, dict[str, Any]],
    ) -> None:
        super().__init__()
        self.index = index
        self.input_path = input_path
        self.output_path = output_path
        self.input_format = input_format
        self.output_format = output_format
        self.input_options = input_options
        self.output_options = output_options
        self.middleware_options = middleware_options
        self.signals = ConversionWorkerSignals()

    @Slot()
    def run(self) -> None:
        result_kwargs: dict[str, Any] = {"running": False}
        try:
            with CatchWarnings() as w:
                input_plugin = plugin_manager.plugins.get("svs", {})[self.input_format]
                output_plugin = plugin_manager.plugins.get("svs", {})[self.output_format]
                project = input_plugin.load(
                    pathlib.Path(self.input_path),
                    self.input_options,
                )
                for (
                    middleware_abbr,
                    middleware_option,
                ) in self.middleware_options.items():
                    middleware = middleware_manager.plugins.get("middleware", {})[middleware_abbr]
                    project = middleware.process(
                        project,
                        middleware_option,
                    )
                output_plugin.dump(
                    UPath(self.output_path),
                    project,
                    self.output_options,
                )
                result_kwargs |= {
                    "success": True,
                    "tmp_path": self.output_path,
                }
            if w.output:
                result_kwargs["warning"] = w.output
            self.signals.result.emit(self.index, result_kwargs)
        except Exception:
            result_kwargs |= {
                "success": False,
                "error": traceback.format_exc(),
            }
            with contextlib.suppress(RuntimeError):
                self.signals.result.emit(self.index, result_kwargs)


class SplitWorker(QRunnable):
    def __init__(
        self,
        index: int,
        input_path: str,
        output_dir: str,
        input_format: str,
        output_format: str,
        input_options: dict[str, Any],
        output_options: dict[str, Any],
        middleware_options: dict[str, dict[str, Any]],
    ) -> None:
        super().__init__()
        self.index = index
        self.input_path = input_path
        self.output_dir = output_dir
        UPath(self.output_dir).mkdir(parents=True, exist_ok=True)
        self.input_format = input_format
        self.output_format = output_format
        self.input_options = input_options
        self.output_options = output_options
        self.middleware_options = middleware_options
        self.signals = ConversionWorkerSignals()

    @Slot()
    def run(self) -> None:
        result_kwargs: dict[str, Any] = {"running": False}
        try:
            with CatchWarnings() as w:
                input_plugin = plugin_manager.plugins.get("svs", {})[self.input_format]
                output_plugin = plugin_manager.plugins.get("svs", {})[self.output_format]
                project = input_plugin.load(
                    pathlib.Path(self.input_path),
                    self.input_options,
                )
                for (
                    middleware_abbr,
                    middleware_option,
                ) in self.middleware_options.items():
                    middleware = middleware_manager.plugins.get("middleware", {})[middleware_abbr]
                    project = middleware.process(
                        project,
                        middleware_option,
                    )
                for child_project in project.split_tracks(settings.max_track_count):
                    output_plugin.dump(
                        UPath(self.output_dir) / uuid_str(),
                        child_project,
                        self.output_options,
                    )
                result_kwargs |= {
                    "success": True,
                    "tmp_path": self.output_dir,
                }
            if w.output:
                result_kwargs["warning"] = w.output
            self.signals.result.emit(self.index, result_kwargs)
        except Exception:
            result_kwargs |= {
                "success": False,
                "error": traceback.format_exc(),
            }
            with contextlib.suppress(RuntimeError):
                self.signals.result.emit(self.index, result_kwargs)


class MergeWorker(QRunnable):
    def __init__(
        self,
        index: int,
        input_paths: list[str],
        output_path: str,
        input_format: str,
        output_format: str,
        input_options: dict[str, Any],
        output_options: dict[str, Any],
        middleware_options: dict[str, dict[str, Any]],
    ) -> None:
        super().__init__()
        self.index = index
        self.input_paths = input_paths
        self.output_path = output_path
        self.input_format = input_format
        self.output_format = output_format
        self.input_options = input_options
        self.output_options = output_options
        self.middleware_options = middleware_options
        self.signals = ConversionWorkerSignals()

    @Slot()
    def run(self) -> None:
        result_kwargs: dict[str, Any] = {"running": False}
        try:
            with CatchWarnings() as w:
                input_plugin = plugin_manager.plugins.get("svs", {})[self.input_format]
                output_plugin = plugin_manager.plugins.get("svs", {})[self.output_format]
                child_projects = [
                    input_plugin.load(
                        pathlib.Path(input_path),
                        self.input_options,
                    )
                    for input_path in self.input_paths
                ]
                project = Project.merge_projects(child_projects)
                for (
                    middleware_abbr,
                    middleware_option,
                ) in self.middleware_options.items():
                    middleware = middleware_manager.plugins.get("middleware", {})[middleware_abbr]
                    project = middleware.process(
                        project,
                        middleware_option,
                    )
                output_plugin.dump(
                    UPath(self.output_path),
                    project,
                    self.output_options,
                )
                result_kwargs |= {
                    "success": True,
                    "tmp_path": self.output_path,
                }
            if w.output:
                result_kwargs["warning"] = w.output
            self.signals.result.emit(self.index, result_kwargs)
        except Exception:
            result_kwargs |= {
                "success": False,
                "error": traceback.format_exc(),
            }
            with contextlib.suppress(RuntimeError):
                self.signals.result.emit(self.index, result_kwargs)


class TaskManager(QObject):
    conversion_mode_changed = Signal(str)
    input_format_changed = Signal(str)
    output_format_changed = Signal(str)
    input_fields_changed = Signal()
    output_fields_changed = Signal()
    task_count_changed = Signal(int)
    busy_changed = Signal(bool)
    middleware_options_updated = Signal()
    _start_conversion = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent=parent)
        self._conversion_mode = ConversionMode.DIRECT
        self.tasks = ModelProxy(dataclasses.asdict(BaseTask()))
        self.tasks.rowsInserted.connect(self._on_tasks_changed)
        self.tasks.rowsRemoved.connect(self._on_tasks_changed)
        self.input_formats = ModelProxy({"value": "", "text": ""})
        self.output_formats = ModelProxy({"value": "", "text": ""})
        self.input_fields = ModelProxy(
            {
                "index": 0,
                "name": "",
                "title": "",
                "description": "",
                "default": "",
                "type": "",
                "value": "",
                "choices": [],
            }
        )
        self._input_fields_inited = False
        self.output_fields = ModelProxy(
            {
                "index": 0,
                "name": "",
                "title": "",
                "description": "",
                "default": "",
                "type": "",
                "value": "",
                "choices": [],
            }
        )
        self._output_fields_inited = False
        self.middleware_states = ModelProxy(
            {
                "index": 0,
                "identifier": "",
                "name": "",
                "description": "",
                "value": False,
            }
        )
        self.middleware_fields: dict[str, ModelProxy] = {}
        self.init_middleware_options()
        self.reload_formats()
        self.input_format_changed.connect(self.set_input_fields)
        self.output_format_changed.connect(self.set_output_fields)
        self.output_format_changed.connect(self.reset_output_ext)
        self._start_conversion.connect(self.start)
        self.timer = QTimer()
        self.timer.interval = 100
        self.timer.timeout.connect(self.check_busy)
        self.tasks.rowsAboutToBeRemoved.connect(self.delete_tmp_file)
        self.plugin_candidates = PluginCadidatesTableModel()

    @property
    def thread_pool(self) -> QThreadPool:
        return QThreadPool.global_instance()

    @Slot(int)
    def toggle_plugin(self, index: int) -> None:
        plugin_ids = list(plugin_manager.plugins.get("svs", {}))
        if index < len(plugin_ids):
            key = plugin_ids[index]
        else:
            key = self.plugin_candidates.plugin_candidates[index][0]
        if key in plugin_manager.plugins.get("svs", {}) and key not in settings.disabled_plugins:
            settings.disabled_plugins.append(key)
        elif key in settings.disabled_plugins:
            settings.disabled_plugins.remove(key)
        else:
            return
        plugin_manager.blacklist = [
            pluginlib.BlacklistEntry("svs", each) for each in settings.disabled_plugins
        ]
        self.plugin_candidates.reload_formats()
        self.reload_formats()

    def _on_tasks_changed(self, index: QModelIndex, start: int, end: int) -> None:
        self.task_count_changed.emit(len(self.tasks))

    def get_conversion_mode(self) -> str:
        return self._conversion_mode.value

    def set_conversion_mode(self, mode: str) -> None:
        self._conversion_mode = ConversionMode(mode)
        self.conversion_mode_changed.emit(mode)
        for i, task in enumerate(self.tasks):
            if task["success"] is False or self.delete_tmp_file(QModelIndex(), i, i):
                self.tasks.update(
                    i,
                    {
                        "tmp_path": "",
                        "running": False,
                        "success": None,
                        "error": "",
                        "warning": "",
                    },
                )

    conversion_mode = Property(
        str,
        get_conversion_mode,
        set_conversion_mode,
        notify=conversion_mode_changed,
    )

    @Property(int, notify=task_count_changed)
    def count(self) -> int:
        return len(self.tasks)

    def init_middleware_options(self) -> None:
        for middleware_id, middleware in middleware_manager.plugins.get("middleware", {}).items():
            self.middleware_states.append(
                {
                    "index": len(self.middleware_states),
                    "identifier": middleware_id,
                    "name": middleware.info.name,
                    "description": middleware.info.description,
                    "value": False,
                }
            )
            self.middleware_fields[middleware_id] = ModelProxy(
                {
                    "name": "",
                    "title": "",
                    "description": "",
                    "default": "",
                    "type": "",
                    "value": "",
                    "choices": [],
                }
            )
        self.reload_middleware_options()
        self.middleware_options_updated.connect(self.reload_middleware_options)

    def reload_middleware_options(self) -> None:
        for middleware_id, middleware_cls in middleware_manager.plugins.get(
            "middleware", {}
        ).items():
            option_class = middleware_cls.process_option_cls
            self.middleware_fields[middleware_id].clear()
            middleware_fields = self.inspect_fields(option_class)
            self.middleware_fields[middleware_id].append_many(middleware_fields)

    @Slot(result=None)
    def reload_formats(self) -> None:
        self.input_formats.clear()
        self.input_formats.append_many(
            [
                {
                    "text": plugin.info.file_format,
                    "value": plugin.info.suffix,
                }
                for plugin_id, plugin in plugin_manager.plugins.get("svs", {}).items()
                if plugin_id not in writeonly_plugin_ids
            ],
        )
        self.input_format_changed.emit("")
        self.output_formats.clear()
        self.output_formats.append_many(
            [
                {
                    "text": plugin.info.file_format,
                    "value": plugin.info.suffix,
                }
                for plugin_id, plugin in plugin_manager.plugins.get("svs", {}).items()
                if plugin_id not in readonly_plugin_ids
            ],
        )
        self.output_format_changed.emit("")

    def delete_tmp_file(self, index: QModelIndex, start: int, end: int) -> bool:
        deleted = False
        for i in range(start, end + 1):
            path = UPath(self.tasks[i]["tmp_path"])
            if path.exists():
                with contextlib.suppress(Exception):
                    if path.is_dir():
                        path.rmdir()
                    else:
                        path.unlink()
                deleted = True
        return deleted

    @property
    def input_format(self) -> str | None:
        return settings.last_input_format

    @input_format.setter
    def input_format(self, value: str | None) -> None:
        if value is not None:
            settings.last_input_format = value

    @property
    def output_format(self) -> str | None:
        return settings.last_output_format

    @output_format.setter
    def output_format(self, value: str | None) -> None:
        if value is not None:
            settings.last_output_format = value

    @Slot(result=bool)
    def start_conversion(self) -> bool:
        if self.busy:
            return False
        self._start_conversion.emit()
        return True

    @property
    def output_ext(self) -> str:
        if settings.auto_set_output_extension and self.output_format:
            return f".{self.output_format}"
        return ""

    @Slot(str)
    def reset_output_ext(self, value: str) -> None:
        self.tasks.update_many(0, [{"ext": self.output_ext}] * len(self.tasks))

    @staticmethod
    def output_dir(task: dict[str, Any]) -> pathlib.Path:
        return (
            settings.save_folder
            if settings.save_folder.is_absolute()
            else pathlib.Path(task["path"]).parent / str(settings.save_folder)
        )

    def output_path(self, task: dict[str, Any]) -> pathlib.Path:
        output_dir = self.output_dir(task)
        if self._conversion_mode == ConversionMode.SPLIT:
            return output_dir / f"{task['stem']}_**{self.output_ext}"
        return output_dir / f"{task['stem']}{self.output_ext}"

    @Slot(int, result=str)
    def get_output_path(self, index: int) -> str:
        task = self.tasks[index]
        return str(self.output_path(task))

    @Slot(int, result=bool)
    def open_output_dir(self, index: int) -> bool:
        task = self.tasks[index]
        open_path(self.output_dir(task))
        return True

    @Slot(int, result=bool)
    def open_output_path(self, index: int) -> bool:
        task = self.tasks[index]
        open_path(self.output_path(task))
        return True

    @Slot(int, result=bool)
    def output_path_exists(self, index: int) -> bool:
        task = self.tasks[index]
        if self._conversion_mode != ConversionMode.SPLIT:
            return self.output_path(task).exists()
        output_dir = self.output_dir(task)
        tmp_path = UPath(task["tmp_path"])
        return any(
            target_path.exists()
            for i in range(more_itertools.ilen(tmp_path.iterdir()))
            if (target_path := output_dir / f"{task['stem']}_{i + 1:0=2d}{self.output_ext}")
        )

    @Slot(int, result=bool)
    def move_to_output(self, index: int) -> bool:
        task = self.tasks[index]
        if not task["success"]:
            return False
        output_dir = self.output_dir(task)
        tmp_path = UPath(task["tmp_path"])
        result = False
        try:
            if tmp_path.exists():
                if tmp_path.is_dir():
                    for i, child_file in enumerate(tmp_path.iterdir()):
                        if not child_file.is_file():
                            continue
                        target_path = output_dir / f"{task['stem']}_{i + 1:0=2d}{self.output_ext}"
                        if target_path.exists():
                            target_path.unlink()
                        target_path.write_bytes(child_file.read_bytes())
                else:
                    target_path = output_dir / f"{task['stem']}{self.output_ext}"
                    if target_path.exists():
                        target_path.unlink()
                    target_path.write_bytes(tmp_path.read_bytes())
                result = True
        except OSError as e:
            self.tasks.update(index, {"error": str(e)})
        return result

    @staticmethod
    def inspect_fields(option_class: type[BaseModel]) -> list[dict[str, Any]]:
        fields = []
        for i, (option_key, field_info) in enumerate(option_class.model_fields.items()):
            default_value = None if field_info.default is PydanticUndefined else field_info.default
            if issubclass(field_info.annotation, bool):
                fields.append(
                    {
                        "index": i,
                        "type": "bool",
                        "name": option_key,
                        "title": field_info.title,
                        "description": field_info.description or "",
                        "default": default_value,
                        "value": default_value,
                    }
                )
            elif issubclass(field_info.annotation, enum.Enum):
                if default_value is not None:
                    default_value = default_value.value
                type_hints = get_type_hints(field_info.annotation, include_extras=True)
                annotations = None
                if "_value_" in type_hints:
                    value_args = get_args(type_hints["_value_"])
                    if len(value_args) >= 2:
                        model = value_args[1]
                        if hasattr(model, "model_fields"):
                            annotations = model.model_fields
                if annotations is None:
                    continue
                choices = []
                for enum_item in field_info.annotation:
                    if enum_item.name in annotations:
                        enum_field = annotations[enum_item.name]
                        choices.append(
                            {
                                "value": enum_item.value,
                                "text": enum_field.title,
                                "desc": enum_field.description or "",
                            }
                        )
                    else:
                        logger.warning(enum_item.name)
                fields.append(
                    {
                        "index": i,
                        "type": "enum",
                        "name": option_key,
                        "title": field_info.title,
                        "description": field_info.description or "",
                        "default": default_value,
                        "value": default_value,
                        "choices": choices,
                    }
                )
            elif option_key == "lyric_replacement_preset_name":
                choices = [
                    {
                        "value": preset,
                        "text": preset,
                        "desc": "",
                    }
                    for preset in get_ui_settings().lyric_replace_rules
                ]
                fields.append(
                    {
                        "index": i,
                        "type": "enum",
                        "name": option_key,
                        "title": field_info.title,
                        "description": field_info.description or "",
                        "default": default_value,
                        "value": default_value,
                        "choices": choices,
                    }
                )
            elif option_key in ["encoding", "lyric_encoding"]:
                choices = [
                    {
                        "value": preset,
                        "text": preset,
                        "desc": "",
                    }
                    for preset in supported_charset_names()
                ]
                fields.append(
                    {
                        "index": i,
                        "type": "enum",
                        "name": option_key,
                        "title": field_info.title,
                        "description": field_info.description or "",
                        "default": default_value,
                        "value": default_value,
                        "choices": choices,
                    }
                )
            elif issubclass(
                field_info.annotation,
                str | int | float | Color | BaseComplexModel,
            ):
                if issubclass(field_info.annotation, BaseComplexModel):
                    default_value = field_info.annotation.default_repr()
                fields.append(
                    {
                        "index": i,
                        "type": "color"
                        if issubclass(field_info.annotation, Color)
                        else field_info.annotation.__name__,
                        "name": option_key,
                        "title": field_info.title,
                        "description": field_info.description or "",
                        "default": default_value,
                        "value": default_value,
                    }
                )
        return fields

    @Slot(str)
    def set_input_fields(self, input_format: str) -> None:
        if input_format == self.input_format and self._input_fields_inited:
            return
        if input_format:
            self.input_format = input_format
            self.input_fields.clear()
            plugin_input = plugin_manager.plugins.get("svs", {})[self.input_format]
            input_fields = self.inspect_fields(plugin_input.input_option_cls)
            self.input_fields.append_many(input_fields)
            if not self._input_fields_inited:
                self._input_fields_inited = True
            self.input_fields_changed.emit()

    @Slot(str)
    def set_output_fields(self, output_format: str) -> None:
        if output_format == self.output_format and self._output_fields_inited:
            return
        if output_format:
            self.output_format = output_format
            self.output_fields.clear()
            plugin_output = plugin_manager.plugins.get("svs", {})[self.output_format]
            output_fields = self.inspect_fields(plugin_output.output_option_cls)
            self.output_fields.append_many(output_fields)
            if not self._output_fields_inited:
                self._output_fields_inited = True
            self.output_fields_changed.emit()

    @Slot(str, result="QVariant")
    def plugin_info(self, name: str) -> dict[str, str]:
        assert name in {"input_format", "output_format"}
        if (suffix := getattr(self, name)) in plugin_manager.plugins.get("svs", {}):
            plugin = plugin_manager.plugins.get("svs", {})[suffix]
            return {
                "name": plugin.info.name,
                "author": plugin.info.author,
                "website": plugin.info.website,
                "description": plugin.info.description,
                "version": plugin.version,
                "file_format": plugin.info.file_format,
                "suffix": f"(*.{plugin.info.suffix})",
                "icon_base64": f"data:image/png;base64,{plugin.info.icon_base64}",
            }
        return {
            "name": "",
            "author": "",
            "website": "",
            "description": "",
            "version": "",
            "file_format": "",
            "suffix": "(*.*)",
            "icon_base64": "",
        }

    @Slot()
    def reset_stems(self) -> None:
        for i, task in enumerate(self.tasks):
            self.tasks.update(i, {"stem": pathlib.Path(task["path"]).stem})

    @Slot(list)
    def add_task_paths(self, paths: list[str]) -> None:
        tasks = []
        path_obj = None
        for path in paths:
            path_obj = pathlib.Path(path)
            tasks.append(
                BaseTask(
                    path=path,
                    name=path_obj.name,
                    stem=path_obj.stem,
                    ext=self.output_ext,
                    success=None,
                )
            )
        self.tasks.append_many([dataclasses.asdict(task) for task in tasks])
        if (
            settings.auto_detect_input_format
            and path_obj is not None
            and (suffix := path_obj.suffix[1:]) in plugin_manager.plugins.get("svs", {})
        ):
            self.set_str("input_format", suffix)

    @Slot(str, result=QAbstractListModel)
    def qget(self, name: str) -> Any:
        return getattr(self, name)

    @Slot(str, result=QAbstractListModel)
    def get_middleware_fields(self, name: str) -> Any:
        return self.middleware_fields[name]

    @Slot(str, result=str)
    def get_str(self, name: str) -> str:
        assert name in {"input_format", "output_format"}
        return getattr(self, name)

    @Slot(str, str)
    def set_str(self, name: str, value: str) -> None:
        assert name in {"input_format", "output_format"}
        if (
            name == "input_format"
            and settings.reset_tasks_on_input_change
            and value != self.input_format
            and (
                delete_len := more_itertools.ilen(
                    more_itertools.rstrip(
                        self.tasks,
                        lambda task: task["path"].lower().endswith(f".{value}"),
                    )
                )
            )
        ):
            self.tasks.delete_many(0, delete_len)
        getattr(self, f"{name}_changed").emit(value)

    @Slot()
    def check_busy(self) -> None:
        if self.busy:
            return
        self.set_busy(False)
        if self.timer.active:
            self.timer.stop()
            if settings.open_save_folder_on_completion:
                success_task = next(
                    (
                        task
                        for i, task in enumerate(self.tasks)
                        if task["success"] and not self.output_path_exists(i)
                    ),
                    None,
                )
                if success_task is not None:
                    output_dir = self.output_dir(success_task)
                    open_path(output_dir)

    def set_busy(self, busy: bool) -> None:
        self.busy_changed.emit(busy)

    @Property(bool, notify=busy_changed)
    def busy(self) -> bool:
        return self.thread_pool.active_thread_count > 0

    @Slot()
    def start(self) -> None:
        if self.input_format is None or self.output_format is None:
            error_message = "Please select input and output formats first."
            for i in range(len(self.tasks)):
                self.tasks.update(
                    i,
                    {"success": False, "error": error_message, "warning": ""},
                )
            return
        input_options = {field["name"]: field["value"] for field in self.input_fields}
        output_options = {field["name"]: field["value"] for field in self.output_fields}
        middleware_options = {
            middleware_state["identifier"]: {
                field["name"]: field["value"]
                for field in self.middleware_fields[middleware_state["identifier"]]
            }
            for middleware_state in self.middleware_states
            if middleware_state["value"]
        }
        for i in range(len(self.tasks)):
            self.tasks.update(i, {"success": False, "error": "", "warning": ""})
        self.thread_pool.max_thread_count = (
            max(len(self.tasks), 4) if settings.multi_threaded_conversion else 1
        )
        if self._conversion_mode == ConversionMode.DIRECT:
            for i in range(len(self.tasks)):
                input_path = self.tasks[i]["path"]
                output_path = f"memory:/{uuid_str()}"
                worker = ConversionWorker(
                    i,
                    input_path,
                    output_path,
                    self.input_format,
                    self.output_format,
                    input_options,
                    output_options,
                    middleware_options,
                )
                worker.signals.result.connect(
                    self.tasks.update,
                    type=Qt.ConnectionType.BlockingQueuedConnection,
                )
                self.tasks.update(
                    i,
                    {
                        "running": True,
                        "success": None,
                        "error": None,
                        "warning": None,
                    },
                )
                self.thread_pool.start(worker)
                if not i:
                    self.set_busy(True)
        elif self._conversion_mode == ConversionMode.SPLIT:
            for i in range(len(self.tasks)):
                input_path = self.tasks[i]["path"]
                output_dir = f"memory:/{uuid_str()}"
                worker = SplitWorker(
                    i,
                    input_path,
                    output_dir,
                    self.input_format,
                    self.output_format,
                    input_options,
                    output_options,
                    middleware_options,
                )
                worker.signals.result.connect(
                    self.tasks.update,
                    type=Qt.ConnectionType.BlockingQueuedConnection,
                )
                self.tasks.update(
                    i,
                    {
                        "running": True,
                        "success": None,
                        "error": None,
                        "warning": None,
                    },
                )
                self.thread_pool.start(worker)
                if not i:
                    self.set_busy(True)
        elif self._conversion_mode == ConversionMode.MERGE and len(self.tasks):
            input_paths = [task["path"] for task in self.tasks]
            output_path = f"memory:/{uuid_str()}"
            worker = MergeWorker(
                0,
                input_paths,
                output_path,
                self.input_format,
                self.output_format,
                input_options,
                output_options,
                middleware_options,
            )
            worker.signals.result.connect(
                self.tasks.update,
                type=Qt.ConnectionType.BlockingQueuedConnection,
            )
            self.tasks.update(
                0,
                {
                    "running": True,
                    "success": None,
                    "error": None,
                    "warning": None,
                },
            )
            self.thread_pool.start(worker)
            self.set_busy(True)
        self.timer.start()
