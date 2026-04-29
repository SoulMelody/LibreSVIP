import asyncio
import ctypes
import enum
import io
import json
import pathlib
import re
import traceback
from functools import partial
from importlib.resources import as_file
from typing import get_args, get_type_hints
from zipfile import ZipFile

import flet as ft
import flet_permission_handler as fph
import more_itertools
from pydantic import BaseModel
from pydantic_core import PydanticUndefined
from pydantic_extra_types.color import Color
from upath import UPath

import libresvip
from libresvip.core.config import (
    LYRIC_REPLACE_MODE_PREFIX_SUFFIX,
    LyricsReplacement,
    LyricsReplaceMode,
    settings,
)
from libresvip.core.constants import res_dir
from libresvip.core.warning_types import CatchWarnings
from libresvip.extension.base import ReadOnlyConverterMixin, WriteOnlyConverterMixin
from libresvip.extension.manager import get_translation, middleware_manager, plugin_manager
from libresvip.model.base import BaseComplexModel, Project
from libresvip.utils import translation
from libresvip.utils.translation import gettext_lazy as _


class LOGFONT(ctypes.Structure):
    _fields_ = (
        ("lfHeight", ctypes.c_long),
        ("lfWidth", ctypes.c_long),
        ("lfEscapement", ctypes.c_long),
        ("lfOrientation", ctypes.c_long),
        ("lfWeight", ctypes.c_long),
        ("lfItalic", ctypes.c_byte),
        ("lfUnderline", ctypes.c_byte),
        ("lfStrikeOut", ctypes.c_byte),
        ("lfCharSet", ctypes.c_byte),
        ("lfOutPrecision", ctypes.c_byte),
        ("lfClipPrecision", ctypes.c_byte),
        ("lfQuality", ctypes.c_byte),
        ("lfPitchAndFamily", ctypes.c_byte),
        ("lfFaceName", ctypes.c_wchar * 32),
    )


class NONCLIENTMETRICS(ctypes.Structure):
    _fields_ = (
        ("cbSize", ctypes.c_ulong),
        ("iBorderWidth", ctypes.c_long),
        ("iScrollWidth", ctypes.c_long),
        ("iScrollHeight", ctypes.c_long),
        ("iCaptionWidth", ctypes.c_long),
        ("iCaptionHeight", ctypes.c_long),
        ("lfCaptionFont", LOGFONT),
        ("iSmCaptionWidth", ctypes.c_long),
        ("iSmCaptionHeight", ctypes.c_long),
        ("lfSmCaptionFont", LOGFONT),
        ("iMenuWidth", ctypes.c_long),
        ("iMenuHeight", ctypes.c_long),
        ("lfMenuFont", LOGFONT),
        ("lfStatusFont", LOGFONT),
        ("lfMessageFont", LOGFONT),
        ("iPaddedBorderWidth", ctypes.c_long),
    )


SPI_GETNONCLIENTMETRICS = 0x29


def ensure_bool(value: bool | str) -> bool:
    if isinstance(value, bool):
        return value
    return json.loads(value)


def get_default_font_win32() -> str:
    metrics = NONCLIENTMETRICS()
    metrics.cbSize = ctypes.sizeof(NONCLIENTMETRICS)
    ctypes.windll.user32.SystemParametersInfoW(
        SPI_GETNONCLIENTMETRICS, metrics.cbSize, ctypes.byref(metrics), 0
    )
    return metrics.lfMessageFont.lfFaceName


def get_default_font_unix() -> str | None:
    import fontconfig

    for font in fontconfig.query(where="", select=("family",)):
        return font["family"]


async def main(page: ft.Page) -> None:
    loop = asyncio.get_running_loop()
    shared_preferences = ft.SharedPreferences()
    storage_paths = ft.StoragePaths()
    page.title = "LibreSVIP"
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.window.min_width = 480
    page.window.min_height = 720
    page.window.title_bar_hidden = True
    page.window.title_bar_buttons_hidden = True
    page.splash = ft.Container(content=ft.ProgressRing(), alignment=ft.Alignment.CENTER)

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

    with as_file(res_dir / "libresvip.ico") as icon:
        page.window.icon = str(icon)

    if page.platform == ft.PagePlatform.WINDOWS:
        page.theme = ft.Theme(font_family=get_default_font_win32())
    elif page.platform in [ft.PagePlatform.LINUX, ft.PagePlatform.MACOS] and (
        default_font_family := get_default_font_unix()
    ):
        page.theme = ft.Theme(font_family=default_font_family)
    if not await shared_preferences.contains_key("dark_mode"):
        await shared_preferences.set("dark_mode", "System")
    page.theme_mode = ft.ThemeMode(
        ((await shared_preferences.get("dark_mode") or "System").lower()).strip('"')
    )

    async def change_theme(dark_mode: str) -> None:
        page.theme_mode = ft.ThemeMode(dark_mode.lower())
        await shared_preferences.set("dark_mode", dark_mode)
        page.update()

    if not await shared_preferences.contains_key("language"):
        await shared_preferences.set("language", "en_US")
    translation.singleton_translation = get_translation(await shared_preferences.get("language"))

    async def change_language(lang: str) -> None:
        await shared_preferences.set("language", lang)
        translation.singleton_translation = get_translation(lang)
        await page.push_route(f"/?lang={lang}")

    if not await shared_preferences.contains_key("save_folder"):
        await shared_preferences.set(
            "save_folder",
            "." if page.web else (await storage_paths.get_downloads_directory()) or ".",
        )
    save_folder_text_field = ft.Ref[ft.TextField]()
    temp_path = UPath("memory:/")

    task_list_view = ft.Ref[ft.ReorderableListView]()
    input_select = ft.Ref[ft.Dropdown]()
    output_select = ft.Ref[ft.Dropdown]()
    conversion_mode_select = ft.Ref[ft.Dropdown]()
    input_options = ft.Ref[ft.ResponsiveRow]()
    output_options = ft.Ref[ft.ResponsiveRow]()
    middleware_options = {
        middleware_id: ft.Ref[ft.ExpansionPanel]()
        for middleware_id in middleware_manager.plugins.get("middleware", {})
    }
    lyric_rules_list_view = ft.Ref[ft.ListView]()
    lyric_group_select = ft.Ref[ft.Dropdown]()

    def build_options(option_class: type[BaseModel]) -> list[ft.Control]:
        fields = []
        for option_key, field_info in option_class.model_fields.items():
            default_value = None if field_info.default is PydanticUndefined else field_info.default
            if field_info.annotation is None:
                continue
            elif issubclass(field_info.annotation, enum.Enum):
                default_value = default_value.value if default_value is not None else None
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
                            ft.DropdownOption(
                                enum_item.value,
                                _(enum_field.title),
                                content=ft.Text(
                                    _(enum_field.title),
                                    tooltip=ft.Tooltip(
                                        _(enum_field.description or ""),
                                        trigger_mode=ft.TooltipTriggerMode.TAP,
                                    ),
                                ),
                            )
                        )
                fields.append(
                    ft.Dropdown(
                        options=choices,
                        label=_(field_info.title or ""),
                        value=default_value,
                        data=option_key,
                        col=10 if field_info.description is not None else 12,
                    )
                )
            elif issubclass(field_info.annotation, bool):
                fields.append(
                    ft.Switch(
                        label=_(field_info.title or ""),
                        value=default_value,
                        data=option_key,
                        col=10 if field_info.description is not None else 12,
                    )
                )
            elif issubclass(field_info.annotation, int):
                fields.append(
                    ft.TextField(
                        label=_(field_info.title or ""),
                        value=default_value,
                        data=option_key,
                        input_filter=ft.NumbersOnlyInputFilter(),
                        col=10 if field_info.description is not None else 12,
                    )
                )
            elif issubclass(field_info.annotation, float):
                fields.append(
                    ft.TextField(
                        label=_(field_info.title or ""),
                        value=default_value,
                        data=option_key,
                        input_filter=ft.InputFilter(regex_string=r"^-?\d+(\.\d*)?$"),
                        col=10 if field_info.description is not None else 12,
                    )
                )
            elif issubclass(field_info.annotation, str | BaseComplexModel | Color):
                if issubclass(field_info.annotation, BaseComplexModel):
                    default_value = field_info.annotation.default_repr()
                fields.append(
                    ft.TextField(
                        label=_(field_info.title or ""),
                        value=default_value,
                        data=option_key,
                        col=10 if field_info.description is not None else 12,
                    )
                )
            else:
                continue
            if field_info.description:
                fields.append(
                    ft.IconButton(
                        ft.Icons.HELP_OUTLINE_OUTLINED,
                        mouse_cursor=ft.MouseCursor.HELP,
                        tooltip=ft.Tooltip(_(field_info.description)),
                        col=2,
                    )
                )
        return fields

    def build_input_options(value: str | None) -> list[ft.Control]:
        if value in plugin_manager.plugins.get("svs", {}):
            input_plugin = plugin_manager.plugins.get("svs", {})[value]
            return build_options(input_plugin.input_option_cls)
        return []

    def build_middleware_options(value: str) -> list[ft.Control]:
        if value in middleware_manager.plugins.get("middleware", {}):
            middleware = middleware_manager.plugins.get("middleware", {})[value]
            return build_options(middleware.process_option_cls)
        return []

    def build_output_options(value: str | None) -> list[ft.Control]:
        if value in plugin_manager.plugins.get("svs", {}):
            output_plugin = plugin_manager.plugins.get("svs", {})[value]
            return build_options(output_plugin.output_option_cls)
        return []

    async def set_last_input_format(value: str | ft.Event[ft.BaseControl] | None) -> None:
        if control := getattr(value, "control", None):
            value = control.value
        if input_select.current.value != value:
            input_select.current.value = value
        last_input_format = await shared_preferences.get("last_input_format")
        if last_input_format != value:
            input_options.current.controls = build_input_options(value)
            reset_tasks_on_input_change = ensure_bool(
                await shared_preferences.get("reset_tasks_on_input_change")
            )
            if reset_tasks_on_input_change:
                task_list_view.current.controls.clear()
            await shared_preferences.set("last_input_format", value)

    async def set_last_output_format(value: str | ft.Event[ft.BaseControl] | None) -> None:
        if control := getattr(value, "control", None):
            value = control.value
        if output_select.current.value != value:
            output_select.current.value = value
        last_output_format = await shared_preferences.get("last_output_format")
        if last_output_format != value:
            output_options.current.controls = build_output_options(value)
            await shared_preferences.set("last_output_format", value)

    def show_task_log(e: ft.ControlEvent) -> None:
        list_tile = e.control.parent.parent
        if list_tile.data.get("log_text"):

            async def copy_log_text(e: ft.ControlEvent) -> None:
                await clipboard.set(list_tile.data["log_text"])
                banner: ft.Banner = ft.Banner(
                    ft.Text(_("Copied")),
                    leading=ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE),
                    actions=[ft.TextButton(_("OK"), on_click=page.pop_dialog)],
                )
                page.show_dialog(banner)

            page.views.append(
                ft.View(
                    route="/task_log",
                    appbar=ft.AppBar(
                        title=ft.Text(_("Task log")),
                        bgcolor=ft.Colors.SURFACE,
                        leading=ft.IconButton(
                            ft.Icons.ARROW_BACK_OUTLINED,
                            tooltip=_("Back"),
                            on_click=lambda _: view_pop(None),
                        ),
                    ),
                    controls=[
                        ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Button(
                                            _("Copy to clipboard"),
                                            on_click=copy_log_text,
                                        )
                                    ],
                                    alignment=ft.MainAxisAlignment.END,
                                ),
                                ft.TextField(
                                    value=list_tile.data["log_text"],
                                    multiline=True,
                                    expand=True,
                                    max_lines=24,
                                    autofocus=True,
                                ),
                            ],
                        )
                    ],
                )
            )
            page.update()

    async def select_files() -> None:
        if files := await file_picker.pick_files(
            _("Select files to convert"), allow_multiple=True, with_data=True
        ):
            auto_detect_input_format = await shared_preferences.get("auto_detect_input_format")
            if page.web:
                for file in files:
                    await on_upload_progress(file)
                return
            for file in files:
                last_input_format = await shared_preferences.get("last_input_format")
                file_path = pathlib.Path(file.path)
                suffix = file_path.suffix.lower().removeprefix(".")
                if (
                    suffix != last_input_format
                    and auto_detect_input_format
                    and suffix in plugin_manager.plugins.get("svs", {})
                ):
                    await set_last_input_format(suffix)
                task_list_view.current.controls.append(
                    ft.ListTile(
                        leading=ft.Stack(
                            [
                                ft.Icon(
                                    ft.Icons.ACCESS_TIME_FILLED_OUTLINED,
                                    color=ft.Colors.GREY_400,
                                ),
                                ft.ProgressRing(visible=False),
                            ]
                        ),
                        title=ft.Text(file.name),
                        subtitle=ft.Text(file_path.stem),
                        trailing=ft.PopupMenuButton(
                            menu_position=ft.PopupMenuPosition.UNDER,
                            items=[
                                ft.PopupMenuItem(
                                    icon=ft.Icons.REMOVE_RED_EYE_OUTLINED,
                                    content=_("View Log"),
                                    on_click=show_task_log,
                                ),
                                ft.PopupMenuItem(
                                    icon=ft.Icons.EDIT,
                                    content=_("Rename"),
                                    on_click=open_rename_dialog,
                                ),
                                ft.PopupMenuItem(
                                    icon=ft.Icons.DELETE_OUTLINE,
                                    content=_("Remove"),
                                    on_click=remove_task,
                                ),
                            ],
                            tooltip=_("Actions"),
                        ),
                        data={"path": file_path, "log_text": ""},
                        content_padding=ft.Padding(0, 0, 30, 0),
                    )
                )
            page.update()

    async def select_save_folder() -> None:
        if path := await file_picker.get_directory_path(
            _("Change Output Directory"),
            ## (await shared_preferences.get("save_folder")).strip('"'),
        ):
            await shared_preferences.set("save_folder", path)
            if save_folder_text_field.current is not None:
                save_folder_text_field.current.value = path

    if not await shared_preferences.contains_key("auto_detect_input_format"):
        await shared_preferences.set("auto_detect_input_format", True)

    async def change_auto_detect_input_format(e: ft.ControlEvent) -> None:
        await shared_preferences.set("auto_detect_input_format", e.control.value)

    if not await shared_preferences.contains_key("reset_tasks_on_input_change"):
        await shared_preferences.set("reset_tasks_on_input_change", True)

    async def change_reset_tasks_on_input_change(e: ft.ControlEvent) -> None:
        await shared_preferences.set("reset_tasks_on_input_change", e.control.value)

    if not await shared_preferences.contains_key("max_track_count"):
        await shared_preferences.set("max_track_count", 1)

    async def change_max_track_count(e: ft.ControlEvent) -> None:
        await shared_preferences.set("max_track_count", int(e.control.value))

    current_lyric_group = "default"
    lyric_replace_rules: dict[str, list[dict]] = {}

    async def load_lyric_rules_from_prefs() -> None:
        nonlocal lyric_replace_rules
        raw = await shared_preferences.get("lyric_replace_rules")
        lyric_replace_rules = json.loads(raw) if raw else {"default": []}

    async def save_lyric_rules_to_prefs() -> None:
        await shared_preferences.set("lyric_replace_rules", json.dumps(lyric_replace_rules))

    def get_lyric_rules_for_group(group_name: str) -> list[LyricsReplacement]:
        return [
            LyricsReplacement(
                mode=LyricsReplaceMode(r.get("mode", "full")),
                pattern_main=r.get("pattern_main", ""),
                pattern_prefix=r.get("pattern_prefix", ""),
                pattern_suffix=r.get("pattern_suffix", ""),
                replacement=r.get("replacement", ""),
                flags=re.RegexFlag(r.get("flags", re.IGNORECASE.value)),
            )
            for r in lyric_replace_rules.get(group_name, [])
        ]

    def build_lyric_rule_tile(index: int, rule: LyricsReplacement) -> ft.Card:
        def remove_rule(e: ft.ControlEvent) -> None:
            rules = lyric_replace_rules.get(current_lyric_group, [])
            if 0 <= index < len(rules):
                del rules[index]
            refresh_lyric_rules_table(current_lyric_group)

        return ft.Card(
            ft.Container(
                ft.Column(
                    [
                        ft.ResponsiveRow(
                            [
                                ft.Dropdown(
                                    label=_("Mode"),
                                    options=[
                                        ft.DropdownOption(
                                            LyricsReplaceMode.FULL.value, _("Full match")
                                        ),
                                        ft.DropdownOption(
                                            LyricsReplaceMode.ALPHABETIC.value, _("Alphabetic")
                                        ),
                                        ft.DropdownOption(
                                            LyricsReplaceMode.NON_ALPHABETIC.value,
                                            _("Non-alphabetic"),
                                        ),
                                        ft.DropdownOption(
                                            LyricsReplaceMode.REGEX.value, _("Regex")
                                        ),
                                    ],
                                    value=rule.mode.value,
                                    col=6,
                                    dense=True,
                                    data=("mode", index),
                                    on_select=lambda e: update_lyric_rule_field(
                                        e.control.data[1], "mode", e.control.value
                                    ),
                                ),
                                ft.Dropdown(
                                    label=_("Flags"),
                                    options=[
                                        ft.DropdownOption(
                                            str(re.IGNORECASE.value), _("Ignore case")
                                        ),
                                        ft.DropdownOption(
                                            str(re.UNICODE.value), _("Case sensitive")
                                        ),
                                    ],
                                    value=str(rule.flags.value),
                                    col=6,
                                    dense=True,
                                    data=("flags", index),
                                    on_select=lambda e: update_lyric_rule_field(
                                        e.control.data[1], "flags", e.control.value
                                    ),
                                ),
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.TextField(
                            label=_("Pattern"),
                            value=rule.pattern_main,
                            dense=True,
                            data=("pattern_main", index),
                            on_change=lambda e: update_lyric_rule_field(
                                e.control.data[1], "pattern_main", e.control.value
                            ),
                        ),
                        ft.TextField(
                            label=_("Prefix"),
                            value=rule.pattern_prefix,
                            dense=True,
                            data=("pattern_prefix", index),
                            disabled=rule.mode != LyricsReplaceMode.REGEX,
                            on_change=lambda e: update_lyric_rule_field(
                                e.control.data[1], "pattern_prefix", e.control.value
                            ),
                        ),
                        ft.TextField(
                            label=_("Suffix"),
                            value=rule.pattern_suffix,
                            dense=True,
                            data=("pattern_suffix", index),
                            disabled=rule.mode != LyricsReplaceMode.REGEX,
                            on_change=lambda e: update_lyric_rule_field(
                                e.control.data[1], "pattern_suffix", e.control.value
                            ),
                        ),
                        ft.TextField(
                            label=_("Replacement"),
                            value=rule.replacement,
                            dense=True,
                            data=("replacement", index),
                            on_change=lambda e: update_lyric_rule_field(
                                e.control.data[1], "replacement", e.control.value
                            ),
                        ),
                        ft.Row(
                            [
                                ft.IconButton(
                                    ft.Icons.DELETE_OUTLINED,
                                    tooltip=_("Delete"),
                                    on_click=remove_rule,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.END,
                        ),
                    ],
                ),
                padding=10,
            ),
        )

    def update_lyric_rule_field(index: int, field: str, value: str) -> None:
        rules = lyric_replace_rules.get(current_lyric_group, [])
        if 0 <= index < len(rules):
            if field == "mode":
                rules[index]["mode"] = value
                if value in LYRIC_REPLACE_MODE_PREFIX_SUFFIX:
                    prefix, suffix = LYRIC_REPLACE_MODE_PREFIX_SUFFIX[value]
                    rules[index]["pattern_prefix"] = prefix
                    rules[index]["pattern_suffix"] = suffix
                refresh_lyric_rules_table(current_lyric_group)
            elif field == "flags":
                rules[index]["flags"] = int(value)
            else:
                rules[index][field] = value

    def refresh_lyric_rules_table(group_name: str) -> None:
        nonlocal current_lyric_group
        current_lyric_group = group_name
        rules = get_lyric_rules_for_group(group_name)
        lyric_rules_list_view.current.controls = [
            build_lyric_rule_tile(i, rule) for i, rule in enumerate(rules)
        ]
        page.update()

    def add_lyric_group(e: ft.ControlEvent) -> None:
        def confirm_add(e: ft.ControlEvent) -> None:
            group_name = add_dialog.content.value.strip()
            if group_name and group_name not in lyric_replace_rules:
                lyric_replace_rules[group_name] = []
                if lyric_group_select.current is not None:
                    lyric_group_select.current.options.append(
                        ft.DropdownOption(group_name, group_name)
                    )
                    lyric_group_select.current.value = group_name
                refresh_lyric_rules_table(group_name)
            page.pop_dialog()

        add_dialog = ft.AlertDialog(
            title=ft.Text(_("Add")),
            content=ft.TextField(label=_("Preset")),
            actions=[
                ft.TextButton(_("OK"), on_click=confirm_add),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(add_dialog)

    def delete_lyric_group(e: ft.ControlEvent) -> None:
        nonlocal current_lyric_group
        if current_lyric_group == "default":
            return
        del lyric_replace_rules[current_lyric_group]
        if lyric_group_select.current is not None:
            lyric_group_select.current.options = [
                ft.DropdownOption(g, g) for g in lyric_replace_rules
            ]
            lyric_group_select.current.value = "default"
        current_lyric_group = "default"
        refresh_lyric_rules_table("default")

    def add_lyric_rule(e: ft.ControlEvent) -> None:
        mode = LyricsReplaceMode.FULL.value
        prefix, suffix = LYRIC_REPLACE_MODE_PREFIX_SUFFIX.get(mode, ("", ""))
        lyric_replace_rules.setdefault(current_lyric_group, []).append(
            {
                "mode": mode,
                "pattern_main": "",
                "pattern_prefix": prefix,
                "pattern_suffix": suffix,
                "replacement": "",
                "flags": re.IGNORECASE.value,
            }
        )
        refresh_lyric_rules_table(current_lyric_group)

    async def save_lyric_rules(e: ft.ControlEvent) -> None:
        await save_lyric_rules_to_prefs()
        banner = ft.Banner(
            ft.Text(_("Saved")),
            leading=ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE),
            actions=[ft.TextButton(_("OK"), on_click=page.pop_dialog)],
        )
        page.show_dialog(banner)

    async def on_upload_progress(f: ft.FilePickerFile) -> None:
        auto_detect_input_format = ensure_bool(
            await shared_preferences.get("auto_detect_input_format")
        )
        last_input_format = await shared_preferences.get("last_input_format")
        file_path = temp_path / f.name
        file_path.write_bytes(f.bytes)
        suffix = file_path.suffix.lower().removeprefix(".")
        if (
            suffix != last_input_format
            and auto_detect_input_format
            and suffix in plugin_manager.plugins.get("svs", {})
        ):
            await set_last_input_format(suffix)
        task_list_view.current.controls.append(
            ft.ListTile(
                leading=ft.Stack(
                    [
                        ft.Icon(
                            ft.Icons.ACCESS_TIME_FILLED_OUTLINED,
                            color=ft.Colors.GREY_400,
                        ),
                        ft.ProgressRing(visible=False),
                    ]
                ),
                title=ft.Text(f.name),
                subtitle=ft.Text(file_path.stem),
                trailing=ft.PopupMenuButton(
                    menu_position=ft.PopupMenuPosition.UNDER,
                    items=[
                        ft.PopupMenuItem(
                            icon=ft.Icons.REMOVE_RED_EYE_OUTLINED,
                            content=_("View Log"),
                            on_click=show_task_log,
                        ),
                        ft.PopupMenuItem(
                            icon=ft.Icons.EDIT,
                            content=_("Rename"),
                            on_click=open_rename_dialog,
                        ),
                        ft.PopupMenuItem(
                            icon=ft.Icons.DELETE_OUTLINE,
                            content=_("Remove"),
                            on_click=remove_task,
                        ),
                    ],
                    tooltip=_("Actions"),
                ),
                data={"path": file_path, "log_text": ""},
            )
        )

    clipboard = ft.Clipboard()
    file_picker = ft.FilePicker()
    url_launcher = ft.UrlLauncher()
    page.services.extend(
        [
            clipboard,
            file_picker,
            shared_preferences,
            storage_paths,
            url_launcher,
        ]
    )
    if (
        page.platform
        not in [
            ft.PagePlatform.ANDROID,
            ft.PagePlatform.IOS,
            ft.PagePlatform.WINDOWS,
        ]
        or page.web
    ):
        permission_handler = None
    else:
        permission_handler = fph.PermissionHandler()
        page.services.append(permission_handler)

    async def check_permission(e: ft.ControlEvent) -> None:
        if permission_handler is None:
            return
        result: fph.PermissionStatus | None = await permission_handler.get_status(e.control.data)
        banner_ref = ft.Ref[ft.Banner]()
        dismiss_btn = ft.TextButton(_("OK"), on_click=page.pop_dialog)
        if result != fph.PermissionStatus.GRANTED:
            result = await permission_handler.request(e.control.data)
            if result == fph.PermissionStatus.GRANTED:
                banner = ft.Banner(
                    ft.Text(_("Permission granted, you can now select files from your device.")),
                    ref=banner_ref,
                    leading=ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINED),
                    actions=[dismiss_btn],
                )
            else:
                banner = ft.Banner(
                    ft.Text(
                        _(
                            "Permission denied, please grant the permission to manage external storage."
                        )
                    ),
                    ref=banner_ref,
                    leading=ft.Icon(ft.Icons.WARNING_OUTLINED),
                    actions=[dismiss_btn],
                )
        else:
            banner = ft.Banner(
                ft.Text(
                    _("Permission already granted, you can now select files from your device.")
                ),
                ref=banner_ref,
                leading=ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINED),
                actions=[dismiss_btn],
            )
        page.show_dialog(banner)

    def open_rename_dialog(e: ft.ControlEvent) -> None:
        list_tile = e.control.parent.parent

        def close_rename_dialog() -> None:
            list_tile.subtitle.value = rename_dialog.content.value
            page.pop_dialog()

        rename_dialog: ft.AlertDialog = ft.AlertDialog(
            title=ft.Text(_("Rename")),
            content=ft.TextField(list_tile.subtitle.value),
            actions=[
                ft.TextButton(_("OK"), on_click=lambda _: close_rename_dialog()),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(rename_dialog)

    def remove_task(e: ft.ControlEvent) -> None:
        task_list_view.current.controls.remove(e.control.parent.parent)

    def convert_one(
        input_format: str,
        output_format: str,
        max_track_count: int,
        save_folder_str: str,
        list_tile: ft.ListTile,
        *sub_tasks: list[ft.ListTile],
    ) -> None:
        conversion_mode = conversion_mode_select.current.value
        if (
            list_tile.leading is None
            or list_tile.subtitle is None
            or list_tile.data is None
            or list_tile.trailing is None
        ):
            return
        save_folder = pathlib.Path(save_folder_str)
        list_tile.data["log_text"] = ""
        list_tile.leading.controls[0].visible = False
        list_tile.leading.controls[1].visible = True
        list_tile.trailing.items[-1].disabled = True
        list_tile.update()
        try:
            with CatchWarnings() as w:
                output_path = temp_path / list_tile.subtitle.value
                if conversion_mode != "split":
                    output_path = output_path.with_suffix(
                        f".{output_format}",
                    )
                input_plugin = plugin_manager.plugins.get("svs", {})[input_format]
                output_plugin = plugin_manager.plugins.get("svs", {})[output_format]
                input_option = {
                    control.data: control.value
                    for control in input_options.current.controls
                    if control.data is not None and hasattr(control, "value")
                }
                if conversion_mode == "merge":
                    child_projects = [
                        input_plugin.load(
                            sub_task.data["path"],
                            input_option,
                        )
                        for sub_task in more_itertools.value_chain(list_tile, sub_tasks)
                        if sub_task.data is not None
                    ]
                    project = Project.merge_projects(child_projects)
                else:
                    project = input_plugin.load(
                        list_tile.data["path"],
                        input_option,
                    )
                for middleware_id, middleware_ref in middleware_options.items():
                    if (
                        middleware_ref.current.header is not None
                        and middleware_ref.current.header.leading.value
                    ):
                        middleware = middleware_manager.plugins.get("middleware", {})[middleware_id]
                        if middleware_ref.current.content is not None:
                            project = middleware.process(
                                project,
                                {
                                    control.data: control.value
                                    for control in middleware_ref.current.content.controls[
                                        -1
                                    ].controls
                                    if control.data is not None and hasattr(control, "value")
                                },
                            )
                output_option = {
                    control.data: control.value
                    for control in output_options.current.controls
                    if control.data is not None and hasattr(control, "value")
                }
                if conversion_mode == "split":
                    output_path.mkdir(parents=True, exist_ok=True)
                    for i, child_project in enumerate(
                        project.split_tracks(max_track_count), start=1
                    ):
                        output_plugin.dump(
                            output_path / f"{list_tile.subtitle.value}_{i:0=2d}.{output_format}",
                            child_project,
                            output_option,
                        )
                else:
                    output_plugin.dump(
                        output_path,
                        project,
                        output_option,
                    )
            if w.output:
                list_tile.data["log_text"] = w.output
            buffer = io.BytesIO()
            if output_path.is_file():
                buffer.write(output_path.read_bytes())
            else:
                with ZipFile(buffer, "w") as zip_file:
                    for child_file in output_path.iterdir():
                        if not child_file.is_file():
                            continue
                        zip_file.writestr(
                            child_file.name,
                            child_file.read_bytes(),
                        )
            if conversion_mode != "split":
                save_path = save_folder / output_path.name
            else:
                save_path = save_folder / f"{list_tile.subtitle.value}.zip"
            if page.web:
                loop.create_task(
                    file_picker.save_file(
                        file_name=save_path.name,
                        src_bytes=buffer.getvalue(),
                    )
                )
            else:
                save_path.write_bytes(buffer.getvalue())
            if w.output:
                list_tile.leading.controls[0].name = ft.Icons.WARNING_OUTLINED
                list_tile.leading.controls[0].color = ft.Colors.YELLOW_400
            else:
                list_tile.leading.controls[0].name = ft.Icons.CHECK_CIRCLE_OUTLINED
                list_tile.leading.controls[0].color = ft.Colors.GREEN_400
        except Exception:
            list_tile.leading.controls[0].name = ft.Icons.ERROR_OUTLINED
            list_tile.leading.controls[0].color = ft.Colors.RED_400
            list_tile.data["log_text"] = traceback.format_exc()
        list_tile.leading.controls[0].visible = True
        list_tile.leading.controls[1].visible = False
        list_tile.trailing.items[-1].disabled = False
        list_tile.update()

    async def on_route_change(event: ft.RouteChangeEvent | None = None) -> None:
        page.views.clear()
        await load_lyric_rules_from_prefs()

        def click_navigation_bar(event: ft.ControlEvent | None) -> None:
            for index, p in enumerate(pages.controls):
                p.visible = index == bottom_nav_bar.selected_index
            page.update()

        async def convert_all(e: ft.ControlEvent) -> None:
            if (
                (input_format := await shared_preferences.get("last_input_format")) is None
                or (output_format := await shared_preferences.get("last_output_format")) is None
                or (max_track_count := await shared_preferences.get("max_track_count")) is None
                or (
                    save_folder_str := (
                        settings.save_folder
                        if page.web
                        else (await shared_preferences.get("save_folder")).strip('"')
                    )
                )
                is None
            ):
                return
            await load_lyric_rules_from_prefs()
            settings.lyric_replace_rules = {
                group_name: [
                    LyricsReplacement(
                        mode=LyricsReplaceMode(r.get("mode", "full")),
                        pattern_main=r.get("pattern_main", ""),
                        pattern_prefix=r.get("pattern_prefix", ""),
                        pattern_suffix=r.get("pattern_suffix", ""),
                        replacement=r.get("replacement", ""),
                        flags=re.RegexFlag(r.get("flags", re.IGNORECASE.value)),
                    )
                    for r in rules
                ]
                for group_name, rules in lyric_replace_rules.items()
            }
            bottom_nav_bar.selected_index = 1
            click_navigation_bar(None)
            if conversion_mode_select.current.value != "merge":
                for list_tile in task_list_view.current.controls:
                    page.run_thread(
                        convert_one,
                        input_format,
                        output_format,
                        max_track_count,
                        save_folder_str,
                        list_tile,
                    )
            elif len(task_list_view.current.controls) > 0:
                page.run_thread(
                    convert_one,
                    input_format,
                    output_format,
                    max_track_count,
                    save_folder_str,
                    task_list_view.current.controls[0],
                    *task_list_view.current.controls[1:],
                )

        bottom_nav_bar = ft.NavigationBar(
            on_change=click_navigation_bar,
            destinations=[
                ft.NavigationBarDestination(
                    icon=ft.Icons.SETTINGS_APPLICATIONS_OUTLINED, label=_("Basic Settings")
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.TASK_ALT_OUTLINED, label=_("Conversion mode & Task list")
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.SETTINGS_OUTLINED, label=_("Advanced Options")
                ),
            ],
        )
        switch_theme_btn = ft.PopupMenuButton(
            icon=ft.Icons.PALETTE_OUTLINED,
            tooltip=_("Switch Theme"),
            menu_position=ft.PopupMenuPosition.UNDER,
            items=[
                ft.PopupMenuItem(
                    content=_("System"),
                    icon=ft.Icons.BRIGHTNESS_AUTO_OUTLINED,
                    on_click=partial(change_theme, "System"),
                ),
                ft.PopupMenuItem(
                    content=_("Light"),
                    icon=ft.Icons.LIGHT_MODE_OUTLINED,
                    on_click=partial(change_theme, "Light"),
                ),
                ft.PopupMenuItem(
                    content=_("Dark"),
                    icon=ft.Icons.DARK_MODE_OUTLINED,
                    on_click=partial(change_theme, "Dark"),
                ),
            ],
        )
        switch_language_btn = ft.PopupMenuButton(
            icon=ft.Icons.TRANSLATE_OUTLINED,
            tooltip=_("Switch Language"),
            menu_position=ft.PopupMenuPosition.UNDER,
            items=[
                ft.PopupMenuItem(content="简体中文", on_click=partial(change_language, "zh_CN")),
                ft.PopupMenuItem(content="English", on_click=partial(change_language, "en_US")),
                ft.PopupMenuItem(content="Deutsch", on_click=partial(change_language, "de_DE")),
            ],
        )
        window_buttons = []
        maximize_button = None

        def on_maximize_click(e: ft.ControlEvent | ft.TapEvent) -> None:
            page.window.maximized = not page.window.maximized
            page.update()
            if maximize_button is None:
                return
            if page.window.maximized:
                maximize_button.current.icon = ft.Icons.CLOSE_FULLSCREEN_OUTLINED
                maximize_button.current.tooltip = _("Restore")
            else:
                maximize_button.current.icon = ft.Icons.OPEN_IN_FULL_OUTLINED
                maximize_button.current.tooltip = _("Maximize")

        if page.platform not in [ft.PagePlatform.IOS, ft.PagePlatform.ANDROID] and not page.web:
            maximize_button = ft.Ref[ft.IconButton]()

            def on_minimize_click(e: ft.ControlEvent) -> None:
                page.window.minimized = True
                page.update()

            async def on_close(e: ft.ControlEvent) -> None:
                await page.window.close()

            window_buttons.extend(
                [
                    ft.IconButton(
                        icon=ft.Icons.MINIMIZE_OUTLINED,
                        tooltip=_("Minimize"),
                        on_click=on_minimize_click,
                    ),
                    ft.IconButton(
                        ref=maximize_button,
                        icon=ft.Icons.OPEN_IN_FULL_OUTLINED,
                        tooltip=_("Maximize"),
                        on_click=on_maximize_click,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE_OUTLINED,
                        hover_color=ft.Colors.RED_400,
                        tooltip=_("Close"),
                        on_click=on_close,
                    ),
                ]
            )

        async def swap_formats(e: ft.ControlEvent) -> None:
            if (
                input_select.current.value not in readonly_plugin_ids
                and output_select.current.value not in writeonly_plugin_ids
            ):
                last_output_format, last_input_format = (
                    output_select.current.value,
                    input_select.current.value,
                )
                await set_last_output_format(last_input_format)
                await set_last_input_format(last_output_format)
                page.update()

        def show_plugin_info(control: ft.Ref[ft.Dropdown]) -> None:
            if control.current.value:
                plugin_obj = plugin_manager.plugins.get("svs", {})[control.current.value]
                page.views.append(
                    ft.View(
                        route="/plugin_info",
                        appbar=ft.AppBar(
                            title=ft.Text(plugin_obj.info.name),
                            center_title=True,
                            bgcolor=ft.Colors.SURFACE,
                            leading=ft.IconButton(
                                ft.Icons.ARROW_BACK_OUTLINED,
                                tooltip=_("Back"),
                                on_click=lambda _: view_pop(None),
                            ),
                        ),
                        controls=[
                            ft.ResponsiveRow(
                                [
                                    ft.Image(
                                        src=plugin_obj.info.icon_base64,
                                        fit=ft.BoxFit.FILL,
                                        col=3,
                                        width=100,
                                        height=100,
                                        border_radius=50,
                                    ),
                                    ft.ResponsiveRow(
                                        [
                                            ft.Icon(ft.Icons.BOOKMARK_OUTLINE_OUTLINED, col=1),
                                            ft.Text(
                                                plugin_obj.version, tooltip=_("Version"), col=3
                                            ),
                                            ft.Icon(ft.Icons.PERSON_OUTLINE_OUTLINED, col=1),
                                            ft.Row(
                                                [
                                                    ft.Text(
                                                        spans=[
                                                            ft.TextSpan(
                                                                _(plugin_obj.info.author),
                                                                ft.TextStyle(
                                                                    decoration=ft.TextDecoration.UNDERLINE
                                                                ),
                                                                url=plugin_obj.info.website,
                                                            ),
                                                        ],
                                                        tooltip=plugin_obj.info.website,
                                                    ),
                                                    ft.Icon(ft.Icons.OPEN_IN_NEW_OUTLINED),
                                                ],
                                                col=7,
                                            ),
                                            ft.Icon(ft.Icons.INSERT_DRIVE_FILE_OUTLINED, col=1),
                                            ft.Text(
                                                f"{_(plugin_obj.info.file_format)} (*.{plugin_obj.info.suffix})",
                                                col=11,
                                            ),
                                        ],
                                        col=9,
                                    ),
                                    ft.Divider(),
                                    ft.Text(
                                        spans=[
                                            ft.TextSpan(
                                                _("Introduction"),
                                                ft.TextStyle(weight=ft.FontWeight.BOLD),
                                            ),
                                        ],
                                        col=12,
                                    ),
                                    ft.Text(_(plugin_obj.info.description)),
                                ],
                            )
                        ],
                    )
                )
                page.update()

        pages = ft.Stack(
            [
                ft.Column(
                    [
                        ft.ResponsiveRow(
                            [
                                ft.Dropdown(
                                    ref=input_select,
                                    value=await shared_preferences.get("last_input_format"),
                                    label=_("Import format"),
                                    text_size=14,
                                    options=[
                                        ft.DropdownOption(
                                            plugin_id,
                                            f"{_(plugin_obj.info.file_format)} (*.{plugin_obj.info.suffix})",
                                        )
                                        for plugin_id, plugin_obj in plugin_manager.plugins.get(
                                            "svs", {}
                                        ).items()
                                        if plugin_id not in writeonly_plugin_ids
                                    ],
                                    col=10,
                                    dense=True,
                                    on_select=set_last_input_format,
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.INFO_OUTLINE,
                                    tooltip=_("View Detail Information"),
                                    col=2,
                                    on_click=lambda _: show_plugin_info(input_select),
                                ),
                                ft.Container(col=10),
                                ft.IconButton(
                                    icon=ft.Icons.SWAP_VERT_CIRCLE_OUTLINED,
                                    tooltip=_("Swap Input and Output"),
                                    col=2,
                                    on_click=swap_formats,
                                ),
                                ft.Dropdown(
                                    ref=output_select,
                                    value=await shared_preferences.get("last_output_format"),
                                    label=_("Export format"),
                                    text_size=14,
                                    options=[
                                        ft.DropdownOption(
                                            plugin_id,
                                            f"{_(plugin_obj.info.file_format)} (*.{plugin_obj.info.suffix})",
                                        )
                                        for plugin_id, plugin_obj in plugin_manager.plugins.get(
                                            "svs", {}
                                        ).items()
                                        if plugin_id not in readonly_plugin_ids
                                    ],
                                    col=10,
                                    dense=True,
                                    on_select=set_last_output_format,
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.INFO_OUTLINE,
                                    tooltip=_("View Detail Information"),
                                    col=2,
                                    on_click=lambda _: show_plugin_info(output_select),
                                ),
                                ft.Switch(
                                    label=_("Auto detect import format"),
                                    value=ensure_bool(
                                        await shared_preferences.get("auto_detect_input_format")
                                    ),
                                    col=12,
                                    on_change=change_auto_detect_input_format,
                                ),
                                ft.Switch(
                                    label=_("Reset list when import format changed"),
                                    value=ensure_bool(
                                        await shared_preferences.get("reset_tasks_on_input_change")
                                    ),
                                    col=12,
                                    on_change=change_reset_tasks_on_input_change,
                                ),
                                ft.TextField(
                                    ref=save_folder_text_field,
                                    label=_("Output Folder"),
                                    value=(await shared_preferences.get("save_folder")).strip('"'),
                                    col=10,
                                    visible=not page.web,
                                ),
                                ft.IconButton(
                                    ft.Icons.FOLDER_OPEN_OUTLINED,
                                    tooltip=_("Change Output Directory"),
                                    col=2,
                                    on_click=select_save_folder,
                                    visible=not page.web,
                                ),
                                ft.Button(
                                    _("Request permission to access files"),
                                    data=fph.Permission.MANAGE_EXTERNAL_STORAGE,
                                    on_click=check_permission,
                                    col=12,
                                    visible=permission_handler is not None,
                                ),
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        )
                    ],
                    visible=True,
                ),
                ft.Column(
                    [
                        ft.Dropdown(
                            ref=conversion_mode_select,
                            value="direct",
                            label=_("Conversion mode"),
                            options=[
                                ft.DropdownOption("direct", _("Direct")),
                                ft.DropdownOption("split", _("Split")),
                                ft.DropdownOption("merge", _("Merge")),
                            ],
                        ),
                        ft.ResponsiveRow(
                            [
                                ft.Text(_("Max track count"), col=4),
                                ft.Slider(
                                    value=int(
                                        float(await shared_preferences.get("max_track_count"))
                                    ),
                                    min=1,
                                    max=100,
                                    divisions=100,
                                    label="{value}",
                                    col=8,
                                    on_change=change_max_track_count,
                                ),
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.ReorderableListView(
                            ref=task_list_view,
                            height=400,
                            padding=ft.Padding.symmetric(vertical=10),
                        ),
                    ],
                    scroll=ft.ScrollMode.ADAPTIVE,
                    visible=False,
                ),
                ft.Column(
                    [
                        ft.ExpansionPanelList(
                            elevation=8,
                            scroll=ft.ScrollMode.ALWAYS,
                            controls=[
                                ft.ExpansionPanel(
                                    header=ft.ListTile(
                                        leading=ft.Icon(ft.Icons.INPUT),
                                        title=ft.Text(_("Input Options")),
                                    ),
                                    content=ft.Column(
                                        [
                                            ft.Container(height=2),
                                            ft.ResponsiveRow(
                                                controls=build_input_options(
                                                    await shared_preferences.get(
                                                        "last_input_format"
                                                    )
                                                ),
                                                ref=input_options,
                                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                            ),
                                        ]
                                    ),
                                ),
                                *(
                                    ft.ExpansionPanel(
                                        ref=middleware_ref,
                                        header=ft.ListTile(
                                            leading=ft.Switch(value=False),
                                            title=ft.Text(
                                                _(
                                                    middleware_manager.plugins.get(
                                                        "middleware", {}
                                                    )[middleware_id].info.name
                                                )
                                            ),
                                        ),
                                        content=ft.Column(
                                            [
                                                ft.Container(height=2),
                                                ft.ResponsiveRow(
                                                    controls=build_middleware_options(
                                                        middleware_id
                                                    ),
                                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                                ),
                                            ]
                                        ),
                                    )
                                    for middleware_id, middleware_ref in middleware_options.items()
                                ),
                                ft.ExpansionPanel(
                                    header=ft.ListTile(
                                        leading=ft.Icon(ft.Icons.OUTPUT),
                                        title=ft.Text(_("Output Options")),
                                    ),
                                    content=ft.Column(
                                        [
                                            ft.Container(height=2),
                                            ft.ResponsiveRow(
                                                controls=build_output_options(
                                                    await shared_preferences.get(
                                                        "last_output_format"
                                                    )
                                                ),
                                                ref=output_options,
                                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                            ),
                                        ],
                                    ),
                                ),
                            ],
                        )
                    ],
                    scroll=ft.ScrollMode.ADAPTIVE,
                    visible=False,
                ),
            ]
        )

        def show_lyrics_replacement_page(e: ft.ControlEvent | None = None) -> None:
            asyncio.create_task(page.close_drawer())
            page.views.append(
                ft.View(
                    route="/lyrics_replacement",
                    appbar=ft.AppBar(
                        title=ft.Text(_("Lyrics Replacement")),
                        bgcolor=ft.Colors.SURFACE,
                        leading=ft.IconButton(
                            ft.Icons.ARROW_BACK_OUTLINED,
                            tooltip=_("Back"),
                            on_click=lambda _: view_pop(None),
                        ),
                    ),
                    controls=[
                        ft.Column(
                            [
                                ft.ResponsiveRow(
                                    [
                                        ft.Dropdown(
                                            label=_("Preset"),
                                            options=[
                                                ft.DropdownOption(group_name, group_name)
                                                for group_name in lyric_replace_rules
                                            ],
                                            value=current_lyric_group,
                                            col=8,
                                            ref=lyric_group_select,
                                            on_select=lambda e: refresh_lyric_rules_table(
                                                e.control.value
                                            ),
                                        ),
                                        ft.IconButton(
                                            ft.Icons.ADD_OUTLINED,
                                            tooltip=_("Add"),
                                            col=2,
                                            on_click=add_lyric_group,
                                        ),
                                        ft.IconButton(
                                            ft.Icons.DELETE_OUTLINED,
                                            tooltip=_("Delete"),
                                            col=2,
                                            on_click=delete_lyric_group,
                                        ),
                                    ],
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                                ft.ListView(
                                    ref=lyric_rules_list_view,
                                    controls=[
                                        build_lyric_rule_tile(i, rule)
                                        for i, rule in enumerate(
                                            get_lyric_rules_for_group(current_lyric_group)
                                        )
                                    ],
                                    height=400,
                                    padding=ft.Padding.symmetric(vertical=10),
                                ),
                                ft.Row(
                                    [
                                        ft.Button(
                                            _("Add"),
                                            icon=ft.Icons.ADD_OUTLINED,
                                            on_click=add_lyric_rule,
                                        ),
                                        ft.Button(
                                            _("Save"),
                                            icon=ft.Icons.SAVE_OUTLINED,
                                            on_click=save_lyric_rules,
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.END,
                                ),
                            ],
                            scroll=ft.ScrollMode.ADAPTIVE,
                        ),
                    ],
                )
            )
            page.update()

        def show_about_page(e: ft.ControlEvent | None = None) -> None:
            asyncio.create_task(page.close_drawer())
            page.views.append(
                ft.View(
                    route="/about",
                    appbar=ft.AppBar(
                        title=ft.Text(_("About")),
                        bgcolor=ft.Colors.SURFACE,
                        leading=ft.IconButton(
                            ft.Icons.ARROW_BACK_OUTLINED,
                            tooltip=_("Back"),
                            on_click=lambda _: view_pop(None),
                        ),
                    ),
                    controls=[
                        ft.ResponsiveRow(
                            [
                                ft.Text(
                                    spans=[
                                        ft.TextSpan(
                                            "LibreSVIP",
                                            ft.TextStyle(size=24, weight=ft.FontWeight.BOLD),
                                        ),
                                    ],
                                    text_align=ft.TextAlign.CENTER,
                                    col=12,
                                ),
                                ft.Text(
                                    _("Version: ") + libresvip.__version__,
                                    text_align=ft.TextAlign.CENTER,
                                    col=12,
                                ),
                                ft.Text(
                                    _("Author: SoulMelody"), text_align=ft.TextAlign.CENTER, col=12
                                ),
                                ft.TextButton(
                                    _("Author's Profile"),
                                    icon=ft.Icons.LIVE_TV_OUTLINED,
                                    url="https://space.bilibili.com/175862486",
                                    col=6,
                                ),
                                ft.TextButton(
                                    _("Repo URL"),
                                    icon=ft.Icons.LOGO_DEV_OUTLINED,
                                    url="https://github.com/SoulMelody/LibreSVIP",
                                    col=6,
                                ),
                                ft.Card(
                                    ft.Column(
                                        [
                                            ft.Text(
                                                _(
                                                    "LibreSVIP is an open-sourced, liberal and extensionable framework that can convert your singing synthesis projects between different file formats.",
                                                )
                                            ),
                                            ft.Text(
                                                _(
                                                    "All people should have the right and freedom to choose. That's why we're committed to giving you a second chance to keep your creations free from the constraints of platforms and coterie.",
                                                )
                                            ),
                                        ]
                                    ),
                                    col=12,
                                ),
                            ],
                        ),
                    ],
                )
            )
            page.update()

        drawer = ft.NavigationDrawer(
            controls=[
                ft.NavigationDrawerDestination(
                    icon=ft.Icons.TEXT_SNIPPET_OUTLINED,
                    label=_("Lyric Replace Rules"),
                ),
                ft.NavigationDrawerDestination(
                    icon=ft.Icons.HELP_OUTLINED,
                    label=_("About"),
                ),
            ],
            on_change=lambda e: (
                show_lyrics_replacement_page()
                if e.control.selected_index == 0
                else show_about_page()
            ),
        )

        page.views.append(
            ft.View(
                route="/",
                appbar=ft.AppBar(
                    title=ft.WindowDragArea(
                        ft.Row([ft.Text("LibreSVIP")], expand=True),
                        expand=True,
                    ),
                    bgcolor=ft.Colors.SURFACE,
                    actions=[
                        ft.IconButton(
                            ft.Icons.ADD_OUTLINED,
                            tooltip=_("Continue Adding files"),
                            on_click=select_files,
                        ),
                        switch_theme_btn,
                        switch_language_btn,
                        ft.IconButton(
                            ft.Icons.MENU_OUTLINED,
                            tooltip=_("More"),
                            on_click=page.show_drawer,
                        ),
                        *window_buttons,
                    ],
                ),
                navigation_bar=bottom_nav_bar,
                drawer=drawer,
                floating_action_button=ft.FloatingActionButton(
                    icon=ft.Icons.PLAY_ARROW_OUTLINED,
                    tooltip=_("Start Conversion"),
                    on_click=convert_all,
                ),
                controls=[pages],
            )
        )
        page.update()

    def view_pop(view: ft.View | None) -> None:
        if len(page.views) == 1:
            return
        page.views.pop()
        top_view = page.views[-1]
        asyncio.create_task(page.push_route(top_view.route or "/"))

    def on_view_pop(event: ft.ViewPopEvent) -> None:
        view_pop(event.view)

    def on_keyboard_event(event: ft.KeyboardEvent) -> None:
        if event.key == "Escape" and len(page.views) > 1:
            view_pop(page.views[-1])

    page.on_view_pop = on_view_pop
    page.on_keyboard_event = on_keyboard_event
    page.on_route_change = on_route_change
    await on_route_change()
