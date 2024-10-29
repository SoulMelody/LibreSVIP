import contextlib
import pathlib
import platform
from collections.abc import Coroutine
from typing import Any, Union

from textual import on, work
from textual.app import App, ComposeResult
from textual.command import Hit, Hits, Provider
from textual.containers import Container, Horizontal, Right, Vertical, VerticalScroll
from textual.screen import Screen
from textual.validation import Integer
from textual.widgets import (
    Button,
    Collapsible,
    ContentSwitcher,
    DirectoryTree,
    Footer,
    Header,
    Input,
    Label,
    Link,
    ListView,
    Markdown,
    Placeholder,
    ProgressBar,
    Select,
    SelectionList,
    Static,
    Switch,
    Tab,
    TabbedContent,
    TabPane,
    Tabs,
)
from textual.widgets._list_item import ListItem
from textual.widgets.directory_tree import DirEntry
from textual.widgets.selection_list import Selection
from typing_extensions import ParamSpec

import libresvip
from libresvip.core.config import ConflictPolicy, DarkMode, Language, save_settings, settings
from libresvip.extension.manager import get_translation, plugin_manager
from libresvip.utils import translation
from libresvip.utils.translation import gettext_lazy as _

P = ParamSpec("P")

translation.singleton_translation = get_translation()


class LibreSVIPCommandProvider(Provider):
    async def search(self, query: str) -> Hits:
        matcher = self.matcher(query)
        for name, help_text, callback, _discover in self.app.get_system_commands(self.screen):
            if (match := matcher.match(name)) > 0:
                yield Hit(
                    match,
                    matcher.highlight(name),
                    callback,
                    help=help_text,
                )


class RootDirectoryTree(Vertical):
    def __init__(self, root: Union[str, pathlib.Path], *args: P.args, **kwargs: P.kwargs) -> None:
        self.root = root
        self.tree_id = kwargs.pop("id", None)
        super().__init__(*args, **kwargs)

    def get_logical_drive_strings(self) -> list[str]:
        import ctypes.wintypes

        # adapted from winappdbg
        _get_logical_drive_strings_w = ctypes.windll.kernel32.GetLogicalDriveStringsW
        _get_logical_drive_strings_w.argtypes = [ctypes.wintypes.DWORD, ctypes.wintypes.LPWSTR]
        _get_logical_drive_strings_w.restype = ctypes.wintypes.DWORD

        buffer_len = (4 * 26) + 1  # "X:\\\0" from A to Z plus empty string
        buffer = ctypes.create_unicode_buffer("", buffer_len)
        _get_logical_drive_strings_w(buffer_len, buffer)
        drive_strings = []
        string_p = ctypes.addressof(buffer)
        sizeof_wchar = ctypes.sizeof(ctypes.c_wchar)
        while True:
            string_v = ctypes.wstring_at(string_p)
            if string_v == "":
                break
            drive_strings.append(string_v)
            string_p += (len(string_v) * sizeof_wchar) + sizeof_wchar
        return drive_strings

    def compose(self) -> ComposeResult:
        if platform.system() == "Windows":
            with Horizontal(classes="top-pane"):
                yield Label("Select a drive: ", classes="text-middle")
                yield Select(
                    [(drive, drive) for drive in self.get_logical_drive_strings()],
                    id="drive-select",
                )
        yield DirectoryTree(self.root, id=self.tree_id)

    @on(Select.Changed, "#drive-select")
    def on_drive_select(self, event: Select.Changed) -> None:
        if event.value != Select.BLANK:
            self.root = pathlib.Path(event.value)
            directory_tree = self.query_one(DirectoryTree)
            directory_tree.reset_node(
                directory_tree.root, event.value, DirEntry(directory_tree.PATH(self.root))
            )


class PromptScreen(Screen[bool]):
    DEFAULT_CSS = """
    #dialog {
        height: 100%;
        margin: 4 8;
        background: $panel;
        color: $text;
        border: tall $background;
        padding: 1 2;
    }
    Button {
        width: 1fr;
    }
    .question {
        text-style: bold;
        height: 100%;
        content-align: center middle;
    }
    .buttons {
        width: 100%;
        height: auto;
        dock: bottom;
    }
    """

    def __init__(self, output_path: str) -> None:
        self.output_path = output_path
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header(icon="☰")
        yield Footer()
        yield Container(
            Static(
                _("File {} already exists. Overwrite?").format(self.output_path), classes="question"
            ),
            Horizontal(
                Button(_("OK"), id="yes", variant="success"),
                Button(_("Cancel"), id="no", variant="error"),
                classes="buttons",
            ),
        )

    @on(Button.Pressed, "#yes")
    def handle_yes(self) -> None:
        self.dismiss(True)

    @on(Button.Pressed, "#no")
    def handle_no(self) -> None:
        self.dismiss(False)


class PluginInfoScreen(Screen[None]):
    def __init__(self, plugin_id: str) -> None:
        self.plugin_id = plugin_id
        super().__init__()

    @on(Button.Pressed, "#close")
    def on_close(self, event: Button.Pressed) -> None:
        self.app.pop_screen()

    def compose(self) -> ComposeResult:
        yield Header(icon="☰")
        yield Footer()
        plugin_info = plugin_manager.plugin_registry[self.plugin_id]
        with Vertical():
            yield Label(plugin_info.name, classes="title")
            yield Label(f'{_("Version: ")}{plugin_info.version}')
            yield Link(f'{_("Author: ")}{plugin_info.author}', url=plugin_info.website)
            yield Label(_("Introduction"))
            yield Markdown(_(plugin_info.description))
            with Horizontal():
                yield Label("", classes="fill-width")
                yield Button(_("Close"), id="close", variant="success")


class SelectImportProjectScreen(Screen[pathlib.Path]):
    def compose(self) -> ComposeResult:
        yield Header(icon="☰")
        yield Footer()
        yield RootDirectoryTree("/", id="file_selector")

    @on(DirectoryTree.FileSelected, "#file_selector")
    def on_directory_selected(self, event: DirectoryTree.FileSelected) -> None:
        self.dismiss(event.path)


class SelectOutputDirectoryScreen(Screen[pathlib.Path]):
    def compose(self) -> ComposeResult:
        yield Header(icon="☰")
        yield Footer()
        yield RootDirectoryTree("/", id="directory_selector")

    @on(DirectoryTree.DirectorySelected, "#directory_selector")
    def on_directory_selected(self, event: DirectoryTree.DirectorySelected) -> None:
        self.dismiss(event.path)


class SelectFormats(Vertical):
    @on(Button.Pressed, "#swap_input_output")
    def on_swap_input_output(self, pressed: Button.Pressed) -> None:
        input_format_select = self.query_one("#input_format")
        output_format_select = self.query_one("#output_format")
        input_format_value, output_format_value = (
            output_format_select._value,
            input_format_select._value,
        )
        input_format_select._watch_value(input_format_value)
        output_format_select._watch_value(output_format_value)
        if settings.reset_tasks_on_input_change:
            self.app.query_one("ListView#direct").clear()

    @on(Button.Pressed, "#input_plugin_info")
    def on_input_plugin_info(self, pressed: Button.Pressed) -> None:
        if settings.last_input_format is not None:
            self.app.push_screen(PluginInfoScreen(settings.last_input_format))

    @on(Button.Pressed, "#output_plugin_info")
    def on_output_plugin_info(self, pressed: Button.Pressed) -> None:
        if settings.last_output_format is not None:
            self.app.push_screen(PluginInfoScreen(settings.last_output_format))

    @on(Select.Changed, "#input_format")
    def on_input_format_changed(self, event: Select.Changed) -> None:
        last_input_format = event.value if event.value != Select.BLANK else None
        if settings.last_input_format != last_input_format:
            settings.last_input_format = last_input_format
            if settings.reset_tasks_on_input_change:
                self.app.query_one("ListView#direct").clear()

    @on(Select.Changed, "#output_format")
    def on_output_format_changed(self, event: Select.Changed) -> None:
        settings.last_output_format = event.value if event.value != Select.BLANK else None

    def compose(self) -> ComposeResult:
        yield Label(_("Select File Formats"), classes="title")
        with Horizontal():
            yield Label(_("Import format"), classes="text-middle")
            yield Select(
                [
                    (f"{_(plugin_info.file_format)} (*.{plugin_info.suffix})", plugin_id)
                    for plugin_id, plugin_info in plugin_manager.plugin_registry.items()
                ],
                value=(
                    settings.last_input_format
                    if settings.last_input_format is not None
                    else next(
                        iter(plugin_manager.plugin_registry),
                        Select.BLANK,
                    )
                ),
                prompt="",
                id="input_format",
                classes="fill-width",
            )
            yield Button("ℹ", id="input_plugin_info", tooltip=_("View Detail Information"))
        with Horizontal():
            yield Label(_("Swap Input and Output"), classes="text-middle")
            yield Label("", classes="fill-width")
            yield Button("⇅", id="swap_input_output")
        with Horizontal():
            yield Label(_("Export format"), classes="text-middle")
            yield Select(
                [
                    (f"{_(plugin_info.file_format)} (*.{plugin_info.suffix})", plugin_id)
                    for plugin_id, plugin_info in plugin_manager.plugin_registry.items()
                ],
                value=(
                    settings.last_output_format
                    if settings.last_output_format is not None
                    else next(
                        iter(plugin_manager.plugin_registry),
                        Select.BLANK,
                    )
                ),
                prompt="",
                id="output_format",
                classes="fill-width",
            )
            yield Button("ℹ", id="output_plugin_info", tooltip=_("View Detail Information"))


class TaskRow(Right):
    def __init__(
        self,
        input_path: pathlib.Path,
        stem: str,
        ext: str,
        arrow_symbol: str = "→",
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> None:
        self.input_path = input_path
        self.stem = stem
        self.ext = ext
        self.arrow_symbol = arrow_symbol
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        yield Label(str(self.input_path), classes="text-middle half-width")
        yield Label(f"  {self.arrow_symbol}  ", classes="text-middle")
        yield Input(self.stem, id="stem", classes="fill-width")
        yield Label(self.ext, classes="text-middle")

    @on(Input.Changed, "#stem")
    def handle_stem_change(self, event: Input.Changed) -> None:
        self.stem = event.value


class TUIApp(App[None]):
    TITLE = "LibreSVIP"
    COMMANDS = App.COMMANDS | {LibreSVIPCommandProvider}
    DEFAULT_CSS = (
        App.DEFAULT_CSS
        + """
    .title {
        width: 100%;
        text-align: center;
        text-style: bold;
    }
    .card {
        border: solid #666;
    }
    .text-middle {
        padding: 1 2;
    }
    .fill-width {
        width: 1fr;
    }
    .fill-height {
        height: 1fr;
    }
    .top-pane {
        max-height: 5;
        dock: top;
    }
    .bottom-pane {
        max-height: 5;
        dock: bottom;
    }
    .task-row {
        layout: horizontal;
    }
    .half-width {
        width: 50%;
    }
    """
    )

    def on_mount(self) -> None:
        theme_select = self.query_one("#theme_select")

        def update_theme(value: bool) -> None:
            if theme_select._value != value:
                with theme_select.prevent(Select.Changed):
                    theme_select._watch_value(int(value))

        theme_select.watch(self, "dark", update_theme, init=False)
        if settings.dark_mode == DarkMode.LIGHT:
            self.dark = False

    def _on_exit_app(self) -> Coroutine[Any, Any, None]:
        save_settings()
        return super()._on_exit_app()

    def watch_dark(self, dark: bool) -> None:
        settings.dark_mode = DarkMode.DARK if dark else DarkMode.LIGHT
        return super().watch_dark(dark)

    @on(Button.Pressed, "#add_task")
    @work
    async def handle_add_task(self, event: Button.Pressed) -> None:
        selected_path = await self.push_screen_wait(
            SelectImportProjectScreen(),
        )
        ext = selected_path.suffix.removeprefix(".").lower()
        if ext in plugin_manager.plugin_registry and settings.auto_detect_input_format:
            settings.last_input_format = ext
            self.query_one("#input_format")._watch_value(ext)
        direct_view = self.query_one("ListView#direct")
        direct_view.append(
            ListItem(
                TaskRow(
                    selected_path,
                    selected_path.stem,
                    f".{settings.last_output_format}",
                    classes="task-row",
                )
            )
        )

    @on(Switch.Changed)
    def handle_switch_changed(self, changed: Switch.Changed) -> None:
        if changed.switch.id == "auto_detect_import_format":
            settings.auto_detect_input_format = changed.value
        elif changed.switch.id == "reset_tasks_on_input_change":
            settings.reset_tasks_on_input_change = changed.value
        elif changed.switch.id == "multi_threaded_conversion":
            settings.multi_threaded_conversion = changed.value
        elif changed.switch.id == "auto_set_output_extension":
            settings.auto_set_output_extension = changed.value
        elif changed.switch.id == "open_save_folder_on_completion":
            settings.open_save_folder_on_completion = changed.value

    @on(Select.Changed, "#conflict_policy")
    def handle_conflict_policy_changed(self, changed: Select.Changed) -> None:
        settings.conflict_policy = ConflictPolicy(changed.value)

    @on(Select.Changed, "#language_select")
    async def handle_language_changed(self, changed: Select.Changed) -> None:
        if settings.language.value != changed.value:
            settings.language = Language(changed.value)
            translation.singleton_translation = get_translation()
            await self.recompose()

    @on(Select.Changed, "#theme_select")
    def handle_theme_changed(self, changed: Select.Changed) -> None:
        if self.dark != changed.value:
            self.dark = bool(changed.value)

    @on(Button.Pressed, "#delete_task")
    def handle_delete_task(self, event: Button.Pressed) -> None:
        direct_view = self.query_one("ListView#direct")
        item_len = len(direct_view)
        if item_len > 0:
            direct_view.pop(min(direct_view.index or 0, item_len - 1))

    @on(Button.Pressed, "#clear_tasks")
    def handle_clear_tasks(self, event: Button.Pressed) -> None:
        self.query_one("ListView#direct").clear()

    @on(Button.Pressed, "#change_output_directory")
    @work
    async def handle_change_output_directory(self, event: Button.Pressed) -> None:
        settings.save_folder = await self.push_screen_wait(
            SelectOutputDirectoryScreen(),
        )
        self.query_one("#output_directory").update(str(settings.save_folder))

    def handle_open_output_directory(self, event: Button.Pressed) -> None:
        with contextlib.suppress(ImportError):
            import showinfm

            showinfm.show_in_file_manager(str(pathlib.Path().absolute()))

    @on(SelectionList.SelectedChanged)
    def handle_plugins_changed(self, selected: SelectionList.SelectedChanged) -> None:
        settings.disabled_plugins = list(
            set(selected.selection_list._values.keys())
            - set(selected.selection_list._selected.keys())
        )

    @on(Input.Changed, "#max_track_count")
    def handle_max_track_count_changed(self, event: Input.Changed) -> None:
        if event.validation_result.is_valid:
            settings.max_track_count = int(event.value)

    @on(Tabs.TabActivated, "#conversion_mode")
    def handle_conversion_mode_changed(self, activated: Tabs.TabActivated) -> None:
        self.query_one("#task_list").current = activated.tab.id
        max_track_count_input = self.query_one("#max_track_count")
        if activated.tab.id == "split":
            max_track_count_input.disabled = False
        else:
            max_track_count_input.disabled = True

    def compose(self) -> ComposeResult:
        yield Header(icon="☰")
        yield Footer()
        with TabbedContent():
            with TabPane(_("Converter")), Horizontal():
                with Vertical():
                    yield SelectFormats(classes="card")
                    with Vertical(classes="card"):
                        yield Label(_("Conversion mode & Task list"), classes="title")
                        yield Tabs(
                            Tab(_("Direct"), id="direct"),
                            Tab(_("Split"), id="split"),
                            Tab(_("Merge"), id="merge"),
                            id="conversion_mode",
                        )
                        with VerticalScroll(), ContentSwitcher(initial="direct", id="task_list"):
                            yield ListView(id="direct")
                            yield Placeholder(id="split")
                            yield Placeholder(id="merge")
                with Vertical(classes="card"), VerticalScroll():
                    yield Label(_("Advanced Settings"), classes="title")
                    with Collapsible(title=_("Input Options")):
                        pass
                    with Collapsible(title=_("Intermediate Processing")):
                        pass
                    with Collapsible(title=_("Output Options")):
                        pass
                with Horizontal(classes="bottom-pane card"):
                    yield Button("＋", tooltip=_("Add task"), id="add_task")
                    yield Button("▶", tooltip=_("Start conversion"), variant="primary")
                    yield Button("❌", tooltip=_("Delete selected task"), id="delete_task")
                    yield Button("🗑︎", tooltip=_("Clear tasks"), id="clear_tasks", variant="error")
                    yield Label(_("Progress"), classes="text-middle")
                    yield ProgressBar(total=100, show_eta=False, classes="text-middle fill-height")
                    yield Label(_("Max track count"), classes="text-middle")
                    yield Input(
                        value=str(settings.max_track_count),
                        id="max_track_count",
                        validators=[Integer(minimum=1)],
                        disabled=True,
                    )
            with TabPane(_("Basic Settings")), Vertical():
                with Vertical(classes="card"):
                    yield Label(_("Conversion Settings"), classes="title")
                    with Horizontal():
                        yield Label(_("Auto detect import format"), classes="text-middle")
                        yield Label("", classes="fill-width")
                        yield Switch(
                            value=settings.auto_detect_input_format, id="auto_detect_import_format"
                        )
                    with Horizontal():
                        yield Label(
                            _("Reset list when import format changed"), classes="text-middle"
                        )
                        yield Label("", classes="fill-width")
                        yield Switch(
                            value=settings.reset_tasks_on_input_change,
                            id="reset_tasks_on_input_change",
                        )
                    with Horizontal():
                        yield Label(_("Multi-Threaded Conversion"), classes="text-middle")
                        yield Label("", classes="fill-width")
                        yield Switch(
                            value=settings.multi_threaded_conversion, id="multi_threaded_conversion"
                        )
                with Vertical(classes="card"):
                    yield Label(_("Output Settings"), classes="title")
                    with Horizontal():
                        yield Label(
                            _("Set Output File Extension Automatically"), classes="text-middle"
                        )
                        yield Label("", classes="fill-width")
                        yield Switch(
                            value=settings.auto_set_output_extension, id="auto_set_output_extension"
                        )
                    with Horizontal():
                        yield Label(_("Deal With Conflicts"), classes="text-middle")
                        yield Select(
                            [
                                (_("Overwrite"), "Overwrite"),
                                (_("Skip"), "Skip"),
                                (_("Prompt"), "Prompt"),
                            ],
                            value=settings.conflict_policy.value,
                            prompt="",
                            allow_blank=False,
                            id="conflict_policy",
                        )
                    with Horizontal():
                        yield Label(_("Output Folder"), classes="text-middle")
                        yield Static(
                            str(settings.save_folder),
                            classes="text-middle fill-width",
                            disabled=True,
                            id="output_directory",
                        )
                        # yield Button("🗁", id="open_output_directory", tooltip=_("Open Output Directory"))
                        yield Button(
                            "🗀", id="change_output_directory", tooltip=_("Change Output Directory")
                        )
                    with Horizontal():
                        yield Label(_("Open Output Folder When Done"), classes="text-middle")
                        yield Label("", classes="fill-width")
                        yield Switch(
                            value=settings.open_save_folder_on_completion,
                            id="open_save_folder_on_completion",
                        )
            with TabPane(_("Other Settings")), Horizontal():
                with Vertical(classes="card"):
                    yield Label(_("Appearance"), classes="title")
                    with Horizontal():
                        yield Label(_("Switch Language"), classes="text-middle")
                        yield Select(
                            [
                                ("简体中文", "zh_CN"),
                                ("English", "en_US"),
                                # ("日本語", "ja_JP")
                            ],
                            value=settings.language.value,
                            prompt="",
                            allow_blank=False,
                            id="language_select",
                        )
                    with Horizontal():
                        yield Label(_("Switch Theme"), classes="text-middle")
                        yield Select(
                            [
                                (_("Light"), 0),
                                (_("Dark"), 1),
                            ],
                            value=int(self.dark),
                            prompt="",
                            allow_blank=False,
                            id="theme_select",
                        )
                with Vertical(classes="card"):
                    yield Label(_("Choose Plugins"), classes="title")
                    yield SelectionList(
                        *(
                            Selection(
                                f"{plugin_info.name} ({plugin_info.version})",
                                plugin_id,
                                plugin_id not in settings.disabled_plugins,
                            )
                            for plugin_id, plugin_info in plugin_manager.plugin_registry.items()
                        )
                    )
            with TabPane(_("About")), Vertical():
                yield Link(
                    "LibreSVIP 𝅘𝅥𝅮",
                    url="https://github.com/SoulMelody/LibreSVIP",
                    tooltip=_("Repo URL"),
                )
                yield Label(f'{_("Version: ")}{libresvip.__version__}')
                yield Link(
                    _("Author: SoulMelody"),
                    url="https://space.bilibili.com/175862486",
                    tooltip=_("Author's Profile"),
                )
                yield Label(_("Introduction"))
                yield Markdown(f"""
{_("LibreSVIP is an open-sourced, liberal and extensionable framework that can convert your singing synthesis projects between different file formats.")}\n
{_("All people should have the right and freedom to choose. That's why we're committed to giving you a second chance to keep your creations free from the constraints of platforms and coterie.")}""")


if __name__ == "__main__":
    app = TUIApp()
    app.run()
