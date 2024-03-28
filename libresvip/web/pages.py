import argparse
import asyncio
import dataclasses
import enum
import functools
import io
import math
import pathlib
import secrets
import textwrap
import traceback
import uuid
import warnings
import zipfile
from concurrent.futures import ThreadPoolExecutor
from operator import not_
from typing import (
    TYPE_CHECKING,
    Any,
    BinaryIO,
    Optional,
    SupportsFloat,
    TypedDict,
    Union,
    get_args,
    get_type_hints,
)
from urllib.parse import quote, unquote

import aiofiles
from nicegui import app, binding, ui
from nicegui.context import get_client
from nicegui.elements.switch import Switch
from nicegui.events import KeyEventArguments, UploadEventArguments
from nicegui.storage import request_contextvar
from pydantic import RootModel, create_model
from pydantic.dataclasses import dataclass
from pydantic_core import PydanticUndefined
from pydantic_extra_types.color import Color
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response
from upath import UPath

import libresvip
from libresvip.core.config import (
    ConversionMode,
    DarkMode,
    Language,
    LibreSvipBaseUISettings,
)
from libresvip.core.constants import PACKAGE_NAME, app_dir, res_dir
from libresvip.core.warning_types import BaseWarning
from libresvip.extension.manager import middleware_manager, plugin_manager
from libresvip.model.base import BaseComplexModel, Project
from libresvip.utils.text import shorten_error_message
from libresvip.utils.translation import get_translation, lazy_translation
from libresvip.web.elements import QFab, QFabAction

if TYPE_CHECKING:
    from nicegui.elements.menu import Menu
    from nicegui.elements.select import Select

binding.MAX_PROPAGATION_TIME = 0.03


@dataclass
class LibreSvipWebUserSettings(LibreSvipBaseUISettings):
    def __post_init__(self) -> None:
        detected_language = None
        request = request_contextvar.get()
        if accept_lang := request.headers.get("Accept-Language"):
            first_lang = accept_lang.split(",")[0].partition(";")[0]
            if first_lang.startswith("zh"):
                detected_language = Language.from_locale("zh_CN")
            elif first_lang.startswith("ja"):
                detected_language = Language.from_locale("ja_JP")
        if detected_language is not None:
            self.language = detected_language


def dark_mode2str(mode: DarkMode) -> Optional[bool]:
    if mode == DarkMode.LIGHT:
        return False
    elif mode == DarkMode.DARK:
        return True


def int_validator(value: Optional[SupportsFloat]) -> bool:
    if isinstance(value, int):
        return True
    elif isinstance(value, str):
        return value.replace("+", "-").removeprefix("-").isdigit()
    elif isinstance(value, float):
        return value.is_integer()
    else:
        return False


def float_validator(value: Optional[SupportsFloat]) -> bool:
    if isinstance(value, SupportsFloat):
        return not math.isnan(float(value))
    else:
        return False


@dataclasses.dataclass
class ConversionTask:
    name: str
    upload_path: pathlib.Path
    output_path: pathlib.Path
    running: bool
    success: Optional[bool]
    error: Optional[str]
    warning: Optional[str]

    def reset(self) -> None:
        self.running = False
        self.success = None
        self.error = None
        self.warning = None
        if self.output_path.exists():
            self.output_path.unlink()

    def __del__(self) -> None:
        if self.upload_path.exists():
            self.upload_path.unlink()
        if self.output_path.exists():
            self.output_path.unlink()


class ChildMergeTask(TypedDict):
    name: str
    upload_path: pathlib.Path
    running: bool
    success: Optional[bool]
    error: Optional[str]
    warning: Optional[str]
    project: Optional[Project]


class MergeTask(TypedDict):
    name: str
    output_path: pathlib.Path
    project: Optional[Project]
    child_tasks: list[ChildMergeTask]


class ChildSplitTask(TypedDict):
    name: str
    project: Project
    output_path: pathlib.Path
    running: bool
    success: Optional[bool]
    error: Optional[str]
    warning: Optional[str]


class SplitTask(TypedDict):
    name: str
    upload_path: pathlib.Path
    max_track_count: int
    running: bool
    success: Optional[bool]
    error: Optional[str]
    warning: Optional[str]
    child_tasks: list[ChildSplitTask]


@ui.page("/")
@ui.page("/?lang={lang}")
def page_layout(lang: Optional[str] = None) -> None:
    cur_client = get_client()

    default_settings = LibreSvipWebUserSettings()
    default_settings_dict = RootModel[LibreSvipWebUserSettings](default_settings).model_dump(
        mode="json"
    )

    for key, default_value in default_settings_dict.items():
        if key not in app.storage.user:
            if key == "dark_mode":
                default_value = dark_mode2str(default_value)
            app.storage.user[key] = default_value
    if lang is None:
        lang = app.storage.user["language"]
    if lang != app.storage.user["language"]:
        app.storage.user["language"] = lang
    translation = get_translation(PACKAGE_NAME, lang)

    def _(message: str) -> str:
        if message.strip():
            return translation.gettext(message)
        return message

    plugin_details = {
        identifier: {
            "name": plugin.name,
            "author": plugin.author,
            "website": plugin.website,
            "description": plugin.description,
            "version": str(plugin.version),
            "suffix": f"(*.{plugin.suffix})",
            "file_format": plugin.file_format,
            "icon_base64": plugin.icon_base64,
        }
        for identifier, plugin in plugin_manager.plugin_registry.items()
    }

    def plugin_info(attr_name: str) -> None:
        attr = getattr(selected_formats, attr_name)
        with ui.row().classes("w-full h-full"):
            with ui.element("div").classes("w-100 h-100") as icon:
                icon._props["style"] = (
                    f"""background: url('data:image/png;base64,{plugin_details[attr]["icon_base64"]}'); background-size: contain; border-radius: 50%; width: 100px; height: 100px"""
                )
            ui.separator().props("vertical")
            with ui.column().classes("justify-center flex-grow"):
                ui.label(_(plugin_details[attr]["name"] or "")).classes(
                    "text-h5 w-full font-bold text-center",
                )
                with ui.row().classes("w-full"):
                    with ui.element("q-chip").props("icon=tag"):
                        ui.label(plugin_details[attr]["version"])
                        ui.tooltip(_("Version"))
                    ui.separator().props("vertical")
                    with ui.element("q-chip").props("icon=person"):
                        with ui.row().classes("items-center"):
                            ui.label(_("Author") + ": ")
                            ui.link(
                                plugin_details[attr]["author"],
                                plugin_details[attr]["website"],
                                new_tab=True,
                            )
                            ui.icon("open_in_new")
                        ui.tooltip(plugin_details[attr]["website"])
                with ui.element("q-chip").props("icon=outline_insert_drive_file"):
                    ui.label(
                        _(plugin_details[attr]["file_format"] or "")
                        + " "
                        + plugin_details[attr]["suffix"],
                    )
        ui.separator()
        with ui.card_section().classes("w-full"):
            ui.label(_("Introduction")).classes("text-subtitle1 font-bold")
            ui.label(_(plugin_details[attr]["description"] or ""))

    input_plugin_info = ui.refreshable(functools.partial(plugin_info, "input_format"))
    output_plugin_info = ui.refreshable(functools.partial(plugin_info, "output_format"))

    def panel_header(attr_name: str, title: str, prefix: str, icon: str) -> None:
        attr = getattr(selected_formats, attr_name)
        with ui.row().classes("w-full items-center"):
            ui.icon(icon).classes("text-lg")
            ui.label(title).classes("text-subtitle1 font-bold")
            ui.label(prefix + _(plugin_details[attr]["file_format"] or "") + "]").classes(
                "flex-grow",
            )

    input_panel_header = ui.refreshable(
        functools.partial(
            panel_header,
            "input_format",
            _("Input Options"),
            _("[Import as "),
            "input",
        ),
    )
    output_panel_header = ui.refreshable(
        functools.partial(
            panel_header,
            "output_format",
            _("Output Options"),
            _("[Export to "),
            "output",
        ),
    )

    def options_form(attr_prefix: str, method: str) -> None:
        attr = getattr(selected_formats, attr_prefix + "_format")
        conversion_plugin = plugin_manager.plugin_registry[attr]
        field_types = {}
        option_class = None
        if (
            hasattr(conversion_plugin.plugin_object, method)
            and (
                option_class := get_type_hints(
                    getattr(conversion_plugin.plugin_object, method),
                ).get("options")
            )
            and hasattr(option_class, "model_fields")
        ):
            for option_key, field_info in option_class.model_fields.items():
                if issubclass(
                    field_info.annotation,
                    (str, Color, enum.Enum, BaseComplexModel),
                ):
                    field_types[option_key] = str
                else:
                    field_types[option_key] = field_info.annotation
        if not option_class or not field_types:
            return
        setattr(
            selected_formats,
            attr_prefix + "_options",
            TypedDict(f"{attr_prefix.title()}Options", field_types)(),
        )
        option_dict = getattr(selected_formats, attr_prefix + "_options")
        with ui.column().classes("w-full"):
            for i, (option_key, field_info) in enumerate(
                option_class.model_fields.items(),
            ):
                default_value = (
                    None if field_info.default is PydanticUndefined else field_info.default
                )
                with ui.row().classes("items-center w-full") as row:
                    if i:
                        row._props["style"] = """
                            background-image: linear-gradient(to right, #ccc 0%, #ccc 50%, transparent 50%);
                            background-size: 8px 1px;
                            background-repeat: repeat-x;
                        """
                    if issubclass(field_info.annotation, bool):
                        ui.switch(
                            _(field_info.title),
                            value=default_value,
                        ).bind_value(
                            option_dict,
                            option_key,
                        ).classes("flex-grow")
                    elif issubclass(field_info.annotation, enum.Enum):
                        annotations = get_type_hints(
                            field_info.annotation,
                            include_extras=True,
                        )
                        choices = {}
                        for enum_item in field_info.annotation:
                            if enum_item.name in annotations:
                                annotated_args = list(
                                    get_args(annotations[enum_item.name]),
                                )
                                if len(annotated_args) >= 2:
                                    enum_field = annotated_args[1]
                                else:
                                    continue
                                choices[enum_item] = _(enum_field.title)
                        ui.select(
                            choices,
                            label=_(field_info.title),
                            value=default_value,
                        ).bind_value(option_dict, option_key).classes("flex-grow")
                    elif issubclass(field_info.annotation, Color):
                        ui.color_input(
                            label=_(field_info.title),
                            value=default_value,
                        ).bind_value(option_dict, option_key).classes("flex-grow")
                    elif issubclass(field_info.annotation, (str, BaseComplexModel)):
                        if issubclass(field_info.annotation, BaseComplexModel):
                            default_value = field_info.annotation.default_repr()
                        ui.input(
                            label=_(field_info.title),
                            value=default_value,
                        ).bind_value(option_dict, option_key).classes("flex-grow")
                    elif issubclass(field_info.annotation, (int, float)):
                        with (
                            ui.number(
                                label=_(field_info.title),
                                value=default_value,
                            )
                            .bind_value(option_dict, option_key)
                            .classes(
                                "flex-grow",
                            ) as num_input
                        ):
                            if issubclass(field_info.annotation, int):
                                num_input.validation = {
                                    _("Invalid integer"): int_validator,
                                }
                            else:
                                num_input.validation = {
                                    _("Invalid float"): float_validator,
                                }
                    else:
                        continue
                    if field_info.description:
                        with (
                            ui.icon("help_outline")
                            .classes("text-3xl")
                            .style(
                                "cursor: help",
                            )
                        ):
                            ui.tooltip(_(field_info.description))

    input_options = ui.refreshable(functools.partial(options_form, "input", "load"))

    output_options = ui.refreshable(functools.partial(options_form, "output", "dump"))

    def middleware_options_form(attr: str, toggler: Switch) -> None:
        conversion_plugin = middleware_manager.plugin_registry[attr]
        field_types = {}
        option_class = None
        if (
            hasattr(conversion_plugin.plugin_object, "process")
            and (
                option_class := get_type_hints(
                    getattr(conversion_plugin.plugin_object, "process"),
                ).get("options")
            )
            and hasattr(option_class, "model_fields")
        ):
            for option_key, field_info in option_class.model_fields.items():
                if issubclass(
                    field_info.annotation,
                    (str, Color, enum.Enum, BaseComplexModel),
                ):
                    field_types[option_key] = str
                else:
                    field_types[option_key] = field_info.annotation
        if not option_class or not field_types:
            return
        option_dict = getattr(selected_formats.middleware_options, attr)
        with ui.column().classes("w-full").bind_visibility_from(toggler, "value"):
            for i, (option_key, field_info) in enumerate(
                option_class.model_fields.items(),
            ):
                default_value = (
                    None if field_info.default is PydanticUndefined else field_info.default
                )
                with ui.row().classes("items-center w-full") as row:
                    if i:
                        row._props["style"] = """
                            background-image: linear-gradient(to right, #ccc 0%, #ccc 50%, transparent 50%);
                            background-size: 8px 1px;
                            background-repeat: repeat-x;
                        """
                    if issubclass(field_info.annotation, bool):
                        ui.switch(
                            _(field_info.title),
                            value=default_value,
                        ).bind_value(
                            option_dict,
                            option_key,
                        ).classes("flex-grow")
                    elif issubclass(field_info.annotation, enum.Enum):
                        annotations = get_type_hints(
                            field_info.annotation,
                            include_extras=True,
                        )
                        choices = {}
                        for enum_item in field_info.annotation:
                            if enum_item.name in annotations:
                                annotated_args = list(
                                    get_args(annotations[enum_item.name]),
                                )
                                if len(annotated_args) >= 2:
                                    enum_field = annotated_args[1]
                                else:
                                    continue
                                choices[enum_item] = _(enum_field.title)
                        ui.select(
                            choices,
                            label=_(field_info.title),
                            value=default_value,
                        ).bind_value(option_dict, option_key).classes("flex-grow")
                    elif issubclass(field_info.annotation, Color):
                        ui.color_input(
                            label=_(field_info.title),
                            value=default_value,
                        ).bind_value(option_dict, option_key).classes("flex-grow")
                    elif issubclass(field_info.annotation, (str, BaseComplexModel)):
                        if issubclass(field_info.annotation, BaseComplexModel):
                            default_value = field_info.annotation.default_repr()
                        ui.input(
                            label=_(field_info.title),
                            value=default_value,
                        ).bind_value(option_dict, option_key).classes("flex-grow")
                    elif issubclass(field_info.annotation, (int, float)):
                        with (
                            ui.number(
                                label=_(field_info.title),
                                value=default_value,
                            )
                            .bind_value(option_dict, option_key)
                            .classes(
                                "flex-grow",
                            ) as num_input
                        ):
                            if issubclass(field_info.annotation, int):
                                num_input.validation = {
                                    _("Invalid integer"): int_validator,
                                }
                            else:
                                num_input.validation = {
                                    _("Invalid float"): float_validator,
                                }
                    else:
                        continue
                    if field_info.description:
                        with (
                            ui.icon("help_outline")
                            .classes("text-3xl")
                            .style(
                                "cursor: help",
                            )
                        ):
                            ui.tooltip(_(field_info.description))

    select_input: Select
    select_output: Select

    @dataclasses.dataclass
    class SelectedFormats:
        _input_format: str = dataclasses.field(default="")
        _output_format: str = dataclasses.field(default="")
        input_options: dict[str, Any] = dataclasses.field(default_factory=dict)
        output_options: dict[str, Any] = dataclasses.field(default_factory=dict)
        files_to_convert: dict[str, ConversionTask] = dataclasses.field(
            default_factory=dict,
        )
        split_tasks: list[SplitTask] = dataclasses.field(default_factory=list)
        merge_tasks: list[MergeTask] = dataclasses.field(default_factory=list)

        def __post_init__(self) -> None:
            self.middleware_enabled_states = create_model(
                "middleware_enabled_states",
                **{abbr: (bool, False) for abbr in middleware_manager.plugin_registry},
            )()
            self.middleware_options = create_model(
                "middleware_options",
                **{
                    abbr: (options, options())
                    for abbr, middleware in middleware_manager.plugin_registry.items()
                    if (
                        middleware.plugin_object is not None
                        and hasattr(middleware.plugin_object, "process")
                        and (
                            options := get_type_hints(middleware.plugin_object.process).get(
                                "options",
                            )
                        )
                    )
                },
            )()
            self.input_format = app.storage.user["last_input_format"] or next(  # type: ignore[no-redef]
                iter(plugin_manager.plugin_registry),
                "",
            )
            self.output_format = app.storage.user["last_output_format"] or next(  # type: ignore[no-redef]
                iter(plugin_manager.plugin_registry),
                "",
            )
            app.add_route(f"/export/{cur_client.id}/", self.export_all, methods=["GET"])
            app.add_route(
                f"/export/{cur_client.id}/{{filename}}",
                self.export_one,
                methods=["GET"],
            )

        @functools.cached_property
        def temp_path(self) -> UPath:
            user_temp_path = UPath("memory:/") / f"{cur_client.id}"
            if not user_temp_path.exists():
                user_temp_path.mkdir(exist_ok=True)
            return user_temp_path

        def reset(self) -> None:
            self.files_to_convert.clear()
            self.tasks_container.refresh()

        def filter_input_ext(self) -> None:
            self.files_to_convert = {
                name: info
                for name, info in self.files_to_convert.items()
                if info.upload_path.suffix == f".{self.input_format}"
            }
            self.tasks_container.refresh()

        @ui.refreshable
        def tasks_container(self) -> None:
            with ui.scroll_area().classes("w-full"):
                for info in self.files_to_convert.values():
                    with ui.row().classes("w-full items-center"):

                        def remove_row() -> None:
                            del self.files_to_convert[info.name]
                            self.tasks_container.refresh()

                        ui.label(info.name).classes("flex-grow")
                        ui.spinner().props("size=lg").bind_visibility_from(
                            info,
                            "running",
                        )
                        ui.icon("check", size="lg").classes(
                            "text-green-500",
                        ).bind_visibility_from(info, "success")
                        with (
                            ui.dialog() as error_dialog,
                            ui.element(
                                "q-banner",
                            ).classes("bg-red-500 w-auto") as error_banner,
                        ):
                            with (
                                ui.scroll_area()
                                .classes(
                                    remove="nicegui-scroll-area",
                                )
                                .style("width: 500px; height: 16rem;")
                            ):
                                ui.label().classes("text-lg").style(
                                    "word-break: break-all; white-space: pre-wrap;",
                                ).bind_text_from(
                                    info,
                                    "error",
                                    backward=shorten_error_message,
                                )
                            with error_banner.add_slot("action"):
                                ui.button(
                                    _("Copy to clipboard"),
                                    on_click=lambda: ui.run_javascript(
                                        f"navigator.clipboard.writeText({repr(info.error)})",
                                    )
                                    and ui.notify(_("Copied"), type="info"),
                                )
                                ui.button(_("Close"), on_click=error_dialog.close)
                        ui.button(
                            icon="error",
                            color="red",
                            on_click=error_dialog.open,
                        ).props("round").bind_visibility_from(info, "error")
                        with (
                            ui.dialog() as warn_dialog,
                            ui.element("q-banner").classes(
                                "bg-yellow-500 w-auto",
                            ) as warn_banner,
                        ):
                            with (
                                ui.scroll_area()
                                .classes(
                                    remove="nicegui-scroll-area",
                                )
                                .style("width: 500px; height: 16rem;")
                            ):
                                ui.label().classes("text-lg").style(
                                    "word-break: break-all; white-space: pre-wrap;",
                                ).bind_text_from(info, "warning", backward=str)
                            with warn_banner.add_slot("action"):
                                ui.button(
                                    _("Copy to clipboard"),
                                    on_click=lambda: ui.run_javascript(
                                        f"navigator.clipboard.writeText({repr(info.warning)})",
                                    )
                                    and ui.notify(_("Copied"), type="info"),
                                )
                                ui.button(_("Close"), on_click=warn_dialog.close)
                        ui.button(
                            icon="warning",
                            color="yellow",
                            on_click=warn_dialog.open,
                        ).props("round").bind_visibility_from(info, "warning")
                        ui.button(
                            icon="download",
                            on_click=functools.partial(self.save_file, info.name),
                        ).props("round").bind_visibility_from(info, "success")
                        with ui.button(icon="close", on_click=remove_row).props(
                            "round",
                        ):
                            ui.tooltip(_("Remove"))

        async def _add_task(
            self,
            name: str,
            content: Union[BinaryIO, aiofiles.threadpool.binary.AsyncBufferedReader],
        ) -> None:
            if app.storage.user["auto_detect_input_format"]:
                cur_suffix = name.rpartition(".")[-1].lower()
                if cur_suffix in plugin_manager.plugin_registry and cur_suffix != self.input_format:
                    self.input_format = cur_suffix
            upload_path = self.temp_path / name
            if isinstance(content, aiofiles.threadpool.binary.AsyncBufferedReader):
                await content.seek(0)
                upload_path.write_bytes(await content.read())
            else:
                content.seek(0)
                upload_path.write_bytes(content.read())
            output_path = self.temp_path / str(uuid.uuid4())
            conversion_task = ConversionTask(
                name=name,
                upload_path=upload_path,
                output_path=output_path,
                running=False,
                success=None,
                error=None,
                warning=None,
            )
            self.files_to_convert[name] = conversion_task
            self.tasks_container.refresh()

        async def add_task(self, args: UploadEventArguments) -> None:
            await self._add_task(args.name, args.content)

        @property  # type: ignore[no-redef]
        def input_format(self) -> str:
            return self._input_format

        @input_format.setter
        def input_format(self, value: str) -> None:
            if value != self._input_format:
                self._input_format = value
                if app.storage.user["reset_tasks_on_input_change"]:
                    self.files_to_convert.clear()
                app.storage.user["last_input_format"] = value
                input_plugin_info.refresh()
                input_panel_header.refresh()
                input_options.refresh()

        @property  # type: ignore[no-redef]
        def output_format(self) -> str:
            return self._output_format

        @output_format.setter
        def output_format(self, value: str) -> None:
            if value != self._output_format:
                self._output_format = value
                app.storage.user["last_output_format"] = value
                for task in self.files_to_convert.values():
                    task.reset()
                output_plugin_info.refresh()
                output_panel_header.refresh()
                output_options.refresh()

        @property
        def task_count(self) -> int:
            return len(self.files_to_convert)

        def convert_one(self, task: ConversionTask) -> None:
            task.reset()
            lazy_translation.set(translation)
            task.running = True
            try:
                with warnings.catch_warnings(record=True) as w:
                    warnings.simplefilter("always", BaseWarning)
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
                        task.success = False
                    else:
                        project = input_plugin.plugin_object.load(
                            task.upload_path,
                            input_option(**self.input_options),
                        )
                        task.output_path = task.output_path.with_suffix(
                            f".{self.output_format}",
                        )
                        for (
                            middleware_abbr,
                            enabled,
                        ) in self.middleware_enabled_states.model_dump().items():
                            if enabled:
                                middleware = middleware_manager.plugin_registry[middleware_abbr]
                                if middleware.plugin_object is not None and hasattr(
                                    middleware.plugin_object, "process"
                                ):
                                    middleware_option = getattr(
                                        self.middleware_options, middleware_abbr
                                    )
                                    project = middleware.plugin_object.process(
                                        project,
                                        middleware_option.model_validate(
                                            middleware_option, from_attributes=True
                                        ),
                                    )
                        output_plugin.plugin_object.dump(
                            task.output_path,
                            project,
                            output_option(**self.output_options),
                        )
                        task.success = True
                if len(w):
                    task.warning = "\n".join(str(warning.message) for warning in w)
            except Exception:
                task.success = False
                task.error = traceback.format_exc()
            task.running = False

        async def batch_convert(self) -> None:
            if app.storage.user["last_conversion_mode"] == ConversionMode.DIRECT.value:
                n = ui.notification(_("running"), timeout=0)

                loop = asyncio.get_event_loop()
                with ThreadPoolExecutor(
                    max_workers=max(len(self.files_to_convert), 4),
                ) as executor:
                    futures: list[asyncio.Future[None]] = [
                        loop.run_in_executor(
                            executor,
                            self.convert_one,
                            task,
                        )
                        for task in self.files_to_convert.values()
                    ]
                    for i, future in enumerate(asyncio.as_completed(futures)):
                        await future
                        n.message = _("Conversion Progress") + f" {i + 1} / {len(futures)}"
                        n.spinner = True
                n.close_button = _("Close")
                n.spinner = False
                if any(not task.success for task in self.files_to_convert.values()):
                    n.message = _("Conversion Failed")
                    n.type = "negative"
                else:
                    n.message = _("Conversion Successful")
                    n.type = "positive"

        def export_all(self, request: Request) -> Response:
            if result := self._export_all():
                return Response(*result)
            raise HTTPException(400, "No files to export")

        def export_one(self, request: Request) -> Response:
            if result := self._export_one(request.path_params["filename"]):
                return Response(*result)
            raise HTTPException(404, "File not found")

        def _export_one(self, filename: str) -> Optional[tuple[bytes, int, dict[str, str], str]]:
            if (task := self.files_to_convert.get(filename)) and task.success:
                return (
                    task.output_path.read_bytes(),
                    200,
                    {
                        "Content-Disposition": f"attachment; filename={quote(task.upload_path.with_suffix(task.output_path.suffix).name)}",
                    },
                    "application/octet-stream",
                )

        def _export_all(self) -> Optional[tuple[bytes, int, dict[str, str], str]]:
            if len(self.files_to_convert) == 0:
                return None
            elif len(self.files_to_convert) == 1:
                filename = next(iter(self.files_to_convert))
                return self._export_one(filename)
            buffer = io.BytesIO()
            with zipfile.ZipFile(buffer, "w") as zip_file:
                for task in self.files_to_convert.values():
                    if task.success:
                        zip_file.writestr(
                            task.upload_path.with_suffix(task.output_path.suffix).name,
                            task.output_path.read_bytes(),
                        )
            return (
                buffer.getvalue(),
                200,
                {"Content-Disposition": "attachment; filename=export.zip"},
                "application/zip",
            )

        async def add_upload(self) -> None:
            nonlocal select_input
            if app.native.main_window is not None and hasattr(
                app.native.main_window, "create_file_dialog"
            ):
                file_paths = await app.native.main_window.create_file_dialog(
                    allow_multiple=True,
                    file_types=[
                        select_input.options[select_input.value],
                        _("All files (*.*)"),
                    ],
                )
                if file_paths is None:  # Canceled
                    return
                for file_path in file_paths:
                    path = pathlib.Path(file_path)
                    async with aiofiles.open(path, "rb") as content:
                        await self._add_task(path.name, content)
            else:
                ui.run_javascript("add_upload()")

        async def save_file(self, file_name: str = "") -> None:
            nonlocal select_output
            if app.native.main_window is not None and hasattr(
                app.native.main_window, "create_file_dialog"
            ):
                import webview

                result = None
                result = self._export_one(file_name) if file_name else self._export_all()
                if result is None:
                    ui.notify(_("Save failed!"), type="negative")
                    return

                save_filename = unquote(
                    result[2]["Content-Disposition"].removeprefix("attachment; filename=")
                )
                save_path = await app.native.main_window.create_file_dialog(
                    webview.SAVE_DIALOG,
                    save_filename=save_filename,
                    file_types=(
                        _("Compressed Archive (*.zip)")
                        if save_filename.endswith(".zip")
                        else select_output.options[select_output.value],
                        _("All files (*.*)"),
                    ),
                )
                if save_path is None:  # Canceled
                    return
                elif not isinstance(save_path, str):  # list[str]
                    save_path = save_path[0]
                async with aiofiles.open(save_path, "wb") as content:
                    await content.write(result[0])
                ui.notify(_("Saved"), type="positive")
            else:
                ui.download(f"/export/{cur_client.id}/{file_name}")

    dark_toggler = ui.dark_mode().bind_value(app.storage.user, "dark_mode")
    selected_formats = SelectedFormats()
    ui.add_head_html(
        textwrap.dedent(
            """
        <style>
            .q-icon {
                justify-content: flex-end;
            }
        </style>
        """
        ).strip()
    )  # fix icon position

    def swap_values() -> None:
        selected_formats.input_format, selected_formats.output_format = (
            selected_formats.output_format,
            selected_formats.input_format,
        )

    with (
        ui.header(elevated=True)
        .style("background-color: curious-blue")
        .classes(
            "items-center",
        )
    ):
        convert_menu: Menu
        input_formats_menu: Menu
        output_formats_menu: Menu
        theme_menu: Menu
        lang_menu: Menu
        help_menu: Menu

        async def handle_key(e: KeyEventArguments) -> None:
            if e.modifiers.alt or e.modifiers.ctrl or e.modifiers.meta or e.modifiers.shift:
                if e.modifiers.alt and e.action.keyup and not e.action.repeat:
                    if e.key == "c":
                        convert_menu.open()
                    elif e.key == "[":
                        input_formats_menu.open()
                    elif e.key == "]":
                        output_formats_menu.open()
                    elif e.key == "t":
                        theme_menu.open()
                    elif e.key == "l":
                        lang_menu.open()
                    elif e.key == "h":
                        help_menu.open()
                    elif e.key == "o":
                        await selected_formats.add_upload()
                    elif e.key == "i":
                        about_dialog.open()
                    elif e.key == "\\":
                        swap_values()
                    elif e.key == "/":
                        selected_formats.reset()
                    elif e.key == "w":
                        dark_toggler.disable()
                    elif e.key == "b":
                        dark_toggler.enable()
                    elif e.key == "s":
                        dark_toggler.auto()
                    elif e.key == "Enter":
                        await selected_formats.batch_convert()
            elif e.key.number is not None and not e.action.repeat and e.action.keyup:
                key = e.key.number
                for formats_menu, format_item in [
                    (input_formats_menu, input_format_item),
                    (output_formats_menu, output_format_item),
                ]:
                    current_index = format_item._value_to_model_value(format_item.value)
                    count = len(format_item._values)
                    if formats_menu.value:
                        if count >= 10 + key:
                            next_focus = 10 * ((current_index // 10) + 1)
                            next_focus = key if next_focus + key >= count else next_focus + key
                            format_item.value = format_item._values[next_focus]
                        elif current_index != key:
                            format_item.value = format_item._values[key]

        ui.keyboard(on_key=handle_key, active=True)
        with ui.row():
            with ui.button(_("Convert"), on_click=lambda: convert_menu.open(), icon="loop"):
                ui.tooltip("Alt+C")
                with ui.menu() as convert_menu:
                    with ui.menu_item(
                        on_click=selected_formats.add_upload,
                    ):
                        ui.tooltip("Alt+O")
                        with ui.row().classes("items-center"):
                            ui.icon("file_open").classes("text-lg")
                            ui.label(_("Import project"))
                    with ui.menu_item(
                        on_click=selected_formats.batch_convert,
                    ).bind_visibility_from(
                        selected_formats,
                        "task_count",
                        backward=bool,
                    ):
                        ui.tooltip("Alt+Enter")
                        with ui.row().classes("items-center"):
                            ui.icon("play_arrow").classes("text-lg")
                            ui.label(_("Convert"))
                    with ui.menu_item(on_click=selected_formats.reset).bind_visibility_from(
                        selected_formats,
                        "task_count",
                        backward=bool,
                    ):
                        ui.tooltip("Alt+/")
                        with ui.row().classes("items-center"):
                            ui.icon("refresh").classes("text-lg")
                            ui.label(_("Clear Task List"))
                    ui.separator()
                    with ui.menu_item(on_click=swap_values):
                        ui.tooltip("Alt+\\")
                        with ui.row().classes("items-center"):
                            ui.icon("swap_vert").classes("text-lg")
                            ui.label(_("Swap Input and Output"))
            with ui.button(
                _("Import format"),
                on_click=lambda: input_formats_menu.open(),
                icon="login",
            ):
                ui.tooltip("Alt+[")
                with ui.menu() as input_formats_menu:
                    input_format_item = (
                        ui.radio(
                            {
                                k: f"{i} " + _(v["file_format"] or "") + " " + v["suffix"]
                                for i, (k, v) in enumerate(plugin_details.items())
                            },
                        )
                        .bind_value(selected_formats, "input_format")
                        .classes("text-sm")
                    )
            with ui.button(
                _("Export format"),
                on_click=lambda: output_formats_menu.open(),
                icon="logout",
            ):
                ui.tooltip("Alt+]")
                with ui.menu() as output_formats_menu:
                    output_format_item = ui.radio(
                        {
                            k: f"{i} " + _(v["file_format"] or "") + " " + v["suffix"]
                            for i, (k, v) in enumerate(plugin_details.items())
                        },
                    ).bind_value(selected_formats, "output_format")
            with ui.button(
                _("Switch Theme"),
                on_click=lambda: theme_menu.open(),
                icon="palette",
            ):
                ui.tooltip("Alt+T")
                with ui.menu() as theme_menu:
                    with ui.menu_item(on_click=dark_toggler.disable):
                        ui.tooltip("Alt+W")
                        with ui.row().classes("items-center"):
                            ui.icon("light_mode").classes("text-lg")
                            ui.label(_("Light"))
                    with ui.menu_item(on_click=dark_toggler.enable):
                        ui.tooltip("Alt+B")
                        with ui.row().classes("items-center"):
                            ui.icon("dark_mode").classes("text-lg")
                            ui.label(_("Dark"))
                    with ui.menu_item(on_click=dark_toggler.auto):
                        ui.tooltip("Alt+S")
                        with ui.row().classes("items-center"):
                            ui.icon("brightness_auto").classes("text-lg")
                            ui.label(_("System"))
            with ui.button(
                _("Switch Language"),
                on_click=lambda: lang_menu.open(),
                icon="language",
            ):
                ui.tooltip("Alt+L")
                with ui.menu() as lang_menu:
                    ui.menu_item(
                        "简体中文",
                        on_click=lambda: ui.navigate.to("/?lang=zh_CN")
                        if lang != "zh_CN"
                        else None,
                    )
                    ui.menu_item(
                        "English",
                        on_click=lambda: ui.navigate.to("/?lang=en_US")
                        if lang != "en_US"
                        else None,
                    )
                    ui.menu_item("日本語").props("disabled")
            with ui.dialog() as about_dialog, ui.card():
                ui.label(_("About")).classes("text-lg")
                with ui.column().classes("text-center w-full"):
                    ui.label(_("LibreSVIP")).classes("text-h4 font-bold w-full")
                    ui.label(_("Version: ") + libresvip.__version__).classes(
                        "text-md w-full",
                    )
                    ui.label(_("Author: SoulMelody")).classes("text-md w-full")
                    with ui.row().classes("w-full justify-center"):
                        with ui.element("q-chip").props("icon=live_tv"):
                            ui.link(
                                _("Author's Profile"),
                                "https://space.bilibili.com/175862486",
                                new_tab=True,
                            )
                        with ui.element("q-chip").props("icon=logo_dev"):
                            ui.link(
                                _("Repo URL"),
                                "https://github.com/SoulMelody/LibreSVIP",
                                new_tab=True,
                            )
                    ui.label(
                        _(
                            "LibreSVIP is an open-sourced, liberal and extensionable framework that can convert your singing synthesis projects between different file formats.",
                        ),
                    ).classes("text-md w-full")
                    ui.label(
                        _(
                            "All people should have the right and freedom to choose. That's why we're committed to giving you a second chance to keep your creations free from the constraints of platforms and coterie.",
                        ),
                    ).classes("text-md w-full")
                with ui.card_actions().props("align=right").classes("w-full"):
                    ui.button(_("Close"), on_click=about_dialog.close)
            with ui.button(_("Help"), on_click=lambda: help_menu.open(), icon="help"):
                ui.tooltip("Alt+H")
                with ui.menu() as help_menu:
                    with ui.menu_item(on_click=about_dialog.open):
                        ui.tooltip("Alt+I")
                        with ui.row().classes("items-center"):
                            ui.icon("info").classes("text-lg")
                            ui.label(_("About"))
                    with ui.menu_item(), ui.row().classes("items-center"):
                        ui.icon("text_snippet").classes("text-lg")
                        ui.link(
                            _("Documentation"),
                            target="https://soulmelody.github.io/LibreSVIP",
                            new_tab=True,
                        )
        with ui.tabs().classes("w-full sm:visible lg:h-0 lg:invisible") as tabs:
            format_select_tab = ui.tab(_("Select File Formats"))
            options_tab = ui.tab(_("Advanced Settings"))
    uploader = ui.upload(
        multiple=True,
        on_upload=selected_formats.add_task,
        auto_upload=True,
    ).props("hidden")

    def file_format_area() -> None:
        nonlocal select_input, select_output
        with ui.column().classes("w-full"):
            ui.label(_("Choose file format")).classes(
                "text-h5 font-bold",
            )
            with ui.grid().classes(
                "grid grid-cols-11 gap-4 w-full",
            ):
                select_input = (
                    ui.select(
                        {
                            k: _(v["file_format"] or "") + " " + v["suffix"]
                            for k, v in plugin_details.items()
                        },
                        label=_("Import format"),
                    )
                    .classes("col-span-10")
                    .bind_value(selected_formats, "input_format")
                )
                with ui.dialog() as input_info, ui.card():
                    input_plugin_info()
                    with (
                        ui.card_actions()
                        .props(
                            "align=right",
                        )
                        .classes("w-full")
                    ):
                        ui.button(
                            _("Close"),
                            on_click=input_info.close,
                        )
                with ui.button(
                    icon="info",
                    on_click=input_info.open,
                ).classes(
                    "min-w-[45px] max-w-[45px] aspect-square",
                ):
                    ui.tooltip(_("View Detail Information"))
                ui.switch(_("Auto detect import format")).classes(
                    "col-span-5",
                ).bind_value(
                    app.storage.user,
                    "auto_detect_input_format",
                )
                ui.switch(
                    _("Reset list when import format changed"),
                ).classes("col-span-5").bind_value(
                    app.storage.user,
                    "reset_tasks_on_input_change",
                )
                with (
                    ui.button(
                        icon="swap_vert",
                        on_click=swap_values,
                    )
                    .classes("w-fit aspect-square")
                    .props("round")
                ):
                    ui.tooltip(_("Swap Input and Output"))
                select_output = (
                    ui.select(
                        {
                            k: _(v["file_format"] or "") + " " + v["suffix"]
                            for k, v in plugin_details.items()
                        },
                        label=_("Export format"),
                    )
                    .classes("col-span-10")
                    .bind_value(selected_formats, "output_format")
                )
                with (
                    ui.dialog().classes(
                        "h-400 w-600",
                    ) as output_info,
                    ui.card(),
                ):
                    output_plugin_info()
                    with (
                        ui.card_actions()
                        .props(
                            "align=right",
                        )
                        .classes("w-full")
                    ):
                        ui.button(
                            _("Close"),
                            on_click=output_info.close,
                        )
                with ui.button(
                    icon="info",
                    on_click=output_info.open,
                ).classes(
                    "min-w-[45px] max-w-[45px] aspect-square",
                ):
                    ui.tooltip(_("View Detail Information"))

    def tasks_area() -> None:
        with ui.card().classes("w-full h-full") as tasks_card:
            # ui.label(_("Import project")).classes("text-h5 font-bold")
            with ui.tabs().classes("w-full") as conversion_mode_tabs:
                direct = ui.tab("Direct", _("Direct"))
                merge = ui.tab("Merge", _("Merge"))
                split = ui.tab("Split", _("Split"))
            with (
                ui.tab_panels(conversion_mode_tabs, value=app.storage.user["last_conversion_mode"])
                .classes("w-full")
                .bind_value(app.storage.user, "last_conversion_mode")
            ):
                with ui.tab_panel(direct):
                    selected_formats.tasks_container()
                with ui.tab_panel(merge):
                    pass
                with ui.tab_panel(split):
                    pass
            tasks_card.bind_visibility_from(
                selected_formats,
                "task_count",
                backward=bool,
            )
            tasks_card.on(
                "dragover",
                js_handler="""(event) => {
                event.preventDefault()
            }""",
            )
            tasks_card.on(
                "drop",
                js_handler=f"""(event) => {{
                for (let file of event.dataTransfer.files) {{
                    let file_name = file.name
                    post_form('{uploader._props['url']}', {{
                        file_name: file
                    }})
                }}
                event.preventDefault()
            }}""",
            )
            with QFab(
                icon="construction",
            ).classes("absolute bottom-0 left-0 m-2 z-10") as fab:
                with fab.add_slot("active-icon"):
                    ui.icon("construction").classes("rotate-45")
                fab.on(
                    "mouseenter",
                    functools.partial(fab.run_method, "show"),
                )
                QFabAction(
                    icon="refresh",
                    on_click=selected_formats.reset,
                ).tooltip(_("Clear Task List"))
                QFabAction(
                    icon="filter_alt_off",
                    on_click=selected_formats.filter_input_ext,
                ).tooltip(_("Remove Tasks With Other Extensions"))
            with (
                ui.button(
                    icon="add",
                    on_click=selected_formats.add_upload,
                )
                .props("round")
                .classes(
                    "absolute bottom-0 right-2 m-2 z-10",
                )
            ):
                ui.badge().props(
                    "floating color=orange",
                ).bind_text_from(
                    selected_formats,
                    "task_count",
                    backward=str,
                )
                ui.tooltip(_("Continue Adding files"))
        with (
            ui.card()
            .classes(
                "w-full h-full opacity-60 hover:opacity-100 flex items-center justify-center border-dashed border-2 border-indigo-300 hover:border-indigo-500",
            )
            .style("cursor: pointer") as upload_card
        ):
            upload_card.on(
                "dragover",
                js_handler="""(event) => {
                event.preventDefault()
            }""",
            )
            upload_card.on(
                "drop",
                js_handler=f"""(event) => {{
                for (let file of event.dataTransfer.files) {{
                    let file_name = file.name
                    post_form('{uploader._props['url']}', {{
                        file_name: file
                    }})
                }}
                event.preventDefault()
            }}""",
            )
            upload_card.on("click", selected_formats.add_upload)
            upload_card.bind_visibility_from(
                selected_formats,
                "task_count",
                backward=not_,
            )
            ui.icon("file_upload").classes("text-6xl")
            ui.label(
                _("Drag and drop files here or click to upload"),
            ).classes("text-lg")

    def options_area() -> None:
        with ui.scroll_area().classes("w-full h-full"):
            with ui.row().classes("absolute top-0 right-2 m-2 z-10"):
                with (
                    ui.button(
                        icon="play_arrow",
                        on_click=selected_formats.batch_convert,
                    )
                    .props("round")
                    .bind_visibility_from(
                        selected_formats,
                        "task_count",
                        backward=bool,
                    )
                ):
                    ui.tooltip(_("Start Conversion"))
                with (
                    ui.button(
                        icon="download_for_offline",
                        on_click=selected_formats.save_file,
                    )
                    .props("round")
                    .bind_visibility_from(
                        selected_formats,
                        "task_count",
                        backward=bool,
                    )
                ):
                    ui.tooltip(_("Export"))
            ui.label(_("Advanced Options")).classes("text-h5 font-bold")
            with ui.expansion().classes("w-full") as import_panel:
                with import_panel.add_slot("header"):
                    input_panel_header()
                input_options()
            ui.separator()
            with ui.expansion().classes("w-full") as middleware_panel:
                with middleware_panel.add_slot("header"), ui.row().classes("w-full items-center"):
                    ui.icon("auto_fix_high").classes("text-lg")
                    ui.label(_("Intermediate Processing")).classes("text-subtitle1 font-bold")
                for middleware in middleware_manager.plugin_registry.values():
                    with ui.row().classes("items-center w-full"):
                        middleware_toggler = (
                            ui.switch(_(middleware.name))
                            .props("color=green")
                            .bind_value(
                                selected_formats.middleware_enabled_states, middleware.identifier
                            )
                        )
                        if middleware.description:
                            ui.space()
                            with (
                                ui.icon("help_outline")
                                .classes("text-3xl")
                                .style(
                                    "cursor: help",
                                )
                            ):
                                ui.tooltip(_(middleware.description))
                    middleware_options_form(middleware.identifier, middleware_toggler)
            ui.separator()
            with ui.expansion().classes("w-full") as export_panel:
                with export_panel.add_slot("header"):
                    output_panel_header()
                output_options()

    with ui.card().classes("w-full min-w-80").style("height: calc(100vh - 120px)"):
        with ui.splitter(limits=(40, 60)).classes(
            "w-full h-0 sm:invisible lg:h-full lg:visible"
        ) as main_splitter:
            with (
                main_splitter.before,
                ui.splitter(limits=(40, 50), horizontal=True) as left_splitter,
            ):
                with left_splitter.before, ui.card().classes("h-full w-full"):
                    file_format_area()
                with left_splitter.after:
                    tasks_area()
            with main_splitter.after:
                options_area()
        with (
            ui.card().classes("w-full h-full sm:visible lg:h-0 lg:invisible"),
            ui.tab_panels(tabs, value=format_select_tab).classes("h-full w-full"),
        ):
            with (
                ui.tab_panel(format_select_tab),
                ui.splitter(limits=(60, 60), horizontal=True, value=60).classes(
                    "h-full w-full"
                ) as format_select_splitter,
            ):
                with format_select_splitter.before, ui.card().classes("h-full w-full"):
                    file_format_area()
                with format_select_splitter.after:
                    tasks_area()
            with (
                ui.tab_panel(options_tab),
                ui.splitter(limits=(50, 60), horizontal=True).classes(
                    "h-full w-full"
                ) as options_splitter,
            ):
                with options_splitter.before:
                    options_area()
                with options_splitter.after:
                    tasks_area()
    with ui.footer().classes("bg-transparent"):
        ajax_bar = ui.element("q-ajax-bar").props("position=bottom")

    def add_javascript() -> None:
        nonlocal select_input
        ui.add_body_html(
            textwrap.dedent(
                f"""
            <script>
                function get_element(element_id) {{
                    let element = getElement(element_id)
                    if (element.$refs.qRef !== undefined)
                        return element.$refs.qRef
                    return element
                }}
                function post_form(url, data) {{
                    let ajax_bar = get_element({ajax_bar.id})
                    let form_data = new FormData()
                    for (let key in data) {{
                        form_data.append(key, data[key])
                    }}
                    var xhr = new XMLHttpRequest();
                    var progress = 0
                    xhr.onreadystatechange = function() {{
                        if (xhr.readyState === 4) {{
                            ajax_bar.stop()
                        }}
                    }}
                    xhr.upload.onprogress = function(event) {{
                        if (event.lengthComputable) {{
                            let next = event.loaded / event.total * 100
                            if (next - progress > 0.5) {{
                                ajax_bar.increment(next - progress)
                                progress = next
                            }}
                        }}
                    }}
                    xhr.open('POST', url, true);
                    ajax_bar.start()
                    xhr.send(form_data);
                }}
                function add_upload() {{
                    if (window.showOpenFilePicker) {{
                        let format_desc = get_element({select_input.id}).modelValue.label
                        let suffix = format_desc.match(/\\((?:\\*)(\\..*?)\\)/)[1]
                        let bracket_index = format_desc.lastIndexOf('(')
                        let file_format = format_desc.substr(0, bracket_index === -1 ? format_desc.length : bracket_index)
                        window.showOpenFilePicker(
                            {{
                                types: [
                                    {{
                                        description: file_format,
                                        accept: {{
                                            '*/*': [suffix],
                                        }}
                                    }}
                                ],
                                multiple: true
                            }}
                        ).then(async function (fileHandles) {{
                            for (const fileHandle of fileHandles) {{
                                const file = await fileHandle.getFile();
                                let file_name = file.name
                                post_form('{uploader._props['url']}', {{
                                    file_name: file
                                }})
                            }}
                        }});
                    }} else {{
                        get_element({uploader.id}).pickFiles()
                    }}
                }}
            </script>
            """,
            ).strip(),
        )

    add_javascript()


def main() -> None:
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--host", type=str, default="127.0.0.1")
    arg_parser.add_argument("--port", type=int, default=8080)
    arg_parser.add_argument("--reload", action="store_true")
    arg_parser.add_argument("--server", action="store_true")
    arg_parser.add_argument("--daemon", action="store_true")
    args, argv = arg_parser.parse_known_args()

    secrets_path = app_dir.user_config_path / "secrets.txt"
    if not secrets_path.exists():
        secrets_path.parent.mkdir(parents=True, exist_ok=True)
        secrets_path.write_text(secrets.token_urlsafe(32))
    storage_secret = secrets_path.read_text()

    ui.run(
        show=not args.daemon,
        window_size=None if args.server else (1200, 800),
        reload=args.reload,
        host=args.host if args.server else None,
        port=args.port,
        storage_secret=storage_secret,
        title="LibreSVIP",
        favicon=res_dir / "libresvip.ico",
        uvicorn_reload_includes="*.py,*.txt,*.yapsy-plugin,*.mo",
    )
