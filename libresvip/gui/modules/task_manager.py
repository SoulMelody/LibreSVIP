import atexit
import enum
import pathlib
import shutil
import tempfile
import traceback
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Optional, get_args, get_type_hints

from pydantic.color import Color
from qmlease import slot
from qtpy.QtCore import QObject, QUrl, Signal
from qtpy.QtGui import QDesktopServices

from libresvip.core.config import settings
from libresvip.core.warning_types import BaseWarning
from libresvip.extension.manager import plugin_manager, plugin_registry
from libresvip.model.base import BaseComplexModel

from .model_proxy import ModelProxy


class TaskManager(QObject):
    input_format_changed = Signal(str)
    output_format_changed = Signal(str)
    busy_changed = Signal(bool)
    input_fileds_changed = Signal()
    output_fileds_changed = Signal()
    tasks_size_changed = Signal()
    task_finished = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.tasks = ModelProxy(
            {
                "path": "",
                "name": "",
                "stem": "",
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
        self.input_format_changed.connect(self.set_input_fields)
        self.output_format_changed.connect(self.set_output_fields)
        self.busy = False
        self.temp_dir = pathlib.Path(tempfile.mkdtemp(prefix="libresvip"))
        self.temp_dir.mkdir(exist_ok=True)
        atexit.register(self.clean_temp_dir)

    def clean_temp_dir(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @property
    def output_ext(self) -> str:
        return f".{self.output_format}" if settings.auto_set_output_extension else ""

    def output_dir(self, task: dict) -> pathlib.Path:
        if settings.save_folder.is_absolute():
            output_dir = settings.save_folder
        else:
            output_dir = pathlib.Path(task["path"]) / str(settings.save_folder)
        return output_dir

    @slot(int, result=bool)
    def output_path_exists(self, index: int) -> str:
        task = self.tasks[index]
        output_dir = self.output_dir(task)
        return (output_dir / f"{task['stem']}{self.output_ext}").exists()

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
        return self.busy

    def set_busy(self, busy: bool) -> None:
        self.busy = busy
        self.busy_changed.emit(busy)

    def convert_one(
        self, input_path, output_path, input_options, output_options
    ) -> tuple[Optional[str], str]:
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
                pathlib.Path(input_path),
                input_option(**input_options),
            )
            output_plugin.plugin_object.dump(
                pathlib.Path(output_path), project, output_option(**output_options)
            )
            return output_path, "\n".join(str(each) for each in w)

    @slot()
    def start(self):
        self.set_busy(True)
        input_options = {field["name"]: field["value"] for field in self.input_fields}
        output_options = {field["name"]: field["value"] for field in self.output_fields}
        for i in range(len(self.tasks)):
            self.tasks.update(i, {"success": False, "error": "", "warning": ""})
        with ThreadPoolExecutor(
            max_workers=max(len(self.tasks), 4)
            if settings.multi_threaded_conversion
            else 1
        ) as executor:
            future_to_index = {}
            for i, each in enumerate(self.tasks):
                input_path = each["path"]
                output_path = tempfile.mktemp(suffix=self.output_ext, dir=self.temp_dir)
                future_to_index[
                    executor.submit(
                        self.convert_one,
                        input_path,
                        output_path,
                        input_options,
                        output_options,
                    )
                ] = i
            for future in as_completed(future_to_index):
                task_index = future_to_index[future]
                try:
                    tmp_path, warnings = future.result()
                    self.tasks.update(
                        task_index,
                        {"success": True, "tmp_path": tmp_path, "warning": warnings},
                    )
                except Exception:
                    self.tasks.update(
                        task_index, {"success": False, "error": traceback.format_exc()}
                    )
        self.set_busy(False)
        if settings.open_save_folder_on_completion:
            success_task = next((task for task in self.tasks if task["success"]), None)
            if success_task is not None:
                output_dir = self.output_dir(success_task)
                output_url = QUrl.fromLocalFile(output_dir)
                QDesktopServices.openUrl(output_url)
