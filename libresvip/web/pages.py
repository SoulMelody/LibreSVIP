import argparse
import asyncio
import dataclasses
import enum
import functools
import io
import math
import pathlib
import platform
import re
import secrets
import shutil
import textwrap
import traceback
import uuid
import webbrowser
import zipfile
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from operator import not_
from typing import (
    TYPE_CHECKING,
    BinaryIO,
    Optional,
    SupportsFloat,
    TypeVar,
    Union,
    get_args,
    get_type_hints,
)
from urllib.parse import quote, unquote

import aiofiles
import more_itertools
from nicegui import app, binding, ui
from nicegui.context import context
from nicegui.elements.switch import Switch
from nicegui.events import (
    GenericEventArguments,
    KeyEventArguments,
    UploadEventArguments,
    ValueChangeEventArguments,
)
from nicegui.storage import request_contextvar
from pydantic import RootModel, create_model
from pydantic.config import JsonValue
from pydantic.dataclasses import dataclass
from pydantic_core import PydanticUndefined
from pydantic_extra_types.color import Color
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response
from typing_extensions import ParamSpec
from upath import UPath

import libresvip
from libresvip.core.compat import as_file
from libresvip.core.config import (
    ConversionMode,
    DarkMode,
    Language,
    LibreSvipBaseUISettings,
    LyricsReplacement,
    LyricsReplaceMode,
    ui_settings_ctx,
)
from libresvip.core.constants import app_dir, res_dir
from libresvip.core.warning_types import CatchWarnings
from libresvip.extension.manager import (
    get_translation,
    middleware_manager,
    plugin_manager,
)
from libresvip.model.base import BaseComplexModel, Project
from libresvip.utils.search import find_index
from libresvip.utils.text import shorten_error_message, supported_charset_names
from libresvip.utils.translation import gettext_lazy as _
from libresvip.utils.translation import lazy_translation
from libresvip.web.elements import QFab, QFabAction

if TYPE_CHECKING:
    from nicegui.elements.select import Select

binding.MAX_PROPAGATION_TIME = 0.03


P = ParamSpec("P")
R = TypeVar("R")


@dataclass
class LibreSvipWebUserSettings(LibreSvipBaseUISettings):
    def __post_init__(self) -> None:
        self.lyric_replace_rules.setdefault("default", [])
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


def str2dark_mode(value: Optional[bool]) -> DarkMode:
    return {
        True: DarkMode.DARK,
        False: DarkMode.LIGHT,
        None: DarkMode.SYSTEM,
    }.get(value, DarkMode.SYSTEM)


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
            if self.output_path.is_dir():
                self.output_path.rmdir()
            else:
                self.output_path.unlink()

    def __del__(self) -> None:
        if app.native.main_window is None and self.upload_path.exists():
            self.upload_path.unlink()
        if self.output_path.exists():
            if self.output_path.is_dir():
                self.output_path.rmdir()
            else:
                self.output_path.unlink()


def export_all(request: Request) -> Response:
    if selected_formats := getattr(
        app.state, f"{request.path_params['client_id']}_selected_formats"
    ):
        return selected_formats.export_all(request)
    else:
        return Response(
            "No selected formats",
            status_code=400,
        )


app.add_route("/export/{client_id}/", export_all, methods=["GET"])


def export_one(request: Request) -> Response:
    if selected_formats := getattr(
        app.state, f"{request.path_params['client_id']}_selected_formats"
    ):
        return selected_formats.export_one(request)
    else:
        return Response(
            "No selected formats",
            status_code=400,
        )


app.add_route("/export/{client_id}/{filename}", export_one, methods=["GET"])

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


@ui.page("/")
@ui.page("/?lang={lang}")
def page_layout(lang: Optional[str] = None) -> None:
    settings: LibreSvipBaseUISettings

    if app.native.main_window is not None:
        from libresvip.core.config import save_settings, settings

        if lang is not None:
            settings.language = Language.from_locale(lang)

        app.on_shutdown(save_settings)
    else:
        settings = LibreSvipWebUserSettings()
        request = request_contextvar.get()
        session_id = request.session["id"]

        for key, value in app.storage.user.items():
            if hasattr(settings, key):
                if key == "dark_mode":
                    value = str2dark_mode(value)
                elif key == "language":
                    value = Language.from_locale(value)
                setattr(settings, key, value)

        def save_settings() -> None:
            if session_id in app.storage._users:
                storage = app.storage._users[session_id]
                default_settings_dict = RootModel[LibreSvipWebUserSettings](settings).model_dump(
                    mode="json"
                )

                for key, default_value in default_settings_dict.items():
                    if key == "dark_mode":
                        default_value = dark_mode2str(default_value)
                    if key not in storage or storage[key] != default_value:
                        storage[key] = default_value

        context.client.on_disconnect(save_settings)

    translation = get_translation()

    def set_context_vars() -> None:
        lazy_translation.set(translation)
        if app.native.main_window is not None:
            ui_settings_ctx.set(settings)

    def context_vars_wrapper(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            set_context_vars()
            return func(*args, **kwargs)

        return wrapper

    set_context_vars()

    @context_vars_wrapper
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
                    with ui.element("q-chip").props("icon=tag").tooltip(_("Version")):
                        ui.label(plugin_details[attr]["version"])
                    ui.separator().props("vertical")
                    with (
                        ui.element("q-chip")
                        .props("icon=person")
                        .tooltip(plugin_details[attr]["website"]),
                        ui.row().classes("items-center"),
                    ):
                        ui.label(_("Author") + ": ")
                        ui.link(
                            plugin_details[attr]["author"],
                            plugin_details[attr]["website"],
                            new_tab=True,
                        )
                        ui.icon("open_in_new")
                with ui.element("q-chip").props("icon=outline_insert_drive_file"):
                    ui.label(
                        _(plugin_details[attr]["file_format"] or "")
                        + " "
                        + (plugin_details[attr]["suffix"] or ""),
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

    @context_vars_wrapper
    def options_form(attr_prefix: str, method: str) -> None:
        attr = getattr(selected_formats, attr_prefix + "_format")
        conversion_plugin = plugin_manager.plugin_registry[attr]
        option_class = None
        if hasattr(conversion_plugin.plugin_object, method) and (
            _option_class := get_type_hints(
                getattr(conversion_plugin.plugin_object, method),
            ).get("options")
        ):
            option_class = _option_class
        if not option_class:
            return
        option_dict = getattr(selected_formats, attr_prefix + "_options")
        option_dict.clear()
        option_dict.update(option_class().model_dump())
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
                    elif option_key in ["encoding", "lyric_encoding"]:
                        choices = {charset: charset for charset in supported_charset_names()}
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
                            option_dict[option_key] = default_value
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
                        ui.icon("help_outline").classes("text-3xl").style(
                            "cursor: help",
                        ).tooltip(_(field_info.description))

    input_options = ui.refreshable(functools.partial(options_form, "input", "load"))

    output_options = ui.refreshable(functools.partial(options_form, "output", "dump"))

    @context_vars_wrapper
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
                    elif option_key == "lyric_replacement_preset_name":
                        choices = {preset: preset for preset in settings.lyric_replace_rules}
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
                            option_dict[option_key] = default_value
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
                        ui.icon("help_outline").classes("text-3xl").style(
                            "cursor: help",
                        ).tooltip(_(field_info.description))

    select_input: Select
    select_output: Select

    def _input_format_factory() -> str:
        return (
            settings.last_input_format
            if settings.last_input_format is not None
            else next(
                iter(plugin_manager.plugin_registry),
                "",
            )
        )

    def _output_format_factory() -> str:
        return (
            settings.last_output_format
            if settings.last_output_format is not None
            else next(
                iter(plugin_manager.plugin_registry),
                "",
            )
        )

    @dataclasses.dataclass
    class SelectedFormats:
        _input_format: str = dataclasses.field(default_factory=_input_format_factory)
        _output_format: str = dataclasses.field(default_factory=_output_format_factory)
        _conversion_mode: ConversionMode = dataclasses.field(default=ConversionMode.DIRECT)
        current_preset: str = dataclasses.field(default="default")
        input_options: dict[str, JsonValue] = dataclasses.field(default_factory=dict)
        output_options: dict[str, JsonValue] = dataclasses.field(default_factory=dict)
        files_to_convert: dict[str, ConversionTask] = dataclasses.field(
            default_factory=dict,
        )

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

        @functools.cached_property
        def temp_path(self) -> UPath:
            user_temp_path = UPath("memory:/") / f"{context.client.id}"
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
        @context_vars_wrapper
        def tasks_container(self) -> None:
            with ui.scroll_area().classes("w-full"):
                for i, info in enumerate(self.files_to_convert.values()):
                    with ui.row().classes("w-full items-center"):

                        def remove_row() -> None:
                            del self.files_to_convert[info.name]
                            self.tasks_container.refresh()

                        ui.label(info.name).classes("flex-grow")
                        if self._conversion_mode == ConversionMode.MERGE and i:
                            ui.icon("merge", size="lg")
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
                                        f"navigator.clipboard.writeText({info.error!r})",
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
                                        f"navigator.clipboard.writeText({info.warning!r})",
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
                        ui.button(icon="close", on_click=remove_row).props(
                            "round",
                        ).tooltip(_("Remove"))

        @property
        def input_format(self) -> str:
            return self._input_format

        @input_format.setter
        def input_format(self, value: str) -> None:
            if value != self._input_format:
                self._input_format = value
                if settings.reset_tasks_on_input_change:
                    self.files_to_convert.clear()
                settings.last_input_format = value
                input_plugin_info.refresh()
                input_panel_header.refresh()
                input_options.refresh()

        @property
        def output_format(self) -> str:
            return self._output_format

        @output_format.setter
        def output_format(self, value: str) -> None:
            if value != self._output_format:
                self._output_format = value
                settings.last_output_format = value
                for task in self.files_to_convert.values():
                    task.reset()
                output_plugin_info.refresh()
                output_panel_header.refresh()
                output_options.refresh()

        @context_vars_wrapper
        async def _add_task(
            self,
            name: str,
            content: Union[BinaryIO, pathlib.Path],
        ) -> None:
            if settings.auto_detect_input_format:
                cur_suffix = name.rpartition(".")[-1].lower()
                if cur_suffix in plugin_manager.plugin_registry and cur_suffix != self.input_format:
                    self.input_format = cur_suffix
            if isinstance(content, pathlib.Path):
                upload_path = content
            else:
                upload_path = self.temp_path / name
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

        @property
        def conversion_mode(self) -> str:
            return self._conversion_mode.value

        @conversion_mode.setter
        def conversion_mode(self, value: str) -> None:
            if value != self._conversion_mode.value:
                self._conversion_mode = ConversionMode(value)
                for task in self.files_to_convert.values():
                    task.reset()
                self.tasks_container.refresh()

        @property
        def task_count(self) -> int:
            return len(self.files_to_convert)

        @context_vars_wrapper
        def convert_one(self, task: ConversionTask, *sub_tasks: list[ConversionTask]) -> None:
            task.reset()
            task.running = True
            try:
                with CatchWarnings() as w:
                    input_plugin = plugin_manager.plugin_registry[self.input_format]
                    output_plugin = plugin_manager.plugin_registry[self.output_format]
                    if (
                        input_plugin.plugin_object is None
                        or (
                            input_option_class := get_type_hints(
                                input_plugin.plugin_object.load
                            ).get(
                                "options",
                            )
                        )
                        is None
                        or output_plugin.plugin_object is None
                        or (
                            output_option_class := get_type_hints(
                                output_plugin.plugin_object.dump,
                            ).get("options")
                        )
                        is None
                    ):
                        task.success = False
                    else:
                        input_option = input_option_class(**self.input_options)
                        if self._conversion_mode == ConversionMode.MERGE:
                            child_projects = [
                                input_plugin.plugin_object.load(
                                    sub_task.upload_path,
                                    input_option,
                                )
                                for sub_task in more_itertools.value_chain(task, sub_tasks)
                            ]
                            project = Project.merge_projects(child_projects)
                        else:
                            project = input_plugin.plugin_object.load(
                                task.upload_path,
                                input_option,
                            )
                        if self._conversion_mode != ConversionMode.SPLIT:
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
                                        self.middleware_options,
                                        middleware_abbr,
                                    )
                                    project = middleware.plugin_object.process(
                                        project,
                                        middleware_option.model_validate(
                                            middleware_option,
                                            from_attributes=True,
                                        ),
                                    )
                        output_option = output_option_class(**self.output_options)
                        if self._conversion_mode == ConversionMode.SPLIT:
                            task.output_path.mkdir(parents=True, exist_ok=True)
                            for i, child_project in enumerate(
                                project.split_tracks(settings.max_track_count)
                            ):
                                output_plugin.plugin_object.dump(
                                    task.output_path
                                    / f"{task.upload_path.stem}_{i + 1:0=2d}.{self.output_format}",
                                    child_project,
                                    output_option,
                                )
                        else:
                            output_plugin.plugin_object.dump(
                                task.output_path,
                                project,
                                output_option,
                            )
                        task.success = True
                if w.output:
                    task.warning = w.output
            except Exception:
                task.success = False
                task.error = traceback.format_exc()
            task.running = False

        @context_vars_wrapper
        async def batch_convert(self) -> None:
            loop = asyncio.get_event_loop()
            running_tasks = []
            with ThreadPoolExecutor(
                max_workers=max(len(self.files_to_convert), 4),
            ) as executor:
                futures: list[asyncio.Future[None]]
                if self._conversion_mode == ConversionMode.MERGE:
                    (task,), other_tasks = more_itertools.spy(self.files_to_convert.values())
                    futures = [
                        loop.run_in_executor(
                            executor,
                            self.convert_one,
                            task,
                            *other_tasks,
                        )
                    ]
                    running_tasks.append(task)
                else:
                    running_tasks = list(self.files_to_convert.values())
                    futures = [
                        loop.run_in_executor(
                            executor,
                            self.convert_one,
                            task,
                        )
                        for task in running_tasks
                    ]
                for i, future in enumerate(asyncio.as_completed(futures)):
                    await future
            if any(not task.success for task in running_tasks):
                ui.notification(_("Conversion Failed"), type="negative")
            else:
                ui.notification(_("Conversion Successful"), type="positive")

        def export_all(self, request: Request) -> Response:
            if result := self._export_all():
                return Response(*result)
            raise HTTPException(400, "No files to export")

        def export_one(self, request: Request) -> Response:
            if result := self._export_one(request.path_params["filename"]):
                return Response(*result)
            raise HTTPException(404, "File not found")

        def _export_one(self, filename: str) -> Optional[tuple[bytes, int, dict[str, str], str]]:
            if not (task := self.files_to_convert.get(filename)) or not task.success:
                return None
            if self._conversion_mode == ConversionMode.SPLIT:
                buffer = io.BytesIO()
                with zipfile.ZipFile(buffer, "w") as zip_file:
                    for i, child_file in enumerate(task.output_path.iterdir()):
                        if not child_file.is_file():
                            continue
                        zip_file.writestr(
                            child_file.name,
                            child_file.read_bytes(),
                        )
                content = buffer.getvalue()
                filename_header = quote(task.upload_path.with_suffix(".zip").name)
            else:
                content = task.output_path.read_bytes()
                filename_header = quote(task.upload_path.with_suffix(task.output_path.suffix).name)
            return (
                content,
                200,
                {
                    "Content-Disposition": f"attachment; filename={filename_header}",
                },
                "application/octet-stream",
            )

        def _export_all(
            self,
        ) -> Optional[tuple[bytes, int, dict[str, str], str]]:
            if len(self.files_to_convert) == 0:
                return None
            elif len(self.files_to_convert) == 1:
                filename = next(iter(self.files_to_convert))
                return self._export_one(filename)
            buffer = io.BytesIO()
            with zipfile.ZipFile(buffer, "w") as zip_file:
                for task in self.files_to_convert.values():
                    if task.success:
                        if task.output_path.is_dir():
                            for i, child_file in enumerate(task.output_path.iterdir()):
                                if not child_file.is_file():
                                    continue
                                zip_file.writestr(
                                    child_file.name,
                                    child_file.read_bytes(),
                                )
                        else:
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

        @context_vars_wrapper
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
                    await self._add_task(path.name, path)
            else:
                ui.run_javascript("add_upload()")

        @context_vars_wrapper
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
                ui.download(f"/export/{context.client.id}/{file_name}")

    dark_toggler = ui.dark_mode().bind_value(
        settings, "dark_mode", forward=str2dark_mode, backward=dark_mode2str
    )
    selected_formats = SelectedFormats()
    if app.native.main_window is None:
        setattr(
            app.state,
            f"{context.client.id}_selected_formats",
            selected_formats,
        )

        def recycle_state() -> None:
            delattr(app.state, f"{context.client.id}_selected_formats")

        context.client.on_disconnect(recycle_state)
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

    ui.colors(
        primary="#3F51B5",
        secondary="#5C6BC0",
        accent="#8A72AC",
        dark="#212121",
        positive="#28A745",
        negative="#D32F2F",
        info="#536DFE",
        warning="#FFB74D",
    )
    with (
        ui.header(elevated=True)
        .style("background-color: primary")
        .classes(
            "items-center pywebview-drag-region",
        )
    ):
        with ui.row().classes("w-full"):
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
            with QFab(icon="menu").props("square direction=down vertical-actions-align=left"):
                with (
                    QFabAction(
                        _("Convert"),
                        icon="loop",
                        on_click=lambda: convert_menu.open(),
                    )
                    .props("square")
                    .tooltip("Alt+C"),
                    ui.menu() as convert_menu,
                ):
                    with (
                        ui.menu_item(
                            on_click=selected_formats.add_upload,
                        ).tooltip("Alt+O"),
                        ui.row().classes("items-center"),
                    ):
                        ui.icon("file_open").classes("text-lg")
                        ui.label(_("Import project"))
                    with (
                        ui.menu_item(
                            on_click=selected_formats.batch_convert,
                        )
                        .bind_visibility_from(
                            selected_formats,
                            "task_count",
                            backward=bool,
                        )
                        .tooltip("Alt+Enter"),
                        ui.row().classes("items-center"),
                    ):
                        ui.icon("play_arrow").classes("text-lg")
                        ui.label(_("Convert"))
                    with (
                        ui.menu_item(on_click=selected_formats.reset)
                        .bind_visibility_from(
                            selected_formats,
                            "task_count",
                            backward=bool,
                        )
                        .tooltip("Alt+/"),
                        ui.row().classes("items-center"),
                    ):
                        ui.icon("refresh").classes("text-lg")
                        ui.label(_("Clear Task List"))
                    ui.separator()
                    with (
                        ui.menu_item(on_click=swap_values).tooltip("Alt+\\"),
                        ui.row().classes("items-center"),
                    ):
                        ui.icon("swap_vert").classes("text-lg")
                        ui.label(_("Swap Input and Output"))
                with (
                    QFabAction(
                        _("Import format"),
                        icon="login",
                        on_click=lambda: input_formats_menu.open(),
                    )
                    .props("square")
                    .tooltip("Alt+["),
                    ui.menu() as input_formats_menu,
                ):
                    input_format_item = (
                        ui.radio(
                            {
                                k: f"{i} " + _(v["file_format"] or "") + " " + (v["suffix"] or "")
                                for i, (k, v) in enumerate(plugin_details.items())
                            },
                        )
                        .bind_value(selected_formats, "input_format")
                        .classes("text-sm")
                    )
                with (
                    QFabAction(
                        _("Export format"),
                        icon="logout",
                        on_click=lambda: output_formats_menu.open(),
                    )
                    .props("square")
                    .tooltip("Alt+]"),
                    ui.menu() as output_formats_menu,
                ):
                    output_format_item = ui.radio(
                        {
                            k: f"{i} " + _(v["file_format"] or "") + " " + (v["suffix"] or "")
                            for i, (k, v) in enumerate(plugin_details.items())
                        },
                    ).bind_value(selected_formats, "output_format")
                with (
                    QFabAction(
                        _("Switch Theme"),
                        icon="palette",
                        on_click=lambda: theme_menu.open(),
                    )
                    .props("square")
                    .tooltip("Alt+T"),
                    ui.menu() as theme_menu,
                ):
                    with (
                        ui.menu_item(on_click=dark_toggler.disable).tooltip("Alt+W"),
                        ui.row().classes("items-center"),
                    ):
                        ui.icon("light_mode").classes("text-lg")
                        ui.label(_("Light"))
                    with (
                        ui.menu_item(on_click=dark_toggler.enable).tooltip("Alt+B"),
                        ui.row().classes("items-center"),
                    ):
                        ui.icon("dark_mode").classes("text-lg")
                        ui.label(_("Dark"))
                    with (
                        ui.menu_item(on_click=dark_toggler.auto).tooltip("Alt+A"),
                        ui.row().classes("items-center"),
                    ):
                        ui.icon("brightness_auto").classes("text-lg")
                        ui.label(_("System"))
                with (
                    QFabAction(
                        _("Help"),
                        icon="help",
                        on_click=lambda: help_menu.open(),
                    )
                    .props("square")
                    .tooltip("Alt+H"),
                    ui.menu() as help_menu,
                ):
                    with (
                        ui.menu_item(on_click=about_dialog.open).tooltip("Alt+I"),
                        ui.row().classes("items-center"),
                    ):
                        ui.icon("info").classes("text-lg")
                        ui.label(_("About"))
                    with ui.menu_item(), ui.row().classes("items-center"):
                        ui.icon("text_snippet").classes("text-lg")
                        ui.link(
                            _("Documentation"),
                            target="https://soulmelody.github.io/LibreSVIP",
                            new_tab=True,
                        )
            with (
                ui.dialog() as settings_dialog,
                ui.card().classes("min-w-[750px]"),
            ):
                with ui.splitter(value=25, limits=(25, 30)).classes("w-full") as settings_splitter:
                    with (
                        settings_splitter.before,
                        ui.tabs().props("vertical") as settings_nav,
                    ):
                        conversion_settings_tab = ui.tab(
                            _("Conversion Settings"),
                            icon="settings_applications",
                        )
                        lyric_replace_rules_tab = ui.tab(
                            _("Lyric Replace Rules"), icon="text_rotation_none"
                        )
                        language_tab = ui.tab(_("Switch Language"), icon="language")
                    with (
                        settings_splitter.after,
                        ui.tab_panels(settings_nav, value=conversion_settings_tab),
                    ):
                        with (
                            ui.tab_panel(conversion_settings_tab),
                            ui.column(),
                        ):
                            ui.switch(_("Auto detect import format")).bind_value(
                                settings,
                                "auto_detect_input_format",
                            )
                            ui.switch(
                                _("Reset list when import format changed"),
                            ).classes("col-span-5").bind_value(
                                settings,
                                "reset_tasks_on_input_change",
                            )
                        with ui.tab_panel(lyric_replace_rules_tab):
                            columns = [
                                {
                                    "name": "mode",
                                    "label": _("Mode"),
                                    "field": "mode",
                                },
                                {
                                    "name": "pattern_prefix",
                                    "label": _("Prefix"),
                                    "field": "pattern_prefix",
                                },
                                {
                                    "name": "pattern_main",
                                    "label": _("Pattern"),
                                    "field": "pattern_main",
                                },
                                {
                                    "name": "pattern_suffix",
                                    "label": _("Suffix"),
                                    "field": "pattern_suffix",
                                },
                                {
                                    "name": "replacement",
                                    "label": _("Replacement"),
                                    "field": "replacement",
                                },
                                {
                                    "name": "flags",
                                    "label": _("Flags"),
                                    "field": "flags",
                                },
                                {
                                    "name": "actions",
                                    "label": _("Actions"),
                                    "field": "actions",
                                },
                            ]

                            def refresh_rules(
                                preset: str,
                            ) -> list[dict[str, JsonValue]]:
                                return [
                                    {
                                        "id": i + 1,
                                        "mode": rule.mode.value,
                                        "pattern_prefix": rule.pattern_prefix,
                                        "pattern_main": rule.pattern_main,
                                        "pattern_suffix": rule.pattern_suffix,
                                        "replacement": rule.replacement,
                                        "flags": rule.flags.value,
                                    }
                                    for i, rule in enumerate(settings.lyric_replace_rules[preset])
                                ]

                            rows = refresh_rules(selected_formats.current_preset)
                            replace_mode_options = [
                                {"label": _("Full match"), "value": "full"},
                                {
                                    "label": _("Alphabetic"),
                                    "value": "alphabetic",
                                },
                                {
                                    "label": _("Non-alphabetic"),
                                    "value": "non_alphabetic",
                                },
                                {"label": _("Regex"), "value": "regex"},
                            ]
                            re_flags_options = [
                                {
                                    "label": _("Ignore case"),
                                    "value": re.IGNORECASE.value,
                                },
                                {
                                    "label": _("Case sensitive"),
                                    "value": re.UNICODE.value,
                                },
                            ]
                            table = ui.table(columns=columns, rows=rows, pagination=5).classes(
                                "w-full"
                            )
                            table.add_slot(
                                "body-cell-mode",
                                r'''
                                <q-td key="mode" :props="props">
                                    <q-select
                                        v-model="props.row.mode"
                                        readonly
                                        map-options
                                        :options="'''
                                + str(replace_mode_options)
                                + r""""
                                    />
                                </q-td>
                            """,
                            )
                            table.add_slot(
                                "body-cell-pattern_prefix",
                                r"""
                                <q-td key="pattern_prefix" :props="props">
                                    {{ props.row.pattern_prefix }}
                                    <q-popup-edit v-model="props.row.pattern_prefix" v-if="props.row.mode === 'regex'" v-slot="scope">
                                        <q-input
                                            v-model="scope.value" dense autofocus counter
                                            @update:model-value="() => {props.row.pattern_prefix = scope.value; $parent.$emit('modify_field', props.row.id, 'pattern_prefix', scope.value)}"
                                        />
                                    </q-popup-edit>
                                </q-td>
                            """,
                            )
                            table.add_slot(
                                "body-cell-pattern_main",
                                r"""
                                <q-td key="pattern_main" :props="props">
                                    {{ props.row.pattern_main }}
                                    <q-popup-edit v-model="props.row.pattern_main" v-slot="scope">
                                        <q-input
                                            v-model="scope.value" dense autofocus counter
                                            @update:model-value="() => {props.row.pattern_main = scope.value; $parent.$emit('modify_field', props.row.id, 'pattern_main', scope.value)}"
                                        />
                                    </q-popup-edit>
                                </q-td>
                            """,
                            )
                            table.add_slot(
                                "body-cell-pattern_suffix",
                                r"""
                                <q-td key="pattern_suffix" :props="props">
                                    {{ props.row.pattern_suffix }}
                                    <q-popup-edit v-model="props.row.pattern_suffix" v-if="props.row.mode === 'regex'" v-slot="scope">
                                        <q-input
                                            v-model="scope.value" dense autofocus counter
                                            @update:model-value="() => {props.row.pattern_suffix = scope.value; $parent.$emit('modify_field', props.row.id, 'pattern_suffix', scope.value)}"
                                        />
                                    </q-popup-edit>
                                </q-td>
                            """,
                            )
                            table.add_slot(
                                "body-cell-replacement",
                                r"""
                                <q-td key="replacement" :props="props">
                                    {{ props.row.replacement }}
                                    <q-popup-edit v-model="props.row.replacement" v-slot="scope">
                                        <q-input
                                            v-model="scope.value" dense autofocus counter
                                            @update:model-value="() => {props.row.replacement = scope.value; $parent.$emit('modify_field', props.row.id, 'replacement', scope.value)}"
                                        />
                                    </q-popup-edit>
                                </q-td>
                            """,
                            )
                            table.add_slot(
                                "body-cell-flags",
                                r'''
                                <q-td key="flags" :props="props">
                                    <q-select
                                        v-model="props.row.flags"
                                        map-options
                                        :options="'''
                                + str(re_flags_options)
                                + r""""
                                        @update:model-value="() => $parent.$emit('modify_field', props.row.id, 'flags', props.row.flags.value)"
                                    />
                                </q-td>
                            """,
                            )
                            table.add_slot(
                                "body-cell-actions",
                                r"""
                                <q-td key="actions" :props="props">
                                    <span>
                                        <q-btn size="sm" color="accent" round dense
                                            @click="() => $parent.$emit('move_up', props.row)"
                                            icon="arrow_upward" />
                                        <q-btn size="sm" color="accent" round dense
                                            @click="() => $parent.$emit('move_down', props.row)"
                                            icon="arrow_downward" />
                                        <q-btn size="sm" color="accent" round dense
                                            @click="() => $parent.$emit('delete', props.row)"
                                            icon="remove" />
                                    </span>
                                </q-td>
                            """,
                            )

                            def modify_field(
                                event: GenericEventArguments,
                            ) -> None:
                                if (
                                    row_idx := find_index(
                                        rows,
                                        lambda row: row["id"] == event.args["id"],
                                    )
                                ) != -1:
                                    rows[row_idx][event.args[1]] = event.args[2]

                            table.on("modify_field", modify_field)

                            def move_up_rule(
                                event: GenericEventArguments,
                            ) -> None:
                                if (
                                    row_idx := find_index(
                                        rows,
                                        lambda row: row["id"] == event.args["id"],
                                    )
                                ) > 0:
                                    rows[row_idx - 1], rows[row_idx] = (
                                        rows[row_idx],
                                        rows[row_idx - 1],
                                    )
                                    table.update_rows(rows)

                            table.on("move_up", move_up_rule)

                            def move_down_rule(
                                event: GenericEventArguments,
                            ) -> None:
                                if (
                                    -1
                                    < (
                                        row_idx := find_index(
                                            rows,
                                            lambda row: row["id"] == event.args["id"],
                                        )
                                    )
                                    < len(rows) - 1
                                ):
                                    rows[row_idx + 1], rows[row_idx] = (
                                        rows[row_idx],
                                        rows[row_idx + 1],
                                    )
                                    table.update_rows(rows)

                            table.on("move_down", move_down_rule)

                            def delete_rule(
                                event: GenericEventArguments,
                            ) -> None:
                                if (
                                    row_idx := find_index(
                                        rows,
                                        lambda row: row["id"] == event.args["id"],
                                    )
                                ) != -1:
                                    table.remove_rows(rows[row_idx])

                            table.on("delete", delete_rule)

                            with table.add_slot("top"):

                                def table_toggle_fullscreen() -> None:
                                    table.toggle_fullscreen()
                                    table_fullscreen_btn.props(
                                        "icon=fullscreen_exit"
                                        if table.is_fullscreen
                                        else "icon=fullscreen"
                                    )

                                table_fullscreen_btn = (
                                    ui.button(
                                        icon="fullscreen",
                                        on_click=table_toggle_fullscreen,
                                    )
                                    .props("round")
                                    .tooltip(_("Toggle fullscreen"))
                                )

                                def refresh_rows(
                                    event: ValueChangeEventArguments,
                                ) -> None:
                                    if event.value is not None:
                                        settings.lyric_replace_rules.setdefault(event.value, [])
                                        table.update_rows(refresh_rules(event.value))

                                preset_select = ui.select(
                                    list(settings.lyric_replace_rules),
                                    label=_("Preset: "),
                                    new_value_mode="add-unique",
                                    on_change=refresh_rows,
                                ).bind_value(selected_formats, "current_preset")

                                def delete_preset() -> None:
                                    if preset_select.value != "default":
                                        settings.lyric_replace_rules.pop(preset_select.value)
                                        preset_select.set_options(
                                            list(settings.lyric_replace_rules),
                                            value="default",
                                        )

                                ui.button(icon="remove", on_click=delete_preset).props(
                                    "round"
                                ).tooltip(_("Remove current preset"))

                                def save_preset() -> None:
                                    settings.lyric_replace_rules[preset_select.value] = [
                                        LyricsReplacement(  # type: ignore[call-arg]
                                            mode=LyricsReplaceMode(row["mode"]),
                                            replacement=row["replacement"],
                                            pattern_main=row["pattern_main"],
                                            pattern_prefix=row["pattern_prefix"],
                                            pattern_suffix=row["pattern_suffix"],
                                            flags=re.UNICODE
                                            if row["flags"] == re.UNICODE.value
                                            else re.IGNORECASE,
                                        )
                                        for row in rows
                                    ]
                                    middleware_options.refresh()

                                ui.button(icon="save", on_click=save_preset).props("round").tooltip(
                                    _("Save current preset")
                                )

                                def add_rule(mode_value: str) -> None:
                                    pattern_prefix = pattern_suffix = ""
                                    if mode_value == LyricsReplaceMode.FULL.value:
                                        pattern_prefix = "^"
                                        pattern_suffix = "$"
                                    elif mode_value == LyricsReplaceMode.ALPHABETIC.value:
                                        pattern_prefix = r"(?<=^|\b)"
                                        pattern_suffix = r"(?=$|\b)"
                                    table.add_rows(
                                        {
                                            "id": rows[-1]["id"] + 1 if len(rows) else 1,
                                            "mode": mode_value,
                                            "pattern_main": "",
                                            "pattern_prefix": pattern_prefix,
                                            "pattern_suffix": pattern_suffix,
                                            "replacement": "",
                                            "flags": re.IGNORECASE.value,
                                        }
                                    )

                                with ui.dropdown_button(_("Add new rule"), icon="add").tooltip(
                                    _(
                                        "Alphabetic: Applies to alphabetic characters.\nNon-Alphabetic: For non-alphabetic characters and punctuation marks.\nRegex: for advanced users with knowledge of regular expressions."
                                    )
                                ):
                                    for option in replace_mode_options:
                                        ui.item(
                                            option["label"],
                                            on_click=functools.partial(add_rule, option["value"]),
                                        )
                        with ui.tab_panel(language_tab):

                            def switch_language(
                                event: ValueChangeEventArguments,
                            ) -> None:
                                if event.value == Language.CHINESE:
                                    ui.navigate.to("/?lang=zh_CN")
                                elif event.value == Language.ENGLISH:
                                    ui.navigate.to("/?lang=en_US")

                            ui.select(
                                {
                                    Language.CHINESE: "简体中文",
                                    Language.ENGLISH: "English",
                                    Language.JAPANESE: "日本語",
                                },
                            ).bind_value(
                                settings,
                                "language",
                            ).on_value_change(switch_language)
                with ui.card_actions().props("align=right").classes("w-full"):
                    ui.button(_("Close"), on_click=settings_dialog.close)
            ui.button(
                icon="settings",
                on_click=settings_dialog.open,
            ).classes("aspect-square").tooltip(_("Settings (&S)"))
            ui.space()
            with ui.tabs().classes("sm:visible lg:h-0 lg:invisible") as tabs:
                format_select_tab = ui.tab(_("Select File Formats"))
                options_tab = ui.tab(_("Advanced Settings"))
            ui.space()
            if app.native.main_window is not None:
                if platform.system() == "Windows":
                    import ctypes.wintypes

                    import clr

                    clr.AddReference("System")
                    clr.AddReference("System.Windows.Forms")

                    from System import IntPtr
                    from System.Windows.Forms import Screen

                    user32 = ctypes.windll.user32  # type: ignore[attr-defined]
                    rect_tuple = (0, 0, 1200, 800)
                    _maximized = False

                    def _maximize() -> None:
                        nonlocal _maximized, rect_tuple
                        if not _maximized:
                            hwnd = user32.GetForegroundWindow()
                            screen = Screen.FromHandle(IntPtr(hwnd))
                            rect = ctypes.wintypes.RECT()
                            user32.GetWindowRect(hwnd, ctypes.pointer(rect))
                            rect_tuple = (
                                rect.left,
                                rect.top,
                                rect.right - rect.left,
                                rect.bottom - rect.top,
                            )
                            user32.MoveWindow(
                                hwnd,
                                screen.Bounds.X,
                                screen.Bounds.Y,
                                screen.WorkingArea.Width,
                                screen.WorkingArea.Height,
                                True,
                            )
                            _maximized = True

                    app.native.main_window.maximize = _maximize

                    def _restore() -> None:
                        nonlocal _maximized
                        if _maximized:
                            _maximized = False
                        hwnd = user32.GetForegroundWindow()
                        user32.MoveWindow(hwnd, *rect_tuple, True)

                    app.native.main_window.restore = _restore
                maximized = False
                maximize_text = _("Maximize")
                restore_text = _("Restore")

                def toggle_maxmized() -> None:
                    nonlocal maximized
                    if maximized:
                        app.native.main_window.restore()
                        maximize_button.props("icon=open_in_full")
                        maximize_button_tooltip.set_text(maximize_text)
                    else:
                        app.native.main_window.maximize()
                        maximize_button.props("icon=close_fullscreen")
                        maximize_button_tooltip.set_text(restore_text)
                    maximized = not maximized

                ui.button(icon="minimize", on_click=app.native.main_window.minimize).classes(
                    "aspect-square"
                ).tooltip(_("Minimize"))
                with ui.button(
                    icon="open_in_full",
                    on_click=toggle_maxmized,
                ).classes("aspect-square") as maximize_button:
                    maximize_button_tooltip = ui.tooltip(maximize_text)
                ui.button(
                    icon="close",
                    color="negative",
                    on_click=app.native.main_window.destroy,
                ).classes("aspect-square").tooltip(_("Close"))

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
                    elif e.key == "a":
                        dark_toggler.auto()
                    elif e.key == "s":
                        settings_dialog.open()
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
                            k: _(v["file_format"] or "") + " " + (v["suffix"] or "")
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
                ui.button(
                    icon="info",
                    on_click=input_info.open,
                ).classes(
                    "min-w-[45px] max-w-[45px] aspect-square",
                ).tooltip(_("View Detail Information"))
                ui.switch(_("Auto detect import format")).classes(
                    "col-span-5",
                ).bind_value(
                    settings,
                    "auto_detect_input_format",
                )
                ui.switch(
                    _("Reset list when import format changed"),
                ).classes("col-span-5").bind_value(
                    settings,
                    "reset_tasks_on_input_change",
                )
                ui.button(
                    icon="swap_vert",
                    on_click=swap_values,
                ).classes("min-w-[45px] max-w-[45px] w-fit aspect-square").props("round").tooltip(
                    _("Swap Input and Output")
                )
                select_output = (
                    ui.select(
                        {
                            k: _(v["file_format"] or "") + " " + (v["suffix"] or "")
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
                ui.button(
                    icon="info",
                    on_click=output_info.open,
                ).classes(
                    "min-w-[45px] max-w-[45px] aspect-square",
                ).tooltip(_("View Detail Information"))

    def tasks_area() -> None:
        with ui.card().classes("w-full h-full").tight() as tasks_card:
            with ui.row().classes("w-full"):
                ui.label(_("Import project")).classes("text-h5 font-bold")
                ui.space()
                ui.label(_("Conversion Mode:")).classes("text-h5")
                ui.toggle(
                    {mode.value: mode.name for mode in ConversionMode},
                ).bind_value(
                    selected_formats,
                    "conversion_mode",
                )
            selected_formats.tasks_container()
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
            with ui.row().classes(
                "absolute bottom-0 right-2 m-2 z-10",
            ):
                ui.label(_("Max Track count:")).bind_visibility_from(
                    selected_formats,
                    "conversion_mode",
                    backward=ConversionMode.SPLIT.value.__eq__,
                )
                ui.knob(
                    min=1,
                    max=10,
                    step=1,
                    show_value=True,
                    track_color="light-blue",
                ).bind_value(settings, "max_track_count").bind_visibility_from(
                    selected_formats,
                    "conversion_mode",
                    backward=ConversionMode.SPLIT.value.__eq__,
                )
                with ui.button(
                    icon="add",
                    on_click=selected_formats.add_upload,
                ).props("round"):
                    ui.badge().props(
                        "floating color=orange",
                    ).bind_text_from(
                        selected_formats,
                        "task_count",
                        backward=str,
                    ).tooltip(_("Continue Adding files"))
        with (
            ui.card()
            .classes(
                "w-full h-full opacity-60 hover:opacity-100 flex items-center justify-center border-dashed border-2 border-indigo-300 hover:border-indigo-500",
            )
            .style("cursor: pointer")
            .tight() as upload_card
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

    @ui.refreshable
    def middleware_options() -> None:
        for middleware in middleware_manager.plugin_registry.values():
            with ui.row().classes("items-center w-full"):
                middleware_toggler = (
                    ui.switch(_(middleware.name))
                    .props("color=green")
                    .bind_value(
                        selected_formats.middleware_enabled_states,
                        middleware.identifier,
                    )
                )
                if middleware.description:
                    ui.space()
                    ui.icon("help_outline").classes("text-3xl").style(
                        "cursor: help",
                    ).tooltip(_(middleware.description))
            middleware_options_form(middleware.identifier, middleware_toggler)

    def options_area() -> None:
        with ui.scroll_area().classes("w-full h-full"):
            with ui.row().classes("absolute top-0 right-2 m-2 z-10"):
                ui.button(
                    icon="play_arrow",
                    on_click=selected_formats.batch_convert,
                ).props("round").bind_visibility_from(
                    selected_formats,
                    "task_count",
                    backward=bool,
                ).tooltip(_("Start Conversion"))
                ui.button(
                    icon="download_for_offline",
                    on_click=selected_formats.save_file,
                ).props("round").bind_visibility_from(
                    selected_formats,
                    "task_count",
                    backward=bool,
                ).tooltip(_("Export"))
            ui.label(_("Advanced Options")).classes("text-h5 font-bold")
            with ui.expansion().classes("w-full") as import_panel:
                with import_panel.add_slot("header"):
                    input_panel_header()
                input_options()
            ui.separator()
            with ui.expansion().classes("w-full") as middleware_panel:
                with (
                    middleware_panel.add_slot("header"),
                    ui.row().classes("w-full items-center"),
                ):
                    ui.icon("auto_fix_high").classes("text-lg")
                    ui.label(_("Intermediate Processing")).classes("text-subtitle1 font-bold")
                middleware_options()
            ui.separator()
            with ui.expansion().classes("w-full") as export_panel:
                with export_panel.add_slot("header"):
                    output_panel_header()
                output_options()

    with ui.card().classes("w-full min-w-80").style("height: calc(100vh - 155px)").tight():
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
            ui.card().classes("w-full h-full sm:visible lg:h-0 lg:invisible").tight(),
            ui.tab_panels(tabs, value=format_select_tab).classes("h-full w-full"),
        ):
            with (
                ui.tab_panel(format_select_tab),
                ui.splitter(limits=(60, 60), horizontal=True, value=60).classes(
                    "h-full w-full"
                ) as format_select_splitter,
            ):
                with (
                    format_select_splitter.before,
                    ui.card().classes("h-full w-full").tight(),
                ):
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
    arg_parser.add_argument("--server", action="store_true")
    arg_parser.add_argument("--daemon", action="store_true")
    args, argv = arg_parser.parse_known_args()

    if shutil.which("termux-open-url") is not None:
        # a workaround for termux platform, from https://github.com/python/cpython/issues/90371#issuecomment-1460738762
        webbrowser.register("termux-open-url '%s'", None)

    secrets_path = app_dir.user_config_path / "secrets.txt"
    if not secrets_path.exists():
        secrets_path.parent.mkdir(parents=True, exist_ok=True)
        secrets_path.write_text(secrets.token_urlsafe(32))
    storage_secret = secrets_path.read_text()

    with as_file(res_dir / "libresvip.ico") as icon_path:
        ui.run(
            show=not args.daemon,
            window_size=None if args.server else (1200, 800),
            frameless=not args.server,
            reload=False,
            host=args.host if args.server else None,
            port=args.port,
            storage_secret=storage_secret,
            title="LibreSVIP",
            favicon=icon_path,
        )
