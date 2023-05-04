import atexit
import enum
import pathlib
import shutil
import tempfile
import traceback
import warnings
from typing import Any, get_args, get_type_hints

from pydantic.color import Color
from qmlease import slot
from qtpy.QtCore import QObject, QRunnable, QThreadPool, QTimer, QUrl, Signal
from qtpy.QtGui import QDesktopServices

from libresvip.core.config import settings
from libresvip.core.warning_types import BaseWarning
from libresvip.extension.manager import plugin_manager, plugin_registry
from libresvip.model.base import BaseComplexModel

from .model_proxy import ModelProxy


def open_path(path: pathlib.Path):
    output_url = QUrl.fromLocalFile(path)
    QDesktopServices.openUrl(output_url)


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
        parent=None,
    ):
        super().__init__(parent=parent)
        self.index = index
        self.input_path = input_path
        self.output_path = output_path
        self.input_format = input_format
        self.output_format = output_format
        self.input_options = input_options
        self.output_options = output_options
        self.signals = ConversionWorkerSignals()

    @slot()
    def run(self):
        try:
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always", BaseWarning)
                input_plugin = plugin_registry[self.input_format]
                output_plugin = plugin_registry[self.output_format]
                input_option = get_type_hints(input_plugin.plugin_object.load).get(
                    "options"
                )
                output_option = get_type_hints(output_plugin.plugin_object.dump).get(
                    "options"
                )
                project = input_plugin.plugin_object.load(
                    pathlib.Path(self.input_path),
                    input_option(**self.input_options),
                )
                output_plugin.plugin_object.dump(
                    pathlib.Path(self.output_path),
                    project,
                    output_option(**self.output_options),
                )
                warning_str = "\n".join(str(each) for each in w)
                self.signals.result.emit(
                    self.index,
                    {
                        "success": True,
                        "tmp_path": self.output_path,
                        "warning": warning_str,
                    },
                )
        except Exception:
            self.signals.result.emit(
                self.index, {"success": False, "error": traceback.format_exc()}
            )


class TaskManager(QObject):
    input_format_changed = Signal(str)
    output_format_changed = Signal(str)
    busy_changed = Signal(bool)
    input_fileds_changed = Signal()
    output_fileds_changed = Signal()
    tasks_size_changed = Signal()
    start_conversion = Signal()
    all_tasks_finished = Signal()

    def __init__(self, parent=None):
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
        self.input_formats.append_many(
            [
                {
                    "text": f"{plugin.file_format} (*.{plugin.suffix})",
                    "value": plugin.suffix,
                }
                for plugin in plugin_registry.values()
            ],
        )
        self.output_formats.append_many(
            [
                {
                    "text": f"{plugin.file_format} (*.{plugin.suffix})",
                    "value": plugin.suffix,
                }
                for plugin in plugin_registry.values()
            ],
        )
        self.input_format = ""
        self.output_format = ""
        self.thread_pool = QThreadPool.globalInstance()
        self.temp_dir = pathlib.Path(tempfile.mkdtemp(prefix="libresvip"))
        self.temp_dir.mkdir(exist_ok=True)
        atexit.register(self.clean_temp_dir)
        self.input_format_changed.connect(self.set_input_fields)
        self.output_format_changed.connect(self.set_output_fields)
        self.output_format_changed.connect(self.reset_output_ext)
        self.start_conversion.connect(self.start)
        self.timer = QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.check_busy)

    def clean_temp_dir(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @slot(str, list, result=bool)
    def trigger_event(self, event: str, args: list) -> bool:
        if hasattr(self, event):
            sig = getattr(self, event)
            sig.emit(*args)
            return True
        return False

    @property
    def output_ext(self) -> str:
        return f".{self.output_format}" if settings.auto_set_output_extension else ""

    @slot(bool)
    def reset_output_ext(self, value: bool):
        self.tasks.update_many(0, [{"ext": self.output_ext}] * len(self.tasks))

    @staticmethod
    def output_dir(task: dict) -> pathlib.Path:
        return (
            settings.save_folder
            if settings.save_folder.is_absolute()
            else pathlib.Path(task["path"]).parent / str(settings.save_folder)
        )

    def output_path(self, task: dict) -> pathlib.Path:
        output_dir = self.output_dir(task)
        return output_dir / f"{task['stem']}{self.output_ext}"

    @slot(int, result=str)
    def get_output_path(self, index: int) -> str:
        task = self.tasks[index]
        return str(self.output_path(task))

    @slot(int, result=bool)
    def open_output_dir(self, index: int) -> bool:
        task = self.tasks[index]
        open_path(self.output_dir(task))
        return True

    @slot(int, result=bool)
    def open_output_path(self, index: int) -> bool:
        task = self.tasks[index]
        open_path(self.output_path(task))
        return True

    @slot(int, result=bool)
    def output_path_exists(self, index: int) -> str:
        task = self.tasks[index]
        return self.output_path(task).exists()

    @slot(int, result=bool)
    def move_to_output(self, index: int) -> bool:
        task = self.tasks[index]
        if not task["success"]:
            return False
        output_dir = self.output_dir(task)
        try:
            pathlib.Path(task["tmp_path"]).rename(
                output_dir / f"{task['stem']}{self.output_ext}"
            )
            return True
        except (FileExistsError, FileNotFoundError):
            return False

    @slot(str)
    def set_input_fields(self, input_format: str) -> None:
        if input_format == self.input_format:
            return
        self.input_format = input_format
        self.input_fields.clear()
        plugin_input = plugin_registry[self.input_format]
        if hasattr(plugin_input.plugin_object, "load"):
            option_class = get_type_hints(plugin_input.plugin_object.load)["options"]
            input_fields = []
            for option in option_class.__fields__.values():
                option_key = option.name
                if issubclass(option.type_, bool):
                    input_fields.append(
                        {
                            "type": "bool",
                            "name": option_key,
                            "title": option.field_info.title,
                            "description": option.field_info.description or "",
                            "default": option.default,
                            "value": option.default,
                        }
                    )
                elif issubclass(
                    option.type_, (str, int, float, Color, BaseComplexModel)
                ):
                    default_value = (
                        option.type_.default_repr()
                        if issubclass(option.type_, BaseComplexModel)
                        else option.default
                    )
                    input_fields.append(
                        {
                            "type": "color"
                            if issubclass(option.type_, Color)
                            else "other",
                            "name": option_key,
                            "title": option.field_info.title,
                            "description": option.field_info.description or "",
                            "default": default_value,
                            "value": default_value,
                        }
                    )
                elif issubclass(option.type_, enum.Enum):
                    annotations = get_type_hints(option.type_, include_extras=True)
                    choices = []
                    for enum_item in option.type_:
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
                                }
                            )
                        else:
                            print(enum_item.name)
                    input_fields.append(
                        {
                            "type": "enum",
                            "name": option_key,
                            "title": option.field_info.title,
                            "description": option.field_info.description or "",
                            "default": option.default.value,
                            "value": option.default.value,
                            "choices": choices,
                        }
                    )
            self.input_fields.append_many(input_fields)
            self.input_fileds_changed.emit()

    @slot(str)
    def set_output_fields(self, output_format: str) -> None:
        if output_format == self.output_format:
            return
        self.output_format = output_format
        self.output_fields.clear()
        plugin_output = plugin_registry[self.output_format]
        if hasattr(plugin_output.plugin_object, "dump"):
            option_class = get_type_hints(plugin_output.plugin_object.dump)["options"]
            output_fields = []
            for option in option_class.__fields__.values():
                option_key = option.name
                if issubclass(option.type_, bool):
                    output_fields.append(
                        {
                            "type": "bool",
                            "name": option_key,
                            "title": option.field_info.title,
                            "description": option.field_info.description or "",
                            "default": option.default,
                            "value": option.default,
                        }
                    )
                elif issubclass(
                    option.type_, (str, int, float, Color, BaseComplexModel)
                ):
                    default_value = (
                        option.type_.default_repr()
                        if issubclass(option.type_, BaseComplexModel)
                        else option.default
                    )
                    output_fields.append(
                        {
                            "type": "color"
                            if issubclass(option.type_, Color)
                            else "other",
                            "name": option_key,
                            "title": option.field_info.title,
                            "description": option.field_info.description or "",
                            "default": default_value,
                            "value": default_value,
                        }
                    )
                elif issubclass(option.type_, enum.Enum):
                    annotations = get_type_hints(option.type_, include_extras=True)
                    choices = []
                    for enum_item in option.type_:
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
                                }
                            )
                        else:
                            print(enum_item.name)
                    output_fields.append(
                        {
                            "type": "enum",
                            "name": option_key,
                            "title": option.field_info.title,
                            "description": option.field_info.description or "",
                            "default": option.default.value,
                            "value": option.default.value,
                            "choices": choices,
                        }
                    )
            self.output_fields.append_many(output_fields)
            self.output_fileds_changed.emit()

    @slot(str, result=dict)
    def plugin_info(self, name: str) -> dict:
        assert name in {"input_format", "output_format"}
        if (suffix := getattr(self, name)) in plugin_registry:
            plugin = plugin_registry[suffix]
            return {
                "name": plugin.name,
                "author": plugin.author,
                "website": plugin.website,
                "description": plugin.description,
                "version": plugin.version_string,
                "format_desc": f"{plugin.file_format} (*.{plugin.suffix})",
                "icon_base64": f"data:image/png;base64,{plugin.icon_base64}",
            }
        return {
            "name": "",
            "author": "",
            "website": "",
            "description": "",
            "version": "",
            "format_desc": "",
            "icon_base64": "",
        }

    @slot()
    def reset_stems(self) -> None:
        for i, task in enumerate(self.tasks):
            self.tasks.update(i, {"stem": pathlib.Path(task["path"]).stem})

    @slot(list)
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
        self.tasks_size_changed.emit()
        if (
            settings.auto_detect_input_format
            and path_obj is not None
            and (suffix := path_obj.suffix[1:]) in plugin_registry
        ):
            self.set_str("input_format", suffix)

    @slot()
    def reset(self) -> None:
        self.tasks.clear()
        self.tasks_size_changed.emit()

    @slot(str, result=object)
    def qget(self, name: str) -> Any:
        return getattr(self, name)

    @slot(str, object)
    def qset(self, name: str, value: Any) -> None:
        setattr(self, name, value)

    @slot(str, result=str)
    def get_str(self, name: str) -> str:
        assert name in {"input_format", "output_format"}
        return getattr(self, name)

    @slot(str, str)
    def set_str(self, name: str, value: str) -> None:
        assert name in {"input_format", "output_format"}
        getattr(self, f"{name}_changed").emit(value)

    @slot(str, result=bool)
    def install_plugin(self, path: str) -> bool:
        return plugin_manager.installFromZIP(path)

    @slot(result=bool)
    def is_busy(self) -> bool:
        return self.thread_pool.activeThreadCount() > 0

    @slot()
    def check_busy(self) -> None:
        if self.is_busy():
            self.set_busy(True)
        else:
            self.set_busy(False)
            if self.timer.isActive():
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

    @slot()
    def start(self):
        self.set_busy(True)
        input_options = {field["name"]: field["value"] for field in self.input_fields}
        output_options = {field["name"]: field["value"] for field in self.output_fields}
        for i in range(len(self.tasks)):
            self.tasks.update(i, {"success": False, "error": "", "warning": ""})
        self.thread_pool.setMaxThreadCount(
            max(len(self.tasks), 4) if settings.multi_threaded_conversion else 1
        )
        for i in range(len(self.tasks)):
            input_path = self.tasks[i]["path"]
            output_path = tempfile.mktemp(suffix=self.output_ext, dir=self.temp_dir)
            worker = ConversionWorker(
                i,
                input_path,
                output_path,
                self.input_format,
                self.output_format,
                input_options,
                output_options,
            )
            worker.signals.result.connect(self.tasks.update)
            self.thread_pool.start(worker)
        self.timer.start()
