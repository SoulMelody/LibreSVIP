import enum
import io
import pathlib
import traceback
import zipfile
from typing import Optional, get_args, get_type_hints

import flet as ft
import more_itertools
from pydantic import BaseModel
from pydantic_core import PydanticUndefined
from pydantic_extra_types.color import Color
from upath import UPath

import libresvip
from libresvip.core.compat import as_file
from libresvip.core.config import settings
from libresvip.core.constants import res_dir
from libresvip.core.warning_types import CatchWarnings
from libresvip.extension.manager import get_translation, middleware_manager, plugin_manager
from libresvip.model.base import BaseComplexModel, Project
from libresvip.utils import translation
from libresvip.utils.translation import gettext_lazy as _


def main(page: ft.Page) -> None:
    page.title = "LibreSVIP"
    page.window.width = 600
    page.window.height = 700
    page.window.title_bar_hidden = True
    page.window.title_bar_buttons_hidden = True

    with as_file(res_dir / "libresvip.ico") as icon:
        page.window.icon = str(icon)

    if not page.client_storage.contains_key("dark_mode"):
        page.client_storage.set("dark_mode", "System")
    page.theme_mode = ft.ThemeMode((page.client_storage.get("dark_mode") or "System").lower())

    def change_theme(dark_mode: str) -> None:
        page.theme_mode = ft.ThemeMode(dark_mode.lower())
        page.client_storage.set("dark_mode", dark_mode)
        page.update()

    if not (page.client_storage.contains_key("language")):
        page.client_storage.set("language", "en_US")
    translation.singleton_translation = get_translation(page.client_storage.get("language"))

    def change_language(lang: str) -> None:
        page.client_storage.set("language", lang)
        translation.singleton_translation = get_translation(lang)
        page.go(f"/?lang={lang}")

    if not (page.client_storage.contains_key("save_folder")):
        page.client_storage.set("save_folder", ".")
    save_folder_text_field = ft.Ref[ft.TextField]()
    temp_path = UPath("memory:/")

    task_list_view = ft.Ref[ft.ListView]()
    input_select = ft.Ref[ft.Dropdown]()
    output_select = ft.Ref[ft.Dropdown]()
    conversion_mode_select = ft.Ref[ft.Dropdown]()
    input_options = ft.Ref[ft.ResponsiveRow]()
    output_options = ft.Ref[ft.ResponsiveRow]()
    middleware_options = {
        middleware_id: ft.Ref[ft.ExpansionPanel]()
        for middleware_id in middleware_manager.plugin_registry
    }

    def build_options(option_class: BaseModel) -> list[ft.Control]:
        fields = []
        for option_key, field_info in option_class.model_fields.items():
            default_value = None if field_info.default is PydanticUndefined else field_info.default
            if field_info.annotation is None:
                continue
            elif issubclass(field_info.annotation, enum.Enum):
                default_value = default_value.value if default_value is not None else None
                annotations = get_type_hints(
                    field_info.annotation,
                    include_extras=True,
                )
                choices = []
                for enum_item in field_info.annotation:
                    if enum_item.name in annotations:
                        annotated_args = list(
                            get_args(annotations[enum_item.name]),
                        )
                        if len(annotated_args) >= 2:
                            enum_field = annotated_args[1]
                        else:
                            continue
                        choices.append(
                            ft.dropdown.Option(
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
            elif issubclass(field_info.annotation, (str, BaseComplexModel, Color)):
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

    def build_input_options(value: Optional[str]) -> list[ft.Control]:
        if value in plugin_manager.plugin_registry:
            input_plugin = plugin_manager.plugin_registry[value]
            if (
                input_plugin.plugin_object is not None
                and (
                    input_option_cls := get_type_hints(input_plugin.plugin_object.load).get(
                        "options",
                    )
                )
                is not None
            ):
                return build_options(input_option_cls)
        return []

    def build_middleware_options(value: str) -> list[ft.Control]:
        if value in middleware_manager.plugin_registry:
            middleware = middleware_manager.plugin_registry[value]
            if (
                middleware.plugin_object is not None
                and (
                    middleware_option_cls := get_type_hints(middleware.plugin_object.process).get(
                        "options"
                    )
                )
                is not None
            ):
                return build_options(middleware_option_cls)
        return []

    def build_output_options(value: Optional[str]) -> list[ft.Control]:
        if value in plugin_manager.plugin_registry:
            output_plugin = plugin_manager.plugin_registry[value]
            if (
                output_plugin.plugin_object is not None
                and (
                    output_option_cls := get_type_hints(output_plugin.plugin_object.dump).get(
                        "options",
                    )
                )
                is not None
            ):
                return build_options(output_option_cls)
        return []

    def set_last_input_format(value: Optional[str]) -> None:
        if input_select.current.value != value:
            input_select.current.value = value
        last_input_format = page.client_storage.get("last_input_format")
        if last_input_format != value:
            input_options.current.controls = build_input_options(value)
            input_options.current.update()
            reset_tasks_on_input_change = page.client_storage.get("reset_tasks_on_input_change")
            if reset_tasks_on_input_change:
                task_list_view.current.controls.clear()
                task_list_view.current.update()
            page.client_storage.set("last_input_format", value)

    def set_last_output_format(value: Optional[str]) -> None:
        if output_select.current.value != value:
            output_select.current.value = value
        last_output_format = page.client_storage.get("last_output_format")
        if last_output_format != value:
            output_options.current.controls = build_output_options(value)
            output_options.current.update()
            page.client_storage.set("last_output_format", value)

    def show_task_log(e: ft.ControlEvent) -> None:
        list_tile = e.control.parent.parent
        if list_tile.data.get("log_text"):

            def copy_log_text(e: ft.ControlEvent) -> None:
                page.set_clipboard(list_tile.data["log_text"])
                banner: ft.Banner = ft.Banner(
                    ft.Text(_("Copied")),
                    leading=ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE),
                    actions=[ft.TextButton(text=_("OK"), on_click=lambda _: page.close(banner))],
                )
                page.open(banner)

            page.views.append(
                ft.View(
                    "/task_log",
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
                                        ft.ElevatedButton(
                                            text=_("Copy to clipboard"),
                                            on_click=copy_log_text,
                                        )
                                    ],
                                    alignment=ft.MainAxisAlignment.END,
                                ),
                                ft.TextField(
                                    value=list_tile.data["log_text"],
                                    multiline=True,
                                    max_lines=24,
                                    autofocus=True,
                                ),
                            ],
                        )
                    ],
                )
            )
            page.update()

    def on_files_selected(e: ft.FilePickerResultEvent) -> None:
        if e.files:
            auto_detect_input_format = page.client_storage.get("auto_detect_input_format")
            if page.web:
                uf = [
                    ft.FilePickerUploadFile(
                        f.name,
                        upload_url=page.get_upload_url(f.name, 600),
                    )
                    for f in e.files
                ]
                file_picker.upload(uf)
                return
            for file in e.files:
                last_input_format = page.client_storage.get("last_input_format")
                file_path = pathlib.Path(file.path)
                suffix = file_path.suffix.lower().removeprefix(".")
                if (
                    suffix != last_input_format
                    and auto_detect_input_format
                    and suffix in plugin_manager.plugin_registry
                ):
                    set_last_input_format(suffix)
                task_list_view.current.controls.append(
                    ft.ListTile(
                        leading=ft.Stack(
                            [
                                ft.Icon(
                                    ft.Icons.ACCESS_TIME_FILLED_OUTLINED,
                                    color=ft.colors.GREY_400,
                                ),
                                ft.ProgressRing(visible=False),
                            ]
                        ),
                        title=ft.Text(file.name),
                        subtitle=ft.Text(file_path.stem),
                        trailing=ft.PopupMenuButton(
                            items=[
                                ft.PopupMenuItem(
                                    icon=ft.icons.REMOVE_RED_EYE_OUTLINED,
                                    text=_("View Log"),
                                    on_click=show_task_log,
                                ),
                                ft.PopupMenuItem(
                                    icon=ft.icons.EDIT,
                                    text=_("Rename"),
                                    on_click=open_rename_dialog,
                                ),
                                ft.PopupMenuItem(
                                    icon=ft.icons.DELETE_OUTLINE,
                                    text=_("Remove"),
                                    on_click=remove_task,
                                ),
                            ],
                            tooltip=_("Actions"),
                        ),
                        data={"path": file_path, "log_text": ""},
                    )
                )
            page.update()
        if e.path:
            page.client_storage.set("save_folder", e.path)
            if save_folder_text_field.current is not None:
                save_folder_text_field.current.value = e.path
                save_folder_text_field.current.update()

    if not (page.client_storage.contains_key("auto_detect_input_format")):
        page.client_storage.set("auto_detect_input_format", True)

    def change_auto_detect_input_format(e: ft.ControlEvent) -> None:
        page.client_storage.set("auto_detect_input_format", e.control.value)

    if not (page.client_storage.contains_key("reset_tasks_on_input_change")):
        page.client_storage.set("reset_tasks_on_input_change", True)

    def change_reset_tasks_on_input_change(e: ft.ControlEvent) -> None:
        page.client_storage.set("reset_tasks_on_input_change", e.control.value)

    if not (page.client_storage.contains_key("max_track_count")):
        page.client_storage.set("max_track_count", 1)

    def change_max_track_count(e: ft.ControlEvent) -> None:
        page.client_storage.set("max_track_count", e.control.value)

    def on_upload_progress(e: ft.FilePickerUploadEvent) -> None:
        if e.progress == 1.0:
            auto_detect_input_format = page.client_storage.get("auto_detect_input_format")
            last_input_format = page.client_storage.get("last_input_format")
            file_path = settings.save_folder / e.file_name
            suffix = file_path.suffix.lower().removeprefix(".")
            if (
                suffix != last_input_format
                and auto_detect_input_format
                and suffix in plugin_manager.plugin_registry
            ):
                set_last_input_format(suffix)
            task_list_view.current.controls.append(
                ft.ListTile(
                    leading=ft.Stack(
                        [
                            ft.Icon(
                                ft.Icons.ACCESS_TIME_FILLED_OUTLINED,
                                color=ft.colors.GREY_400,
                            ),
                            ft.ProgressRing(visible=False),
                        ]
                    ),
                    title=ft.Text(e.file_name),
                    subtitle=ft.Text(file_path.stem),
                    trailing=ft.PopupMenuButton(
                        items=[
                            ft.PopupMenuItem(
                                icon=ft.icons.REMOVE_RED_EYE_OUTLINED,
                                text=_("View Log"),
                                on_click=show_task_log,
                            ),
                            ft.PopupMenuItem(
                                icon=ft.icons.EDIT,
                                text=_("Rename"),
                                on_click=open_rename_dialog,
                            ),
                            ft.PopupMenuItem(
                                icon=ft.icons.DELETE_OUTLINE,
                                text=_("Remove"),
                                on_click=remove_task,
                            ),
                        ],
                        tooltip=_("Actions"),
                    ),
                    data={"path": file_path, "log_text": ""},
                )
            )
            task_list_view.current.update()

    file_picker = ft.FilePicker(on_result=on_files_selected, on_upload=on_upload_progress)
    permission_handler = ft.PermissionHandler()
    page.overlay.extend([file_picker, permission_handler])

    def check_permission(e: ft.ControlEvent) -> None:
        result = permission_handler.check_permission(e.control.data)
        banner_ref = ft.Ref[ft.Banner]()
        dismiss_btn = ft.TextButton(text=_("OK"), on_click=lambda _: page.close(banner_ref.current))
        if result != ft.PermissionStatus.GRANTED:
            result = permission_handler.request_permission(e.control.data)
            if result == ft.PermissionStatus.GRANTED:
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
        page.open(banner)

    def open_rename_dialog(e: ft.ControlEvent) -> None:
        list_tile = e.control.parent.parent

        def close_rename_dialog() -> None:
            list_tile.subtitle.value = rename_dialog.content.value
            list_tile.subtitle.update()
            page.close(rename_dialog)

        rename_dialog: ft.AlertDialog = ft.AlertDialog(
            title=ft.Text(_("Rename")),
            content=ft.TextField(list_tile.subtitle.value),
            actions=[
                ft.TextButton(_("OK"), on_click=lambda _: close_rename_dialog()),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.open(rename_dialog)

    def remove_task(e: ft.ControlEvent) -> None:
        task_list_view.current.controls.remove(e.control.parent.parent)
        task_list_view.current.update()

    def convert_one(list_tile: ft.ListTile, *sub_tasks: list[ft.ListTile]) -> None:
        conversion_mode = conversion_mode_select.current.value
        if (
            (input_format := page.client_storage.get("last_input_format")) is None
            or (output_format := page.client_storage.get("last_output_format")) is None
            or (max_track_count := page.client_storage.get("max_track_count")) is None
            or (
                save_folder_str := (
                    settings.save_folder if page.web else page.client_storage.get("save_folder")
                )
            )
            is None
            or list_tile.leading is None
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
                input_plugin = plugin_manager.plugin_registry[input_format]
                output_plugin = plugin_manager.plugin_registry[output_format]
                if (
                    input_plugin.plugin_object is not None
                    and (
                        input_option_class := get_type_hints(input_plugin.plugin_object.load).get(
                            "options",
                        )
                    )
                    is not None
                    and output_plugin.plugin_object is not None
                    and (
                        output_option_class := get_type_hints(
                            output_plugin.plugin_object.dump,
                        ).get("options")
                    )
                    is not None
                ):
                    input_option = input_option_class.model_validate(
                        {
                            control.data: control.value
                            for control in input_options.current.controls
                            if control.data is not None and hasattr(control, "value")
                        }
                    )
                    if conversion_mode == "merge":
                        child_projects = [
                            input_plugin.plugin_object.load(
                                sub_task.data["path"],
                                input_option,
                            )
                            for sub_task in more_itertools.value_chain(list_tile, sub_tasks)
                            if sub_task.data is not None
                        ]
                        project = Project.merge_projects(child_projects)
                    else:
                        project = input_plugin.plugin_object.load(
                            list_tile.data["path"],
                            input_option,
                        )
                    for middleware_id, middleware_ref in middleware_options.items():
                        if (
                            middleware_ref.current.header is not None
                            and middleware_ref.current.header.leading.value
                        ):
                            middleware = middleware_manager.plugin_registry[middleware_id]
                            if (
                                middleware_ref.current.content is not None
                                and middleware.plugin_object is not None
                                and hasattr(middleware.plugin_object, "process")
                                and (
                                    middleware_option_cls := get_type_hints(
                                        middleware.plugin_object.process
                                    ).get(
                                        "options",
                                    )
                                )
                            ):
                                project = middleware.plugin_object.process(
                                    project,
                                    middleware_option_cls.model_validate(
                                        {
                                            control.data: control.value
                                            for control in middleware_ref.current.content.controls[
                                                -1
                                            ].controls
                                            if control.data is not None
                                            and hasattr(control, "value")
                                        }
                                    ),
                                )
                    output_option = output_option_class.model_validate(
                        {
                            control.data: control.value
                            for control in output_options.current.controls
                            if control.data is not None and hasattr(control, "value")
                        }
                    )
                    if conversion_mode == "split":
                        output_path.mkdir(parents=True, exist_ok=True)
                        for i, child_project in enumerate(project.split_tracks(max_track_count)):
                            output_plugin.plugin_object.dump(
                                output_path
                                / f"{list_tile.subtitle.value}_{i + 1:0=2d}.{output_format}",
                                child_project,
                                output_option,
                            )
                    else:
                        output_plugin.plugin_object.dump(
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
                with zipfile.ZipFile(buffer, "w") as zip_file:
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
            save_path.write_bytes(buffer.getvalue())
            if page.web:
                page.launch_url(f"/download/{save_path.name}")
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

    def on_route_change(event: ft.RouteChangeEvent) -> None:
        page.views.clear()

        def click_navigation_bar(event: Optional[ft.ControlEvent]) -> None:
            for index, p in enumerate(pages.controls):
                p.visible = index == bottom_nav_bar.selected_index
            page.update()

        def convert_all(e: ft.ControlEvent) -> None:
            bottom_nav_bar.selected_index = 1
            click_navigation_bar(None)
            if conversion_mode_select.current.value != "merge":
                for list_tile in task_list_view.current.controls:
                    page.run_thread(convert_one, list_tile)
            elif len(task_list_view.current.controls) > 0:
                page.run_thread(
                    convert_one,
                    task_list_view.current.controls[0],
                    *task_list_view.current.controls[1:],
                )

        bottom_nav_bar = ft.NavigationBar(
            on_change=click_navigation_bar,
            destinations=[
                ft.NavigationBarDestination(
                    icon=ft.Icons.SWAP_HORIZ_OUTLINED, label=_("Select File Formats")
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
            items=[
                ft.PopupMenuItem(
                    text=_("System"),
                    icon=ft.Icons.BRIGHTNESS_AUTO_OUTLINED,
                    on_click=lambda _: change_theme("System"),
                ),
                ft.PopupMenuItem(
                    text=_("Light"),
                    icon=ft.Icons.LIGHT_MODE_OUTLINED,
                    on_click=lambda _: change_theme("Light"),
                ),
                ft.PopupMenuItem(
                    text=_("Dark"),
                    icon=ft.Icons.DARK_MODE_OUTLINED,
                    on_click=lambda _: change_theme("Dark"),
                ),
            ],
        )
        switch_language_btn = ft.PopupMenuButton(
            icon=ft.Icons.TRANSLATE_OUTLINED,
            tooltip=_("Switch Language"),
            items=[
                ft.PopupMenuItem(text="简体中文", on_click=lambda _: change_language("zh_CN")),
                ft.PopupMenuItem(text="English", on_click=lambda _: change_language("en_US")),
                ft.PopupMenuItem(text="Deutsch", on_click=lambda _: change_language("de_DE")),
            ],
        )
        window_buttons = []
        if page.platform not in [ft.PagePlatform.IOS, ft.PagePlatform.ANDROID] and not page.web:
            maximize_button = ft.Ref[ft.IconButton]()

            def on_minimize_click(e: ft.ControlEvent) -> None:
                page.window.minimized = True
                page.update()

            def on_maximize_click(e: ft.ControlEvent) -> None:
                page.window.maximized = not page.window.maximized
                page.update()
                if page.window.maximized:
                    maximize_button.current.icon = ft.Icons.CLOSE_FULLSCREEN_OUTLINED
                    maximize_button.current.tooltip = _("Restore")
                else:
                    maximize_button.current.icon = ft.Icons.OPEN_IN_FULL_OUTLINED
                    maximize_button.current.tooltip = _("Maximize")
                maximize_button.current.update()

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
                        on_click=lambda _: page.window.close(),
                    ),
                ]
            )

        def swap_formats(e: ft.ControlEvent) -> None:
            last_output_format, last_input_format = (
                output_select.current.value,
                input_select.current.value,
            )
            set_last_output_format(last_input_format)
            set_last_input_format(last_output_format)
            page.update()

        def show_plugin_info(control: ft.Ref[ft.Dropdown]) -> None:
            if control.current.value:
                plugin_obj = plugin_manager.plugin_registry[control.current.value]
                page.views.append(
                    ft.View(
                        "/plugin_info",
                        appbar=ft.AppBar(
                            title=ft.Text(plugin_obj.name),
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
                                        src_base64=plugin_obj.icon_base64,
                                        fit=ft.ImageFit.FILL,
                                        col=3,
                                    ),
                                    ft.ResponsiveRow(
                                        [
                                            ft.Icon(ft.Icons.BOOKMARK_OUTLINE_OUTLINED, col=1),
                                            ft.Text(
                                                str(plugin_obj.version), tooltip=_("Version"), col=3
                                            ),
                                            ft.Icon(ft.Icons.PERSON_OUTLINE_OUTLINED, col=1),
                                            ft.Row(
                                                [
                                                    ft.Text(
                                                        spans=[
                                                            ft.TextSpan(
                                                                _(plugin_obj.author),
                                                                ft.TextStyle(
                                                                    decoration=ft.TextDecoration.UNDERLINE
                                                                ),
                                                                url=plugin_obj.website,
                                                            ),
                                                        ],
                                                        tooltip=plugin_obj.website,
                                                    ),
                                                    ft.Icon(ft.Icons.OPEN_IN_NEW_OUTLINED),
                                                ],
                                                col=7,
                                            ),
                                            ft.Icon(ft.Icons.INSERT_DRIVE_FILE_OUTLINED, col=1),
                                            ft.Text(
                                                f"{_(plugin_obj.file_format)} (*.{plugin_obj.suffix})",
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
                                    ft.Text(_(plugin_obj.description)),
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
                                    value=page.client_storage.get("last_input_format"),
                                    label=_("Import format"),
                                    text_size=14,
                                    options=[
                                        ft.dropdown.Option(
                                            plugin_id,
                                            f"{_(plugin_obj.file_format)} (*.{plugin_obj.suffix})",
                                        )
                                        for plugin_id, plugin_obj in plugin_manager.plugin_registry.items()
                                    ],
                                    col=10,
                                    dense=True,
                                    on_change=lambda e: set_last_input_format(e.control.value),
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
                                    value=page.client_storage.get("last_output_format"),
                                    label=_("Export format"),
                                    text_size=14,
                                    options=[
                                        ft.dropdown.Option(
                                            plugin_id,
                                            f"{_(plugin_obj.file_format)} (*.{plugin_obj.suffix})",
                                        )
                                        for plugin_id, plugin_obj in plugin_manager.plugin_registry.items()
                                    ],
                                    col=10,
                                    dense=True,
                                    on_change=lambda e: set_last_output_format(e.control.value),
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.INFO_OUTLINE,
                                    tooltip=_("View Detail Information"),
                                    col=2,
                                    on_click=lambda _: show_plugin_info(output_select),
                                ),
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
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
                                ft.dropdown.Option("direct", _("Direct")),
                                ft.dropdown.Option("split", _("Split")),
                                ft.dropdown.Option("merge", _("Merge")),
                            ],
                        ),
                        ft.ListView(
                            ref=task_list_view,
                            expand=1,
                            spacing=10,
                            auto_scroll=True,
                            padding=ft.padding.symmetric(vertical=10),
                        ),
                    ],
                    visible=False,
                ),
                ft.Column(
                    [
                        ft.ExpansionPanelList(
                            elevation=8,
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
                                                    page.client_storage.get("last_input_format")
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
                                                    middleware_manager.plugin_registry[
                                                        middleware_id
                                                    ].name
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
                                                    page.client_storage.get("last_output_format")
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
                    scroll=ft.ScrollMode.ALWAYS,
                    height=400,
                    visible=False,
                ),
            ]
        )

        def select_page(e: ft.ControlEvent) -> None:
            if drawer.selected_index == 0:
                page.go("/")
            elif drawer.selected_index == 1:
                page.go("/settings")
            else:
                page.go("/about")

        drawer = ft.NavigationDrawer(
            controls=[
                ft.NavigationDrawerDestination(icon=ft.Icons.LOOP_OUTLINED, label=_("Converter")),
                ft.NavigationDrawerDestination(
                    icon=ft.Icons.SETTINGS_APPLICATIONS_OUTLINED,
                    label=_("Basic Settings"),
                ),
                ft.NavigationDrawerDestination(
                    icon=ft.Icons.HELP_OUTLINED,
                    label=_("About"),
                ),
            ],
            on_change=select_page,
        )

        page.views.append(
            ft.View(
                "/",
                appbar=ft.AppBar(
                    title=ft.WindowDragArea(
                        ft.Row([ft.Text("LibreSVIP")], expand=True), expand=True
                    ),
                    leading=ft.IconButton(
                        ft.Icons.MENU_OUTLINED, on_click=lambda _: page.open(drawer)
                    ),
                    bgcolor=ft.Colors.SURFACE,
                    actions=[
                        ft.IconButton(
                            ft.Icons.ADD_OUTLINED,
                            tooltip=_("Continue Adding files"),
                            on_click=lambda e: file_picker.pick_files(
                                _("Select files to convert"), allow_multiple=True
                            ),
                        ),
                        switch_theme_btn,
                        switch_language_btn,
                        *window_buttons,
                    ],
                ),
                navigation_bar=bottom_nav_bar,
                floating_action_button=ft.FloatingActionButton(
                    icon=ft.Icons.PLAY_ARROW_OUTLINED,
                    tooltip=_("Start Conversion"),
                    on_click=convert_all,
                ),
                drawer=drawer,
                controls=[pages],
            )
        )
        if event.route == "/settings":
            page.views.append(
                ft.View(
                    appbar=ft.AppBar(
                        title=ft.WindowDragArea(
                            ft.Row([ft.Text(_("Basic Settings"))], expand=True), expand=True
                        ),
                        center_title=True,
                        bgcolor=ft.Colors.SURFACE,
                        actions=[switch_theme_btn, switch_language_btn, *window_buttons],
                        leading=ft.IconButton(
                            ft.Icons.ARROW_BACK_OUTLINED,
                            tooltip=_("Back"),
                            on_click=lambda _: view_pop(None),
                        ),
                    ),
                    controls=[
                        ft.ResponsiveRow(
                            [
                                ft.Switch(
                                    _("Auto detect import format"),
                                    value=page.client_storage.get("auto_detect_input_format"),
                                    col=12,
                                    on_change=change_auto_detect_input_format,
                                ),
                                ft.Switch(
                                    _("Reset list when import format changed"),
                                    value=page.client_storage.get("reset_tasks_on_input_change"),
                                    col=12,
                                    on_change=change_reset_tasks_on_input_change,
                                ),
                                ft.Text(_("Max track count"), col=4),
                                ft.Slider(
                                    value=page.client_storage.get("max_track_count"),
                                    min=1,
                                    max=100,
                                    divisions=100,
                                    label="{value}",
                                    col=8,
                                    on_change=change_max_track_count,
                                ),
                                ft.TextField(
                                    ref=save_folder_text_field,
                                    label=_("Output Folder"),
                                    value=page.client_storage.get("save_folder"),
                                    col=10,
                                ),
                                ft.IconButton(
                                    ft.Icons.FOLDER_OPEN_OUTLINED,
                                    tooltip=_("Change Output Directory"),
                                    col=2,
                                    on_click=lambda e: file_picker.get_directory_path(
                                        _("Change Output Directory")
                                    ),
                                ),
                                ft.ElevatedButton(
                                    _("Request permission to access files"),
                                    data=ft.PermissionType.MANAGE_EXTERNAL_STORAGE,
                                    on_click=check_permission,
                                    col=12,
                                ),
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        )
                    ],
                )
            )
        elif event.route == "/about":
            page.views.append(
                ft.View(
                    appbar=ft.AppBar(
                        title=ft.WindowDragArea(
                            ft.Row([ft.Text(_("About"))], expand=True), expand=True
                        ),
                        center_title=True,
                        bgcolor=ft.Colors.SURFACE,
                        actions=[switch_theme_btn, switch_language_btn, *window_buttons],
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
                        )
                    ],
                )
            )
        page.update()

    def view_pop(view: Optional[ft.View]) -> None:
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route or "/")

    def on_view_pop(event: ft.ViewPopEvent) -> None:
        view_pop(event.view)

    def on_keyboard_event(event: ft.KeyboardEvent) -> None:
        if event.key == "Escape" and len(page.views) > 1:
            view_pop(page.views[-1])

    page.on_view_pop = on_view_pop
    page.on_keyboard_event = on_keyboard_event
    page.on_route_change = on_route_change
    page.go("/")
