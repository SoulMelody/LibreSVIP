import flet as ft

import libresvip
from libresvip.core.compat import as_file
from libresvip.core.constants import res_dir
from libresvip.extension.manager import get_translation, plugin_manager
from libresvip.utils import translation
from libresvip.utils.translation import gettext_lazy as _


async def main(page: ft.Page) -> None:
    page.title = "LibreSVIP"
    page.window.width = 600
    page.window.height = 700

    if not (await page.client_storage.contains_key_async("dark_mode")):
        await page.client_storage.set_async("dark_mode", "System")
    page.theme_mode = ft.ThemeMode(
        (await page.client_storage.get_async("dark_mode") or "System").lower()
    )

    def change_theme(dark_mode: str) -> None:
        page.theme_mode = ft.ThemeMode(dark_mode.lower())
        page.client_storage.set("dark_mode", dark_mode)
        page.update()

    if not (await page.client_storage.contains_key_async("language")):
        await page.client_storage.set_async("language", "en_US")
    translation.singleton_translation = get_translation(
        await page.client_storage.get_async("language")
    )

    def change_language(lang: str) -> None:
        page.client_storage.set("language", lang)
        translation.singleton_translation = get_translation(lang)

        def close_banner(e: ft.ControlEvent) -> None:
            page.close(banner)

        dismiss_btn = ft.TextButton(text=_("OK"), on_click=close_banner)
        banner = ft.Banner(
            ft.Text(_("Language settings changed, please restart the app to apply the changes.")),
            leading=ft.Icon(ft.Icons.WARNING_OUTLINED),
            actions=[dismiss_btn],
        )
        page.open(banner)

    if not (await page.client_storage.contains_key_async("save_folder")):
        await page.client_storage.set_async("save_folder", ".")
    save_folder_text_field = ft.TextField(
        label=_("Output Folder"), value=await page.client_storage.get_async("save_folder"), col=10
    )

    def on_files_selected(e: ft.FilePickerResultEvent) -> None:
        if e.files:
            pass
        if e.path:
            page.client_storage.set("save_folder", e.path)
            save_folder_text_field.value = e.path
            save_folder_text_field.update()

    if not (await page.client_storage.contains_key_async("auto_detect_input_format")):
        await page.client_storage.set_async("auto_detect_input_format", True)

    def change_auto_detect_input_format(e: ft.ControlEvent) -> None:
        page.client_storage.set("auto_detect_input_format", e.control.value)

    if not (await page.client_storage.contains_key_async("reset_tasks_on_input_change")):
        await page.client_storage.set_async("reset_tasks_on_input_change", True)

    def change_reset_tasks_on_input_change(e: ft.ControlEvent) -> None:
        page.client_storage.set("reset_tasks_on_input_change", e.control.value)

    if not (await page.client_storage.contains_key_async("max_track_count")):
        await page.client_storage.set_async("max_track_count", 1)

    def change_max_track_count(e: ft.ControlEvent) -> None:
        page.client_storage.set("max_track_count", e.control.value)

    def change_last_input_format(e: ft.ControlEvent) -> None:
        page.client_storage.set("last_input_format", e.control.value)

    def change_last_output_format(e: ft.ControlEvent) -> None:
        page.client_storage.set("last_output_format", e.control.value)

    with as_file(res_dir / "libresvip.ico") as icon:
        page.window.icon = str(icon)

    file_picker = ft.FilePicker(on_result=on_files_selected)
    permission_handler = ft.PermissionHandler()
    page.overlay.extend([file_picker, permission_handler])

    def click_navigation_bar(event: ft.ControlEvent) -> None:
        if event.control.selected_index == 0:
            page.go("/")
        elif event.control.selected_index == 1:
            page.go("/settings")
        else:
            page.go("/about")

    def check_permission(e: ft.ControlEvent) -> None:
        result = permission_handler.check_permission(e.control.data)

        def close_banner(e: ft.ControlEvent) -> None:
            page.close(banner)

        dismiss_btn = ft.TextButton(text=_("OK"), on_click=close_banner)
        if result != ft.PermissionStatus.GRANTED:
            result = permission_handler.request_permission(e.control.data)
            if result == ft.PermissionStatus.GRANTED:
                banner = ft.Banner(
                    ft.Text(_("Permission granted, you can now select files from your device.")),
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
                    leading=ft.Icon(ft.Icons.WARNING_OUTLINED),
                    actions=[dismiss_btn],
                )
        else:
            banner = ft.Banner(
                ft.Text(
                    _("Permission already granted, you can now select files from your device.")
                ),
                leading=ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINED),
                actions=[dismiss_btn],
            )
        page.open(banner)

    bottom_nav_bar = ft.NavigationBar(
        on_change=click_navigation_bar,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.LOOP_OUTLINED, label=_("Converter")),
            ft.NavigationBarDestination(
                icon=ft.Icons.SETTINGS_APPLICATIONS_OUTLINED, label=_("Basic Settings")
            ),
            ft.NavigationBarDestination(icon=ft.Icons.HELP_OUTLINED, label=_("About")),
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
        ],
    )

    def on_route_change(event: ft.RouteChangeEvent) -> None:
        page.views.clear()
        if event.route == "/":
            input_select = ft.Dropdown(
                value=page.client_storage.get("last_input_format"),
                label=_("Import format"),
                text_size=16,
                options=[
                    ft.dropdown.Option(
                        plugin_id, f"{_(plugin_obj.file_format)} (*.{plugin_obj.suffix})"
                    )
                    for plugin_id, plugin_obj in plugin_manager.plugin_registry.items()
                ],
                col=10,
                on_change=change_last_input_format,
            )
            output_select = ft.Dropdown(
                value=page.client_storage.get("last_output_format"),
                label=_("Export format"),
                text_size=16,
                options=[
                    ft.dropdown.Option(
                        plugin_id, f"{_(plugin_obj.file_format)} (*.{plugin_obj.suffix})"
                    )
                    for plugin_id, plugin_obj in plugin_manager.plugin_registry.items()
                ],
                col=10,
                on_change=change_last_output_format,
            )

            def swap_formats(e: ft.ControlEvent) -> None:
                input_select.value, output_select.value = output_select.value, input_select.value
                page.client_storage.set("last_input_format", input_select.value)
                page.client_storage.set("last_output_format", output_select.value)
                page.update()

            def show_plugin_info(control: ft.Dropdown) -> None:
                if control.value:
                    plugin_obj = plugin_manager.plugin_registry[control.value]
                    plugin_info_view: ft.View = ft.View(
                        "/plugin_info",
                        appbar=ft.AppBar(
                            title=ft.Text(plugin_obj.name),
                            center_title=True,
                            bgcolor=ft.Colors.SURFACE,
                            leading=ft.IconButton(
                                ft.Icons.ARROW_BACK_OUTLINED,
                                tooltip=_("Back"),
                                on_click=lambda _: view_pop(plugin_info_view),
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
                                            ft.Icon(ft.Icons.TAG_OUTLINED, col=1),
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
                                            ft.Icon(ft.Icons.FOLDER_OPEN_OUTLINED, col=1),
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
                    page.views.append(plugin_info_view)
                    page.update()

            pages = [
                ft.Column(
                    [
                        ft.Dropdown(
                            value="direct",
                            label=_("Conversion mode"),
                            options=[
                                ft.dropdown.Option("direct", _("Direct")),
                                ft.dropdown.Option("split", _("Split")),
                                ft.dropdown.Option("merge", _("Merge")),
                            ],
                        ),
                        ft.ResponsiveRow(
                            [
                                input_select,
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
                                output_select,
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
                        ft.ExpansionPanelList(
                            elevation=8,
                            controls=[
                                ft.ExpansionPanel(
                                    header=ft.ListTile(title=ft.Text(_("Input Options"))),
                                ),
                                ft.ExpansionPanel(
                                    header=ft.ListTile(title=ft.Text(_("Intermediate Processing"))),
                                ),
                                ft.ExpansionPanel(
                                    header=ft.ListTile(title=ft.Text(_("Output Options"))),
                                ),
                            ],
                        )
                    ],
                    visible=False,
                ),
                ft.ListView(
                    controls=[
                        ft.ListTile(
                            leading=ft.Stack(
                                [
                                    ft.Icon(
                                        ft.Icons.CHECK_CIRCLE_OUTLINED, color=ft.colors.GREEN_400
                                    ),
                                    ft.ProgressRing(visible=False),
                                ]
                            ),
                            title=ft.Text("Foo"),
                            subtitle=ft.Text("Bar"),
                            trailing=ft.PopupMenuButton(
                                items=[
                                    ft.PopupMenuItem(
                                        icon=ft.icons.REMOVE_RED_EYE_OUTLINED, text=_("View Log")
                                    ),
                                    ft.PopupMenuItem(icon=ft.icons.EDIT, text=_("Rename")),
                                    ft.PopupMenuItem(
                                        icon=ft.icons.DELETE_OUTLINE, text=_("Remove")
                                    ),
                                ],
                                tooltip=_("Actions"),
                            ),
                        ),
                    ],
                    expand=1,
                    spacing=10,
                    auto_scroll=True,
                    visible=False,
                    padding=ft.padding.symmetric(vertical=10),
                ),
            ]

            def select_page(e: ft.ControlEvent) -> None:
                for index, p in enumerate(pages):
                    p.visible = index == drawer.selected_index
                drawer.open = False
                page.update()

            drawer = ft.NavigationDrawer(
                controls=[
                    ft.NavigationDrawerDestination(
                        icon=ft.Icons.SWAP_HORIZ_OUTLINED, label=_("Select File Formats")
                    ),
                    ft.NavigationDrawerDestination(
                        icon=ft.Icons.SETTINGS_OUTLINED,
                        label=_("Advanced Options"),
                    ),
                    ft.NavigationDrawerDestination(
                        icon=ft.Icons.TASK_ALT_OUTLINED,
                        label=_("Task List"),
                    ),
                ],
                on_change=select_page,
            )

            view = ft.View(
                "/",
                appbar=ft.AppBar(
                    title=ft.Text("LibreSVIP"),
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
                    ],
                ),
                navigation_bar=bottom_nav_bar,
                floating_action_button=ft.FloatingActionButton(
                    icon=ft.Icons.PLAY_ARROW_OUTLINED, tooltip=_("Start Conversion")
                ),
                drawer=drawer,
                controls=[
                    ft.Column(pages, alignment=ft.MainAxisAlignment.START, expand=True),
                ],
            )
            page.views.append(view)
        elif event.route == "/settings":
            view = ft.View(
                appbar=ft.AppBar(
                    title=ft.Text(_("Basic Settings")),
                    center_title=True,
                    bgcolor=ft.Colors.SURFACE,
                    actions=[switch_theme_btn, switch_language_btn],
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
                            save_folder_text_field,
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
                navigation_bar=bottom_nav_bar,
            )
            page.views.append(view)
        elif event.route == "/about":
            view = ft.View(
                appbar=ft.AppBar(
                    title=ft.Text(_("About")),
                    center_title=True,
                    bgcolor=ft.Colors.SURFACE,
                    actions=[switch_theme_btn, switch_language_btn],
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
                                icon=ft.Icons.PERSON_OUTLINED,
                                url="https://space.bilibili.com/175862486",
                                col=6,
                            ),
                            ft.TextButton(
                                _("Repo URL"),
                                icon=ft.Icons.CODE_OUTLINED,
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
                navigation_bar=bottom_nav_bar,
            )
            page.views.append(view)
        page.update()

    def view_pop(view: ft.View) -> None:
        page.views.remove(view)
        top_view = page.views[-1]
        page.go(top_view.route or "/")

    page.on_route_change = on_route_change
    page.on_view_pop = view_pop
    page.go("/")
