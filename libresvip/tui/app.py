import enum
import io
import pathlib
import traceback
from collections.abc import Coroutine
from dataclasses import dataclass
from typing import Any, cast, get_args, get_type_hints

import more_itertools
from pydantic import BaseModel
from pydantic_core import PydanticCustomError, PydanticUndefined
from pydantic_extra_types.color import Color, parse_str
from rich.syntax import Syntax
from textual import on, work
from textual.app import App, ComposeResult
from textual.command import Hit, Hits, Provider
from textual.containers import (
    Horizontal,
    Right,
    Vertical,
    VerticalGroup,
    VerticalScroll,
)
from textual.message import Message
from textual.screen import Screen
from textual.validation import Integer, Number, ValidationResult, Validator
from textual.widgets import (
    Button,
    Collapsible,
    ContentSwitcher,
    Footer,
    Header,
    Input,
    Label,
    Link,
    ListItem,
    ListView,
    Markdown,
    MaskedInput,
    ProgressBar,
    RichLog,
    Select,
    SelectionList,
    Static,
    Switch,
    Tab,
    TabbedContent,
    TabPane,
    Tabs,
)
from textual.widgets.selection_list import Selection
from textual_fspicker import FileOpen, SelectDirectory
from upath import UPath

import libresvip
from libresvip.core.config import DarkMode, Language, save_settings, settings
from libresvip.core.warning_types import CatchWarnings
from libresvip.extension.base import ReadOnlyConverterMixin, WriteOnlyConverterMixin
from libresvip.extension.manager import get_translation, middleware_manager, plugin_manager
from libresvip.model.base import BaseComplexModel, Project
from libresvip.utils import translation
from libresvip.utils.text import supported_charset_names
from libresvip.utils.translation import gettext_lazy as _

translation.singleton_translation = get_translation()
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


class PluginInfoScreen(Screen[None]):
    def __init__(self, plugin_id: str) -> None:
        self.plugin_id = plugin_id
        super().__init__()

    @on(Button.Pressed, "#close")
    def on_close(self, event: Button.Pressed) -> None:
        self.app.workers
        self.app.pop_screen()

    def compose(self) -> ComposeResult:
        yield Header(icon="☰")
        yield Footer()
        plugin = plugin_manager.plugins.get("svs", {})[self.plugin_id]
        with Vertical():
            yield Label(plugin.info.name, classes="title")
            yield Label(f"{_('Version: ')}{plugin.version}")
            yield Link(f"{_('Author: ')}{_(plugin.info.author)}", url=plugin.info.website)
            yield Label(_("Introduction"))
            yield Markdown(_(plugin.info.description))
            with Horizontal():
                yield Label("", classes="fill-width")
                yield Button(_("Close"), id="close", variant="success")


class TaskLogScreen(Screen[None]):
    def __init__(self, log_text: str) -> None:
        self.log_text = log_text
        super().__init__()

    def on_mount(self) -> None:
        log = self.query_one(RichLog)
        log.clear()
        log.write(Syntax(self.log_text, "python"))

    @on(Button.Pressed, "#close")
    def on_close(self, event: Button.Pressed) -> None:
        self.app.pop_screen()

    @on(Button.Pressed, "#copy")
    def on_copy(self, event: Button.Pressed) -> None:
        self.app.copy_to_clipboard(self.log_text)
        self.app.notify(_("Copied"))

    def compose(self) -> ComposeResult:
        yield Header(icon="☰")
        yield Footer()
        with Vertical():
            yield RichLog(wrap=True)
            with Horizontal():
                yield Label("", classes="fill-width")
                yield Button(_("Copy to clipboard"), id="copy", variant="primary")
                yield Button(_("Close"), id="close", variant="success")


class SelectFormats(Vertical):
    @dataclass
    class InputFormatChanged(Message):
        value: str | None

    @dataclass
    class OutputFormatChanged(Message):
        value: str | None

    @on(Button.Pressed, "#swap_input_output")
    def on_swap_input_output(self, pressed: Button.Pressed) -> None:
        input_format_select = self.query_one("#input_format")
        output_format_select = self.query_one("#output_format")
        if (
            input_format_select._value not in readonly_plugin_ids
            and output_format_select._value not in writeonly_plugin_ids
        ):
            input_format_value, output_format_value = (
                output_format_select._value,
                input_format_select._value,
            )
            input_format_select._watch_value(input_format_value)
            output_format_select._watch_value(output_format_value)

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
            self.post_message(self.InputFormatChanged(value=last_input_format))

    @on(Select.Changed, "#output_format")
    def on_output_format_changed(self, event: Select.Changed) -> None:
        last_output_format = event.value if event.value != Select.BLANK else None
        if settings.last_output_format != last_output_format:
            settings.last_output_format = last_output_format
            self.post_message(self.OutputFormatChanged(value=last_output_format))

    def compose(self) -> ComposeResult:
        yield Label(_("Select File Formats"), classes="title")
        with Horizontal():
            yield Label(_("Import format"), classes="text-middle")
            yield Select(
                [
                    (f"{_(plugin.info.file_format)} (*.{plugin.info.suffix})", plugin_id)
                    for plugin_id, plugin in plugin_manager.plugins.get("svs", {}).items()
                    if plugin_id not in writeonly_plugin_ids
                ],
                value=(
                    settings.last_input_format
                    if settings.last_input_format is not None
                    else next(
                        iter(plugin_manager.plugins.get("svs", {})),
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
                    (f"{_(plugin.info.file_format)} (*.{plugin.info.suffix})", plugin_id)
                    for plugin_id, plugin in plugin_manager.plugins.get("svs", {}).items()
                    if plugin_id not in readonly_plugin_ids
                ],
                value=(
                    settings.last_output_format
                    if settings.last_output_format is not None
                    else next(
                        iter(plugin_manager.plugins.get("svs", {})),
                        Select.BLANK,
                    )
                ),
                prompt="",
                id="output_format",
                classes="fill-width",
            )
            yield Button("ℹ", id="output_plugin_info", tooltip=_("View Detail Information"))


class ColorValidator(Validator):
    def validate(self, value: str) -> ValidationResult:
        try:
            parse_str(value)
            return self.success()
        except PydanticCustomError:
            return self.failure(_("Invalid color format"))


class OptionsForm(ListView):
    def __init__(self, option_class: type[BaseModel] | None, *args: Any, **kwargs: Any) -> None:
        self.option_class = option_class
        self.option_dict = {} if option_class is None else option_class().model_dump(mode="json")
        super().__init__(*args, **kwargs)

    @on(Input.Changed)
    @on(Switch.Changed)
    @on(Select.Changed)
    def handle_value_changed(self, event: Input.Changed | Switch.Changed | Select.Changed) -> None:
        option_key = event.control.id.removeprefix("value_")
        self.option_dict[option_key] = event.value

    def compose(self) -> ComposeResult:
        if self.option_class is None:
            return
        for option_key, field_info in self.option_class.model_fields.items():
            default_value = None if field_info.default is PydanticUndefined else field_info.default
            with ListItem(), Horizontal():
                if option_key == "lyric_replacement_preset_name":
                    choices = [(preset, preset) for preset in settings.lyric_replace_rules]
                    yield Label(_(field_info.title), classes="text-middle")
                    yield Select(
                        choices,
                        allow_blank=False,
                        value=default_value,
                        classes="fill-width",
                        id=f"value_{option_key}",
                    )
                elif option_key in ["encoding", "lyric_encoding"]:
                    choices = [(charset, charset) for charset in supported_charset_names()]
                    yield Label(_(field_info.title), classes="text-middle")
                    yield Select(
                        choices,
                        allow_blank=False,
                        value=default_value,
                        classes="fill-width",
                        id=f"value_{option_key}",
                    )
                elif issubclass(field_info.annotation, enum.Enum):
                    default_value = str(default_value.value) if default_value else None
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
                            choices.append((_(enum_field.title), str(enum_item.value)))
                    yield Label(_(field_info.title), classes="text-middle")
                    yield Select(
                        choices,
                        allow_blank=False,
                        value=default_value,
                        classes="fill-width",
                        id=f"value_{option_key}",
                    )
                elif issubclass(field_info.annotation, bool):
                    yield Label(_(field_info.title), classes="text-middle")
                    yield Label("", classes="fill-width")
                    yield Switch(default_value, id=f"value_{option_key}")
                elif issubclass(field_info.annotation, Color):
                    yield Label(_(field_info.title), classes="text-middle")
                    yield Label("", classes="fill-width")
                    yield MaskedInput(
                        "#NNNnnn",
                        default_value,
                        id=f"value_{option_key}",
                        validators=[ColorValidator()],
                    )
                elif issubclass(field_info.annotation, int | float | str | BaseComplexModel):
                    if issubclass(field_info.annotation, BaseComplexModel):
                        default_value = field_info.annotation.default_repr()
                    elif not isinstance(default_value, str):
                        default_value = str(default_value)
                    validators = []
                    if issubclass(field_info.annotation, int):
                        validators.append(Integer())
                    elif issubclass(field_info.annotation, float):
                        validators.append(Number())
                    yield Label(_(field_info.title), classes="text-middle")
                    yield Input(
                        default_value,
                        id=f"value_{option_key}",
                        validators=validators,
                        classes="fill-width",
                    )
                else:
                    continue
                self.option_dict[option_key] = default_value
                if field_info.description:
                    yield Button("？", tooltip=_(field_info.description), disabled=True)


class TaskRow(Right):
    def __init__(
        self,
        input_path: pathlib.Path,
        stem: str,
        ext: str,
        arrow_symbol: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.input_path = input_path
        self.stem = stem
        self.ext = ext
        self.arrow_symbol = arrow_symbol
        self.log_text = ""
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        yield Label(str(self.input_path), classes="text-middle half-width")
        yield Label(f"  {self.arrow_symbol}  ", classes="text-middle")
        if self.arrow_symbol != "⮥":
            yield Input(self.stem, id="stem", classes="fill-width")
            yield Label(self.ext, id="ext", classes="text-middle")
        else:
            yield Label("", classes="fill-width")
        yield Button("👁", id="view_log", tooltip=_("View Log"))

    @on(Input.Changed, "#stem")
    def handle_stem_change(self, event: Input.Changed) -> None:
        self.stem = event.value

    @on(Button.Pressed, "#view_log")
    def handle_view_log(self, event: Button.Pressed) -> None:
        if self.log_text:
            self.app.push_screen(TaskLogScreen(self.log_text))


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
    .row {
        max-height: 5;
    }
    .top-pane {
        dock: top;
    }
    .bottom-pane {
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

    @property
    def dark(self) -> bool:
        return self.theme != "textual-light"

    @dark.setter
    def dark(self, value: bool) -> None:
        self.theme = "textual-dark" if value else "textual-light"

    def on_mount(self) -> None:
        self.temp_path = UPath("memory:/")
        theme_select = self.query_one("#theme_select")

        def update_theme(value: bool) -> None:
            if theme_select._value != value:
                with theme_select.prevent(Select.Changed):
                    theme_select._watch_value(int(value))

        theme_select.watch(self, "dark", update_theme, init=False)
        if settings.last_input_format is not None:
            self.post_message(SelectFormats.InputFormatChanged(settings.last_input_format))
        if settings.last_output_format is not None:
            self.post_message(SelectFormats.OutputFormatChanged(settings.last_output_format))

    def _on_exit_app(self) -> Coroutine[Any, Any, None]:
        save_settings()
        return super()._on_exit_app()

    def watch_dark(self, dark: bool) -> None:
        settings.dark_mode = DarkMode.DARK if dark else DarkMode.LIGHT
        return super().watch_dark(dark)

    @on(SelectFormats.InputFormatChanged)
    async def handle_input_format_change(self, event: SelectFormats.InputFormatChanged) -> None:
        if settings.reset_tasks_on_input_change:
            tab_id = self.query_one("#task_list").current
            self.query_one(f"ListView#{tab_id}").clear()
        if event.value:
            plugin_object = plugin_manager.plugins.get("svs", {})[event.value]
            input_options = self.query_one("#input_options")
            input_options.option_class = plugin_object.input_option_cls
            input_options.option_dict = {}
            await input_options.recompose()

    @on(SelectFormats.OutputFormatChanged)
    async def handle_output_format_change(self, event: SelectFormats.OutputFormatChanged) -> None:
        if event.value:
            if settings.auto_set_output_extension:
                tab_id = self.query_one("#task_list").current
                task_list_view = self.query_one(f"ListView#{tab_id}")
                for node in task_list_view._nodes:
                    node.ext = event.value
                    node.query_one("#ext").update(f".{event.value}")
            plugin_object = plugin_manager.plugins.get("svs", {})[event.value]
            output_options = self.query_one("#output_options")
            output_options.option_class = plugin_object.output_option_cls
            output_options.option_dict = {}
            await output_options.recompose()

    @on(Button.Pressed, "#add_task")
    @work
    async def handle_add_task(self, event: Button.Pressed) -> None:
        if path_str := await self.push_screen_wait(
            FileOpen("/", title=_("Open"), open_button=_("Open"), cancel_button=_("Cancel")),
        ):
            selected_path = pathlib.Path(path_str)
        else:
            return
        ext = selected_path.suffix.removeprefix(".").lower()
        if ext in plugin_manager.plugins.get("svs", {}) and settings.auto_detect_input_format:
            settings.last_input_format = ext
            self.query_one("#input_format")._watch_value(ext)
        tab_id = self.query_one("#task_list").current
        task_list_view = self.query_one(f"ListView#{tab_id}")
        task_count = len(task_list_view)
        if tab_id == "direct" or task_count == 0:
            arrow_symbol = "→"
        elif tab_id == "split":
            return
        else:
            arrow_symbol = "⮥"
        task_list_view.append(
            ListItem(
                TaskRow(
                    selected_path,
                    selected_path.stem,
                    f".{settings.last_output_format}",
                    classes="task-row",
                    arrow_symbol=arrow_symbol,
                )
            )
        )

    @on(Switch.Changed)
    def handle_switch_changed(self, changed: Switch.Changed) -> None:
        if changed.switch.id == "auto_detect_import_format":
            settings.auto_detect_input_format = changed.value
        elif changed.switch.id == "reset_tasks_on_input_change":
            settings.reset_tasks_on_input_change = changed.value
        elif changed.switch.id == "auto_set_output_extension":
            settings.auto_set_output_extension = changed.value

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

    @work(thread=True)
    def convert_one(
        self, progress_bar: ProgressBar, task_row_item: ListItem, *sub_task_items: list[ListItem]
    ) -> None:
        tab_id = self.query_one("#task_list").current
        task_row = task_row_item.get_child_by_type(TaskRow)
        sub_tasks = [
            cast("ListItem", sub_task_item).get_child_by_type(TaskRow)
            for sub_task_item in sub_task_items
        ]
        task_row.log_text = ""
        if settings.last_input_format is None or settings.last_output_format is None:
            return
        try:
            with CatchWarnings() as w:
                output_path = self.temp_path / task_row.stem
                if tab_id != "split":
                    output_path = output_path.with_suffix(
                        f".{settings.last_output_format}",
                    )
                input_plugin = plugin_manager.plugins.get("svs", {})[settings.last_input_format]
                output_plugin = plugin_manager.plugins.get("svs", {})[settings.last_output_format]
                input_options = self.query_one("#input_options")
                input_option = input_options.option_dict
                if tab_id == "merge":
                    child_projects = [
                        input_plugin.load(
                            sub_task.input_path,
                            input_option,
                        )
                        for sub_task in more_itertools.value_chain(task_row, sub_tasks)
                    ]
                    project = Project.merge_projects(child_projects)
                else:
                    project = input_plugin.load(
                        task_row.input_path,
                        input_option,
                    )
                for (
                    middleware_id,
                    middleware,
                ) in middleware_manager.plugins.get("middleware", {}).items():
                    if self.query_one(f"#{middleware_id}_switch").value:
                        option_form = self.query_one(f"#{middleware_id}_options")
                        project = middleware.process(
                            project,
                            option_form.option_dict,
                        )
                output_options = self.query_one("#output_options")
                output_option = output_options.option_dict
                if tab_id == "split":
                    output_path.mkdir(parents=True, exist_ok=True)
                    for i, child_project in enumerate(
                        project.split_tracks(settings.max_track_count), start=1
                    ):
                        output_plugin.dump(
                            output_path / f"{task_row.stem}_{i:0=2d}.{settings.last_output_format}",
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
                task_row.log_text = w.output
            buffer = io.BytesIO()
            if output_path.is_file():
                buffer.write(output_path.read_bytes())
            else:
                zip_path = UPath("zip://", fo=buffer, mode="a")
                for child_file in output_path.iterdir():
                    if not child_file.is_file():
                        continue
                    (zip_path / child_file.name).write_bytes(
                        child_file.read_bytes(),
                    )
            self.call_from_thread(
                self.deliver_text,
                io.StringIO(buffer.getvalue().decode("latin-1")),
                encoding="latin-1",
                save_directory=settings.save_folder,
                save_filename=output_path.name if tab_id != "split" else f"{task_row.stem}.zip",
            )
        except Exception:
            task_row.log_text = traceback.format_exc()
            self.call_from_thread(
                self.notify,
                f"Error occurred while converting {task_row.input_path}",
                severity="error",
            )
        self.call_from_thread(progress_bar.advance, 1)

    @work(thread=True, exclusive=True)
    def convert_all(self, task_list_view: ListView, progress_bar: ProgressBar) -> None:
        total = len(task_list_view) if task_list_view.id != "merge" else 1
        self.call_from_thread(progress_bar.update, total=total)
        if task_list_view.id == "merge":
            (task_row,), other_tasks = more_itertools.spy(task_list_view._nodes)
            self.convert_one(
                progress_bar,
                task_row,
                *other_tasks,
            )
        else:
            for task_row in task_list_view._nodes:
                self.convert_one(
                    progress_bar,
                    task_row,
                )

    @on(Button.Pressed, "#start_conversion")
    async def handle_start_conversion(self, event: Button.Pressed) -> None:
        tab_id = self.query_one("#task_list").current
        task_list_view = self.query_one(f"ListView#{tab_id}")
        if len(task_list_view):
            progress_bar = self.query_one(ProgressBar)
            self.convert_all(task_list_view, progress_bar)

    @on(Button.Pressed, "#delete_task")
    def handle_delete_task(self, event: Button.Pressed) -> None:
        tab_id = self.query_one("#task_list").current
        task_list_view = self.query_one(f"ListView#{tab_id}")
        item_len = len(task_list_view)
        if item_len > 0:
            task_list_view.pop(min(task_list_view.index or 0, item_len - 1))

    @on(Button.Pressed, "#clear_tasks")
    def handle_clear_tasks(self, event: Button.Pressed) -> None:
        tab_id = self.query_one("#task_list").current
        self.query_one(f"ListView#{tab_id}").clear()

    @on(Button.Pressed, "#change_output_directory")
    @work
    async def handle_change_output_directory(self, event: Button.Pressed) -> None:
        if directory := await self.push_screen_wait(
            SelectDirectory(
                "/",
                title=_("Select directory"),
                select_button=_("Select"),
                cancel_button=_("Cancel"),
            )
        ):
            settings.save_folder = pathlib.Path(directory)
            self.query_one("#output_directory").update(str(directory))

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
        task_list = self.query_one("#task_list")
        task_list.current = activated.tab.id
        max_track_count_input = self.query_one("#max_track_count")
        max_track_count_input.disabled = activated.tab.id != "split"

    def compose(self) -> ComposeResult:
        if settings.dark_mode == DarkMode.LIGHT:
            self.dark = False
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
                            yield ListView(id="split")
                            yield ListView(id="merge")
                with Vertical(classes="card"), VerticalScroll():
                    yield Label(_("Advanced Settings"), classes="title")
                    with Collapsible(title=_("Input Options")):
                        yield OptionsForm(None, id="input_options")
                    for middleware_id, middleware in middleware_manager.plugins.get(
                        "middleware", {}
                    ).items():
                        with Collapsible(title=_(middleware.info.name)), VerticalGroup():
                            with Horizontal(classes="row"):
                                yield Label(_("Enable"), classes="text-middle fill-width")
                                yield Switch(id=f"{middleware_id}_switch")
                            with Vertical():
                                yield OptionsForm(
                                    middleware.process_option_cls, id=f"{middleware_id}_options"
                                )
                    with Collapsible(title=_("Output Options")):
                        yield OptionsForm(None, id="output_options")
                with Horizontal(classes="bottom-pane card row"):
                    yield Button("＋", tooltip=_("Add task"), id="add_task")
                    yield Button(
                        "▶", tooltip=_("Start conversion"), variant="primary", id="start_conversion"
                    )
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
                        yield Label(_("Output Folder"), classes="text-middle")
                        yield Static(
                            str(settings.save_folder),
                            classes="text-middle fill-width",
                            disabled=True,
                            id="output_directory",
                        )
                        yield Button(
                            "🗀", id="change_output_directory", tooltip=_("Change Output Directory")
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
                                ("Deutsch", "de_DE"),
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
                                f"{plugin.info.name} ({plugin.version})",
                                plugin_id,
                                plugin_id not in settings.disabled_plugins,
                            )
                            for plugin_id, plugin in plugin_manager.plugins.get("svs", {}).items()
                        )
                    )
            with TabPane(_("About")), Vertical():
                yield Link(
                    "LibreSVIP 𝅘𝅥𝅮",
                    url="https://github.com/SoulMelody/LibreSVIP",
                    tooltip=_("Repo URL"),
                )
                yield Label(f"{_('Version: ')}{libresvip.__version__} 🔖")
                yield Link(
                    _("Author: SoulMelody") + " 🌐",
                    url="https://space.bilibili.com/175862486",
                    tooltip=_("Author's Profile"),
                )
                yield Label(_("Introduction") + " 📖")
                yield Markdown(f"""
{_("LibreSVIP is an open-sourced, liberal and extensionable framework that can convert your singing synthesis projects between different file formats.")}\n
{_("All people should have the right and freedom to choose. That's why we're committed to giving you a second chance to keep your creations free from the constraints of platforms and coterie.")}""")
