import contextlib
import enum
import pathlib
import traceback
import uuid
import warnings
import zipfile
from typing import Any, Optional, get_args, get_type_hints

import more_itertools
from loguru import logger
from pydantic.warnings import PydanticDeprecationWarning
from pydantic_core import PydanticUndefined
from pydantic_extra_types.color import Color
from PySide6.QtCore import (
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
from PySide6.QtQml import QmlElement, QmlSingleton
from upath import UPath

from __feature__ import snake_case, true_property  # isort:skip # noqa: F401  # type: ignore[import-not-found,reportMissingImports]

from libresvip.core.config import settings
from libresvip.core.warning_types import BaseWarning
from libresvip.extension.manager import plugin_manager
from libresvip.model.base import BaseComplexModel, BaseModel

from .url_opener import open_path
from .vendor.model_proxy import ModelProxy

QML_IMPORT_NAME = "LibreSVIP"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


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
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent=parent)
        self.index = index
        self.input_path = input_path
        self.output_path = output_path
        self.input_format = input_format
        self.output_format = output_format
        self.input_options = input_options
        self.output_options = output_options
        self.signals = ConversionWorkerSignals()

    @Slot()
    def run(self) -> None:
        try:
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always", BaseWarning)
                warnings.filterwarnings("ignore", category=PydanticDeprecationWarning)
                input_plugin = plugin_manager.plugin_registry[self.input_format]
                output_plugin = plugin_manager.plugin_registry[self.output_format]
                if (
                    input_plugin.plugin_object is None
                    or (
                        input_option := get_type_hints(input_plugin.plugin_object.load).get(
                            "options",
                        )
                    )
                    is None
                    or output_plugin.plugin_object is None
                    or (
                        output_option := get_type_hints(
                            output_plugin.plugin_object.dump,
                        ).get("options")
                    )
                    is None
                ):
                    self.signals.result.emit(
                        self.index,
                        {
                            "success": False,
                            "error": "Invalid options",
                        },
                    )
                else:
                    project = input_plugin.plugin_object.load(
                        pathlib.Path(self.input_path),
                        input_option(**self.input_options),
                    )
                    output_plugin.plugin_object.dump(
                        UPath(self.output_path),
                        project,
                        output_option(**self.output_options),
                    )
                    warning_str = "\n".join(str(each.message) for each in w)
                    self.signals.result.emit(
                        self.index,
                        {
                            "success": True,
                            "tmp_path": self.output_path,
                            "warning": warning_str,
                        },
                    )
        except Exception:
            with contextlib.suppress(RuntimeError):
                self.signals.result.emit(
                    self.index,
                    {
                        "success": False,
                        "error": traceback.format_exc(),
                    },
                )


@QmlElement
@QmlSingleton
class TaskManager(QObject):
    input_format_changed = Signal(str)
    output_format_changed = Signal(str)
    busy_changed = Signal(bool)
    all_tasks_finished = Signal()
    _start_conversion = Signal()

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent=parent)
        self.tasks = ModelProxy(
            {
                "path": "",
                "name": "",
                "stem": "",
                "ext": "",
                "tmp_path": "",
                "success": False,
                "error": "",
                "warning": "",
            }
        )
        self.input_formats = ModelProxy({"value": "", "text": ""})
        self.output_formats = ModelProxy({"value": "", "text": ""})
        self.input_fields = ModelProxy(
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
        self._input_fields_inited = False
        self.output_fields = ModelProxy(
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
        self._output_fields_inited = False
        self.reload_formats()
        self.thread_pool = QThreadPool.global_instance()
        self.input_format_changed.connect(self.set_input_fields)
        self.output_format_changed.connect(self.set_output_fields)
        self.output_format_changed.connect(self.reset_output_ext)
        self._start_conversion.connect(self.start)
        self.timer = QTimer()
        self.timer.interval = 100
        self.timer.timeout.connect(self.check_busy)
        self.tasks.rowsAboutToBeRemoved.connect(self.delete_tmp_file)

    @Slot(result=None)
    def reload_formats(self) -> None:
        self.input_formats.clear()
        self.input_formats.append_many(
            [
                {
                    "text": plugin.file_format,
                    "value": plugin.suffix,
                }
                for plugin in plugin_manager.plugin_registry.values()
            ],
        )
        self.output_formats.clear()
        self.output_formats.append_many(
            [
                {
                    "text": plugin.file_format,
                    "value": plugin.suffix,
                }
                for plugin in plugin_manager.plugin_registry.values()
            ],
        )

    @Slot(QModelIndex, int, int)
    def delete_tmp_file(self, index: QModelIndex, start: int, end: int) -> None:
        for i in range(start, end + 1):
            path = UPath(self.tasks[i]["tmp_path"])
            if path.exists():
                with contextlib.suppress(Exception):
                    path.unlink()

    @property
    def input_format(self) -> Optional[str]:
        return settings.last_input_format

    @input_format.setter
    def input_format(self, value: Optional[str]) -> None:
        if value is not None:
            settings.last_input_format = value

    @property
    def output_format(self) -> Optional[str]:
        return settings.last_output_format

    @output_format.setter
    def output_format(self, value: Optional[str]) -> None:
        if value is not None:
            settings.last_output_format = value

    @Slot(result=bool)
    def start_conversion(self) -> bool:
        if self.is_busy():
            return False
        self._start_conversion.emit()
        return True

    @property
    def output_ext(self) -> str:
        if settings.auto_set_output_extension and self.output_format:
            return f".{self.output_format}"
        return ""

    @Slot(bool)
    def reset_output_ext(self, value: bool) -> None:
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
    def output_path_exists(self, index: int) -> str:
        task = self.tasks[index]
        return self.output_path(task).exists()

    @Slot(int, result=bool)
    def move_to_output(self, index: int) -> bool:
        task = self.tasks[index]
        if not task["success"]:
            return False
        output_dir = self.output_dir(task)
        tmp_path = UPath(task["tmp_path"])
        result = False
        try:
            target_path = output_dir / f"{task['stem']}{self.output_ext}"
            if target_path.exists():
                target_path.unlink()
            target_path.write_bytes(tmp_path.read_bytes())
            result = True
        except OSError as e:
            self.tasks.update(index, {"error": str(e)})
        return result

    @staticmethod
    def inspect_fields(option_class: BaseModel) -> list[dict[str, Any]]:
        fields = []
        for option_key, field_info in option_class.model_fields.items():
            default_value = None if field_info.default is PydanticUndefined else field_info.default
            if issubclass(field_info.annotation, bool):
                fields.append(
                    {
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
                annotations = get_type_hints(field_info.annotation, include_extras=True)
                choices = []
                for enum_item in field_info.annotation:
                    if enum_item.name in annotations:
                        annotated_args = list(get_args(annotations[enum_item.name]))
                        if len(annotated_args) >= 2:
                            _, enum_field = annotated_args[:2]
                        else:
                            continue
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
                        "type": "enum",
                        "name": option_key,
                        "title": field_info.title,
                        "description": field_info.description or "",
                        "default": default_value,
                        "value": default_value,
                        "choices": choices,
                    }
                )
            elif issubclass(field_info.annotation, (str, int, float, Color, BaseComplexModel)):
                if issubclass(field_info.annotation, BaseComplexModel):
                    default_value = field_info.annotation.default_repr()
                fields.append(
                    {
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
            plugin_input = plugin_manager.plugin_registry[self.input_format]
            if plugin_input.plugin_object is not None and hasattr(
                plugin_input.plugin_object, "load"
            ):
                option_class = get_type_hints(plugin_input.plugin_object.load)["options"]
                input_fields = self.inspect_fields(option_class)
                self.input_fields.append_many(input_fields)
            if not self._input_fields_inited:
                self._input_fields_inited = True

    @Slot(str)
    def set_output_fields(self, output_format: str) -> None:
        if output_format == self.output_format and self._output_fields_inited:
            return
        if output_format:
            self.output_format = output_format
            self.output_fields.clear()
            plugin_output = plugin_manager.plugin_registry[self.output_format]
            if plugin_output.plugin_object is not None and hasattr(
                plugin_output.plugin_object, "dump"
            ):
                option_class = get_type_hints(plugin_output.plugin_object.dump)["options"]
                output_fields = self.inspect_fields(option_class)
                self.output_fields.append_many(output_fields)
            if not self._output_fields_inited:
                self._output_fields_inited = True

    @Slot(str, result="QVariant")
    def plugin_info(self, name: str) -> dict[str, str]:
        assert name in {"input_format", "output_format"}
        if (suffix := getattr(self, name)) in plugin_manager.plugin_registry:
            plugin = plugin_manager.plugin_registry[suffix]
            return {
                "name": plugin.name,
                "author": plugin.author,
                "website": plugin.website,
                "description": plugin.description,
                "version": str(plugin.version),
                "file_format": plugin.file_format,
                "suffix": f"(*.{plugin.suffix})",
                "icon_base64": f"data:image/png;base64,{plugin.icon_base64}",
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
                {
                    "path": path,
                    "name": path_obj.name,
                    "stem": path_obj.stem,
                    "ext": self.output_ext,
                    "tmp_path": "",
                    "success": None,
                    "error": "",
                    "warning": "",
                }
            )
        self.tasks.append_many(tasks)
        if (
            settings.auto_detect_input_format
            and path_obj is not None
            and (suffix := path_obj.suffix[1:]) in plugin_manager.plugin_registry
        ):
            self.set_str("input_format", suffix)

    @Slot(str, result=QAbstractListModel)
    def qget(self, name: str) -> Any:
        return getattr(self, name)

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
        ):
            if delete_len := more_itertools.ilen(
                more_itertools.rstrip(
                    self.tasks,
                    lambda task: task["path"].lower().endswith(f".{value}"),
                )
            ):
                self.tasks.delete_many(0, delete_len)
        getattr(self, f"{name}_changed").emit(value)

    def plugin_info_file(self, plugin_archive: zipfile.Path) -> Optional[zipfile.Path]:
        plugin_info_filename = None
        for plugin_file in plugin_archive.iterdir():
            if plugin_file.is_file() and plugin_file.name.endswith(
                f".{plugin_manager.info_extension}"
            ):
                plugin_info_filename = plugin_file
        return plugin_info_filename

    @Slot(list, result="QVariant")
    def extract_plugin_infos(self, paths: list[str]) -> list[dict[str, str]]:
        infos = []
        for path in paths:
            zip_file = zipfile.Path(path)
            if (plugin_info_filename := self.plugin_info_file(zip_file)) is not None:
                plugin_info = plugin_manager.info_cls.load(plugin_info_filename)
                if plugin_info is not None:
                    infos.append(
                        {
                            "name": plugin_info.name,
                            "author": plugin_info.author,
                            "version": plugin_info.version,
                            "file_format": plugin_info.file_format,
                            "suffix": f"(*.{plugin_info.suffix})",
                            "info_filename": plugin_info_filename,
                        }
                    )
                    logger.debug(infos)
        return infos

    @Slot(result=bool)
    def is_busy(self) -> bool:
        return self.thread_pool.active_thread_count > 0

    @Slot()
    def check_busy(self) -> None:
        if self.is_busy():
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
            self.all_tasks_finished.emit()

    def set_busy(self, busy: bool) -> None:
        self.busy_changed.emit(busy)

    @Slot()
    def start(self) -> None:
        if self.input_format is None or self.output_format is None:
            error_message = "Please select input and output formats first."
            for i in range(len(self.tasks)):
                self.tasks.update(i, {"success": False, "error": error_message, "warning": ""})
            return
        self.set_busy(True)
        input_options = {field["name"]: field["value"] for field in self.input_fields}
        output_options = {field["name"]: field["value"] for field in self.output_fields}
        for i in range(len(self.tasks)):
            self.tasks.update(i, {"success": False, "error": "", "warning": ""})
        self.thread_pool.max_thread_count = (
            max(len(self.tasks), 4) if settings.multi_threaded_conversion else 1
        )
        for i in range(len(self.tasks)):
            input_path = self.tasks[i]["path"]
            output_path = f"memory:/{uuid.uuid4()}.{self.output_ext}"
            worker = ConversionWorker(
                i,
                input_path,
                output_path,
                self.input_format,
                self.output_format,
                input_options,
                output_options,
            )
            worker.signals.result.connect(
                self.tasks.update, type=Qt.ConnectionType.BlockingQueuedConnection
            )
            self.thread_pool.start(worker)
        self.timer.start()
