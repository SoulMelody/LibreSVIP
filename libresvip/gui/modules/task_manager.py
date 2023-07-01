import atexit
import enum
import pathlib
import shutil
import tempfile
import traceback
import warnings
import zipfile
from typing import Any, get_args, get_type_hints

from pydantic_core import PydanticUndefined
from pydantic_extra_types.color import Color
from qmlease import slot
from qtpy.QtCore import QObject, QRunnable, QThreadPool, QTimer, QUrl, Signal
from qtpy.QtGui import QDesktopServices

from libresvip.core.config import settings
from libresvip.core.warning_types import BaseWarning
from libresvip.extension.manager import load_plugins, plugin_manager, plugin_registry
from libresvip.model.base import BaseComplexModel, BaseModel
from libresvip.utils import shorten_error_message

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
                self.index, {"success": False, "error": shorten_error_message(traceback.format_exc())}
            )


class TaskManager(QObject):
    input_format_changed = Signal(str)
    output_format_changed = Signal(str)
    busy_changed = Signal(bool)
    all_tasks_finished = Signal()
    _start_conversion = Signal()

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
        if not settings.last_input_format and self.input_formats:
            settings.last_input_format = self.input_formats[0]["value"]
        if not settings.last_output_format and self.output_formats:
            settings.last_output_format = self.output_formats[0]["value"]
        self.thread_pool = QThreadPool.globalInstance()
        self.temp_dir = pathlib.Path(tempfile.mkdtemp(prefix="libresvip"))
        self.temp_dir.mkdir(exist_ok=True)
        atexit.register(self.clean_temp_dir)
        self.input_format_changed.connect(self.set_input_fields)
        self.output_format_changed.connect(self.set_output_fields)
        self.output_format_changed.connect(self.reset_output_ext)
        self._start_conversion.connect(self.start)
        self.timer = QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.check_busy)

    @property
    def input_format(self) -> str:
        return settings.last_input_format

    @input_format.setter
    def input_format(self, value: str):
        settings.last_input_format = value

    @property
    def output_format(self) -> str:
        return settings.last_output_format

    @output_format.setter
    def output_format(self, value: str):
        settings.last_output_format = value

    def clean_temp_dir(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @slot(result=bool)
    def start_conversion(self) -> bool:
        if self.is_busy():
            return False
        self._start_conversion.emit()
        return True

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
            target_path = output_dir / f"{task['stem']}{self.output_ext}"
            if target_path.exists():
                target_path.unlink()
            shutil.move(task["tmp_path"], target_path)
            return True
        except (FileExistsError, FileNotFoundError, OSError) as e:
            self.tasks.update(index, {"error": str(e)})
            return False

    @staticmethod
    def inspect_fields(option_class: BaseModel) -> list[dict]:
        fields = []
        for option_key, field_info in option_class.model_fields.items():
            default_value = (
                None if field_info.default is PydanticUndefined else field_info.default
            )
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
            elif issubclass(
                field_info.annotation, (str, int, float, Color, BaseComplexModel)
            ):
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
                            }
                        )
                    else:
                        print(enum_item.name)
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
        return fields

    @slot(str)
    def set_input_fields(self, input_format: str) -> None:
        if input_format == self.input_format:
            return
        self.input_format = input_format
        self.input_fields.clear()
        plugin_input = plugin_registry[self.input_format]
        if hasattr(plugin_input.plugin_object, "load"):
            option_class = get_type_hints(plugin_input.plugin_object.load)["options"]
            input_fields = self.inspect_fields(option_class)
            self.input_fields.append_many(input_fields)

    @slot(str)
    def set_output_fields(self, output_format: str) -> None:
        if output_format == self.output_format and self.output_fields:
            return
        self.output_format = output_format
        self.output_fields.clear()
        plugin_output = plugin_registry[self.output_format]
        if hasattr(plugin_output.plugin_object, "dump"):
            option_class = get_type_hints(plugin_output.plugin_object.dump)["options"]
            output_fields = self.inspect_fields(option_class)
            self.output_fields.append_many(output_fields)

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
        if (
            settings.auto_detect_input_format
            and path_obj is not None
            and (suffix := path_obj.suffix[1:]) in plugin_registry
        ):
            self.set_str("input_format", suffix)

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

    def plugin_info_file(self, temp_plugin_dir: pathlib.Path) -> str:
        plugin_info_filename = None
        for analyzer in plugin_manager.getPluginLocator()._analyzers:
            if analyzer.name == "info_ext":
                for plugin_file in temp_plugin_dir.glob("*.*"):
                    if analyzer.isValidPlugin(str(plugin_file)):
                        plugin_info_filename = plugin_file.name
                        break
                break
        return plugin_info_filename

    @slot(list, result=int)
    def install_plugins(self, infos: list[dict]) -> int:
        success_count = 0
        install_dir = pathlib.Path(plugin_manager.getInstallDir())
        for info in infos:
            try:
                plugin_info, _ = plugin_manager._gatherCorePluginInfo(
                    info["directory"], info["info_filename"]
                )
                if plugin_info is not None:
                    shutil.copytree(info["directory"], install_dir / plugin_info.suffix)
                success_count += 1
            except Exception as e:
                print(e)
        load_plugins()
        return success_count

    @slot(list, result=list)
    def extract_plugin_infos(self, paths: list[str]) -> list[dict]:
        infos = []
        for path in paths:
            temp_plugin_dir = pathlib.Path(
                tempfile.mkdtemp(prefix="plugin", dir=self.temp_dir)
            )
            with zipfile.ZipFile(path) as zip_file:
                zip_file.extractall(path=temp_plugin_dir)
            if (
                plugin_info_filename := self.plugin_info_file(temp_plugin_dir)
            ) is not None:
                plugin_info, _ = plugin_manager._gatherCorePluginInfo(
                    temp_plugin_dir, plugin_info_filename
                )
                if plugin_info is not None:
                    infos.append(
                        {
                            "name": plugin_info.name,
                            "author": plugin_info.author,
                            "version": plugin_info.version,
                            "format_desc": f"{plugin_info.file_format} (*.{plugin_info.suffix})",
                            "directory": str(temp_plugin_dir.resolve().as_posix()),
                            "info_filename": plugin_info_filename,
                        }
                    )
                    print(infos)
        return infos

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
