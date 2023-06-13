import enum
import io
import os
import pathlib
import tempfile
import traceback
import warnings
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import get_args, get_type_hints

from pydantic.color import Color
from trame_client.widgets import html, trame
from trame_server.core import Server
from trame_vuetify.widgets import vuetify3

from libresvip.core.config import settings
from libresvip.core.warning_types import BaseWarning
from libresvip.extension.manager import plugin_registry
from libresvip.model.base import BaseComplexModel
from libresvip.utils import shorten_error_message


def get_dialog_widget(prefix: str):
    template = vuetify3.Template()
    with template:
        with vuetify3.VBtn(
            icon=True,
            click=f"{prefix}_format_info = true",
        ):
            vuetify3.VIcon(
                "mdi-information-outline",
            )
        with vuetify3.VDialog(
            v_model=(f"{prefix}_format_info", False), max_width="600px"
        ):
            with vuetify3.VCard():
                with vuetify3.VListItem(three_line=True):
                    with vuetify3.VListItem(size="100"):
                        vuetify3.VImg(
                            src=(
                                f"'data:image/png;base64,' + plugin_details[{prefix}_format].icon_base64",
                                "",
                            ),
                        )
                    with vuetify3.VListItem():
                        vuetify3.VListItemTitle(
                            v_text=f"plugin_details[{prefix}_format].name",
                        )
                        with vuetify3.VListItemSubtitle():
                            vuetify3.VIcon("mdi-tag", left=True)
                            html.Span(
                                color="primary",
                                v_text=f"plugin_details[{prefix}_format].version",
                            )
                            vuetify3.VListItem()
                            vuetify3.VIcon("mdi-account-circle", left=True)
                            html.A(
                                v_text=f"plugin_details[{prefix}_format].author",
                                href=(f"plugin_details[{prefix}_format].website", "#"),
                                target="_blank",
                            )
                        with vuetify3.VListItemSubtitle():
                            vuetify3.VIcon("mdi-file-outline", left=True)
                            html.Span(
                                color="primary",
                                v_text=f"translations[lang][plugin_details[{prefix}_format].format_desc]",
                            )
                vuetify3.VDivider()
                with vuetify3.VCardSubtitle("{{ translations[lang]['Introduction'] }}"):
                    vuetify3.VCardText(
                        v_html=f"translations[lang][plugin_details[{prefix}_format].description]",
                    )
                with vuetify3.VCardActions():
                    vuetify3.VSpacer()
                    vuetify3.VBtn(
                        "{{ translations[lang]['Close'] }}",
                        color="grey",
                        click=f"{prefix}_format_info = false",
                    )
    return template


def get_option_widgets(prefix: str):
    with vuetify3.VRow(
        v_for=f"(field, i) in {prefix}_fields",
        key="i",
        value="field",
    ):
        vuetify3.VCheckbox(
            label=("translations[lang][field.title]", ""),
            v_model=f"{prefix}[field.name]",
            value=("field.default", False),
            change=f"flushState('{prefix}')",
            v_if="field.type === 'bool'",
        )
        with html.Div(
            "{{ translations[lang][field.title] }}", v_else_if="field.type === 'color'"
        ):
            vuetify3.VColorPicker(
                v_model=f"{prefix}[field.name]",
                value=("field.default", ""),
                change=f"flushState('{prefix}')",
            )
        vuetify3.VSelect(
            label=("translations[lang][field.title]", ""),
            v_model=f"{prefix}[field.name]",
            value=("field.default", ""),
            change=f"flushState('{prefix}')",
            items=("field.choices", []),
            hint=("translations[lang][field.description]", ""),
            v_else_if="field.type === 'enum'",
            each_item_text="""(item) => {
                if (item.text in translations[lang])
                    return translations[lang][item.text]
                return item.text
            }""",
            __properties=[("each_item_text", ":item-title")],
        )
        vuetify3.VTextField(
            label=("translations[lang][field.title]", ""),
            v_model=f"{prefix}[field.name]",
            value=("field.default", ""),
            hint=("translations[lang][field.description]", ""),
            v_else=True,
            validate_rules=r"""[
                (v) => {
                    switch (field.type) {
                        case 'int':
                            if (!/^(\\-|\\+)?[0-9]+$/.test(v))
                                return false
                            break
                        case 'float':
                            if (!/^(\\-|\\+)?[0-9]+(\\.[0-9]+)?$/.test(v))
                                return false
                            break
                    }
                    return true
                }
            ]""",
            __properties=[("validate_rules", ":rules")],
        )
        with vuetify3.VTooltip(
            bottom=True, v_if="field.type === 'bool' || field.type === 'color'"
        ):
            with vuetify3.Template(v_slot_activator="{ on }"):
                vuetify3.VIcon(
                    "mdi-help-circle-outline",
                    v_on="on",
                    slot="append",
                    __properties=["slot"],
                )
            html.Span(
                "{{ translations[lang][field.description] }}",
            )


def initialize(server: Server):
    state, ctrl = server.state, server.controller
    id2file_format = [
        {"value": identifier, "text": f"{plugin.file_format} (*.{plugin.suffix})"}
        for identifier, plugin in plugin_registry.items()
    ]
    plugin_identifiers = list(plugin_registry.keys())

    state.setdefault("show_warning_index", None)
    state.setdefault("show_error_index", None)
    state.setdefault("files_to_convert", [])
    state.setdefault("error_files", [])
    state.setdefault("success_files", [])
    state.setdefault("warning_files", [])
    state.setdefault("convert_errors", {})
    state.setdefault("convert_results", {})
    state.setdefault("convert_warnings", {})
    state.setdefault("input_options_fields", [])
    state.setdefault("output_options_fields", [])
    state.setdefault("input_options", {})
    state.setdefault("output_options", {})
    state.setdefault("converting", False)
    state.setdefault("uploading", False)
    state.setdefault("input_format", settings.last_input_format or (
        plugin_identifiers[0] if plugin_identifiers else ""
    ))
    state.setdefault("output_format", settings.last_output_format or (
        plugin_identifiers[0] if plugin_identifiers else ""
    ))
    state.setdefault(
        "plugin_details",
        {
            identifier: {
                "name": plugin.name,
                "author": plugin.author,
                "website": plugin.website,
                "description": plugin.description,
                "version": plugin.version_string,
                "format_desc": f"{plugin.file_format} (*.{plugin.suffix})",
                "icon_base64": plugin.icon_base64,
            }
            for identifier, plugin in plugin_registry.items()
        },
    )

    def build_fields_info(
        option_class,
        prefix: str,
    ):
        setattr(state, f"{prefix}_fields", [])
        setattr(state, prefix, {})
        option_info = {
            f"{prefix}_fields": [],
            f"{prefix}_defaults": {},
        }
        for i, option in enumerate(option_class.__fields__.values()):
            option_key = option.name
            if issubclass(option.type_, bool):
                option_info[f"{prefix}_fields"].append(
                    {
                        "type": "bool",
                        "name": option_key,
                        "title": option.field_info.title,
                        "description": option.field_info.description,
                        "default": option.default,
                    }
                )
                option_info[f"{prefix}_defaults"][option_key] = option.default
            elif issubclass(option.type_, (str, int, float, Color, BaseComplexModel)):
                if issubclass(option.type_, BaseComplexModel):
                    default_value = option.type_.default_repr()
                else:
                    default_value = option.default
                option_info[f"{prefix}_fields"].append(
                    {
                        "type": "color"
                        if issubclass(option.type_, Color)
                        else option.type_.__name__,
                        "name": option_key,
                        "title": option.field_info.title,
                        "description": option.field_info.description,
                        "default": default_value,
                    }
                )
                option_info[f"{prefix}_defaults"][option_key] = default_value
            elif issubclass(option.type_, enum.Enum):
                annotations = get_type_hints(option.type_, include_extras=True)
                choices = []
                for enum_item in option.type_:
                    if enum_item.name in annotations:
                        annotated_args = list(get_args(annotations[enum_item.name]))
                        if len(annotated_args) >= 2:
                            enum_type, enum_field = annotated_args[:2]
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
                option_info[f"{prefix}_fields"].append(
                    {
                        "type": "enum",
                        "name": option_key,
                        "title": option.field_info.title,
                        "description": option.field_info.description,
                        "default": option.default.value,
                        "choices": choices,
                    }
                )
                option_info[f"{prefix}_defaults"][option_key] = option.default.value
            else:
                print(option.type_)
        setattr(state, f"{prefix}_fields", option_info[f"{prefix}_fields"])
        setattr(state, prefix, option_info[f"{prefix}_defaults"])

    @state.change("input_format")
    def handle_input_change(input_format, **kwargs):
        plugin_input = plugin_registry[input_format]
        if state.auto_reset:
            state.files_to_convert = []
        if hasattr(plugin_input.plugin_object, "load"):
            input_option = get_type_hints(plugin_input.plugin_object.load)["options"]
            build_fields_info(input_option, "input_options")

    @state.change("output_format")
    def handle_output_change(output_format, **kwargs):
        plugin_output = plugin_registry[output_format]
        if hasattr(plugin_output.plugin_object, "dump"):
            output_option = get_type_hints(plugin_output.plugin_object.dump)["options"]
            build_fields_info(output_option, "output_options")

    def convert_one(input_path, output_path, input_options, output_options):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always", BaseWarning)
            input_plugin = plugin_registry[state.input_format]
            output_plugin = plugin_registry[state.output_format]
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
            return output_path, [str(each) for each in w]

    @ctrl.trigger("batch_convert")
    def batch_convert():
        state.error_files = []
        state.success_files = []
        state.convert_results = {}
        convert_results = {}
        state.convert_warnings = {}
        convert_warnings = {}
        state.convert_errors = {}
        convert_errors = {}
        tmp_dir = pathlib.Path(state.temp_dir)
        with ThreadPoolExecutor(
            max_workers=max(len(state.files_to_convert), 4)
        ) as executor:
            future_to_path = {}
            for each in state.files_to_convert:
                input_path = tmp_dir / each["name"]
                input_content = (
                    b"".join(each["content"])
                    if isinstance(each["content"], list)
                    else each["content"]
                )
                input_path.write_bytes(input_content)
                input_path = str(input_path)
                output_path = tempfile.mktemp(
                    suffix=f".{state.output_format}", dir=state.temp_dir
                )
                future_to_path[
                    executor.submit(
                        convert_one,
                        str(input_path),
                        output_path,
                        state.input_options,
                        state.output_options,
                    )
                ] = input_path
            for future in as_completed(future_to_path):
                path = future_to_path[future]
                basename = os.path.basename(path)
                try:
                    data, warning_msgs = future.result()
                    convert_results[basename] = data
                    state.success_files = state.success_files + [basename]
                    if len(warning_msgs) > 0:
                        convert_warnings[basename] = warning_msgs
                        state.warning_files = state.warning_files + [basename]
                except Exception:
                    convert_errors[basename] = shorten_error_message(traceback.format_exc())
                    state.error_files = state.error_files + [basename]
        state.convert_errors = convert_errors
        state.convert_results = convert_results
        state.convert_warnings = convert_warnings
        if len(state.error_files) > 0:
            ctrl.call_js(1)
        elif len(state.success_files) > 0:
            ctrl.call_js(0)
        else:
            ctrl.call_js(2)

    @ctrl.trigger("batch_export")
    def batch_export():
        buffer = io.BytesIO()
        if len(state.files_to_convert) > 1:
            with zipfile.ZipFile(buffer, "w") as zf:
                for src_name, tmp_path in state.convert_results.items():
                    src_path = pathlib.Path(src_name)
                    tmp_path = pathlib.Path(tmp_path)
                    zf.writestr(
                        f"{src_path.stem}.{state.output_format}", tmp_path.read_bytes()
                    )
        else:
            tmp_path = list(state.convert_results.values())[0]
            tmp_path = pathlib.Path(tmp_path)
            buffer.write(tmp_path.read_bytes())
        return server.protocol.addAttachment(memoryview(buffer.getvalue()))

    reset_trigger = trame.JSEval(
        events=("reset", 1),
        exec="""
            trame.refs['convert_button'].$emit('reset');
            if ($event == 1) {
                trame.refs['error_msg'].$emit('show');
            } else if ($event == 0) {
                trame.refs['success_msg'].$emit('show');
            }
        """,
    )
    ctrl.call_js = reset_trigger.exec
    with vuetify3.VCard(dense=True):
        with vuetify3.VTabs(v_model=("convert_step", 1)):
            vuetify3.VTab(
                "{{ translations[lang]['Choose file format'] }}", value=1
            )
            vuetify3.VTab(
                "{{ translations[lang]['Advanced Options'] }}",
                value=2,
                # disabled=("files_to_convert.length > 0", True),
            )
        with vuetify3.VWindow(v_model="convert_step"):
            with vuetify3.VWindowItem(value=1):
                with vuetify3.VCard(outlined=True):
                    with vuetify3.VCol():
                        with vuetify3.VRow(dense=True):
                            with vuetify3.VCol(cols=11):
                                vuetify3.VSelect(
                                    dense=True,
                                    label=(
                                        "translations[lang]['Import format']",
                                        "Import format",
                                    ),
                                    v_model="input_format",
                                    items=("input_formats", id2file_format),
                                    each_item_text="(item) => translations[lang][item.text]",
                                    __properties=[("each_item_text", ":item-title")],
                                )
                            with vuetify3.VCol(cols=1):
                                get_dialog_widget("input")
                        with vuetify3.VRow(dense=True):
                            with vuetify3.VCol(cols=6):
                                vuetify3.VSwitch(
                                    dense=True,
                                    label=(
                                        "translations[lang]['Auto detect import format']",
                                        "Auto detect import format",
                                    ),
                                    v_model=(
                                        "auto_detect",
                                        settings.auto_detect_input_format,
                                    ),
                                )
                            with vuetify3.VCol(cols=5):
                                vuetify3.VSwitch(
                                    dense=True,
                                    label=(
                                        "translations[lang]['Reset list when import format changed']",
                                        "Reset list when import format changed",
                                    ),
                                    v_model=(
                                        "auto_reset",
                                        settings.reset_tasks_on_input_change,
                                    ),
                                )
                            with vuetify3.VCol(cols=1):
                                with vuetify3.VBtn(
                                    icon=True,
                                    disabled=("input_format === output_format", True),
                                    color="primary",
                                    click="""
                                        [input_format, output_format] = [output_format, input_format];
                                        if (auto_reset) {
                                            files_to_convert = [];
                                        }
                                    """,
                                ):
                                    vuetify3.VIcon("mdi-swap-vertical-circle-outline")
                        with vuetify3.VRow(dense=True):
                            with vuetify3.VCol(cols=11):
                                vuetify3.VSelect(
                                    dense=True,
                                    label=(
                                        "translations[lang]['Export format']",
                                        "Export format",
                                    ),
                                    v_model="output_format",
                                    items=("output_formats", id2file_format),
                                    each_item_text="(item) => translations[lang][item.text]",
                                    __properties=[("each_item_text", ":item-title")],
                                )
                            with vuetify3.VCol(cols=1):
                                get_dialog_widget("output")
                with vuetify3.VCard(
                    outlined=True,
                    height="150",
                    drop="""
                        event.preventDefault();
                        this.hover_count = 0;
                        files_to_convert = [];
                        if (event.dataTransfer.files) {
                            for (i = 0; i < event.dataTransfer.files.length; i++) {
                                file = event.dataTransfer.files.item(i);
                                if (auto_detect) {
                                    _input_format = file.name.split('.').pop().toLowerCase();
                                    if (i === 0 && plugin_details[_input_format]) {
                                        input_format = _input_format;
                                        if (auto_reset) {
                                            files_to_convert = [];
                                        }
                                    }
                                }
                                if (file.name.toLowerCase().endsWith(input_format)) {
                                    files_to_convert.push(file);
                                }
                            };
                        };
                    """,
                    classes="text-center",
                    click="trame.refs['file_uploader'].click()",
                    dragover="""event.preventDefault()""",
                    dragenter="""this.hover_count++""",
                    dragleave="""this.hover_count--""",
                    __events=["drop", "dragover", "dragenter", "dragleave", "click"],
                ):
                    vuetify3.VCardTitle("{{ translations[lang]['Import project'] }}")
                    vuetify3.VDivider()
                    with vuetify3.VCardText():
                        vuetify3.VIcon("mdi-file-upload-outline")
                        html.Span(
                            "{{ translations[lang]['Drag and drop files here or click to upload'] }}"
                        )
                    html.Input(
                        v_show="false",
                        ref="file_uploader",
                        type="file",
                        accept=("'.' + input_format", "*.*"),
                        multiple=True,
                        change="""
                        for (i = 0; i < $event.target.files.length; i++) {
                            file = $event.target.files.item(i);
                            if (auto_detect) {
                                _input_format = file.name.split('.').pop().toLowerCase();
                                if (i === 0 && plugin_details[_input_format]) {
                                    input_format = _input_format;
                                    if (auto_reset) {
                                        files_to_convert = [];
                                    }
                                }
                            }
                            if (file.name.toLowerCase().endsWith(input_format)) {
                                files_to_convert.push(file);
                            }
                        };
                        flushState('files_to_convert');""",
                        __events=["change"],
                    )
            with vuetify3.VWindowItem(value=2):
                with vuetify3.VCard(outlined=True, dense=True):
                    with vuetify3.VExpansionPanels(hover=True, popout=True):
                        with vuetify3.VExpansionPanel():
                            with vuetify3.VExpansionPanelTitle():
                                html.B("{{ translations[lang]['Import Options'] }} ")
                                html.Span(
                                    "[ {{ translations[lang]['Import from'] }} {{ translations[lang][plugin_details[input_format].format_desc] }} ]"
                                )
                            with vuetify3.VExpansionPanelText():
                                with vuetify3.VForm():
                                    get_option_widgets("input_options")
                        with vuetify3.VExpansionPanel():
                            with vuetify3.VExpansionPanelTitle():
                                html.B("{{ translations[lang]['Export Options'] }} ")
                                html.Span(
                                    "[ {{ translations[lang]['Export to'] }} {{ translations[lang][plugin_details[output_format].format_desc] }} ]"
                                )
                            with vuetify3.VExpansionPanelText():
                                with vuetify3.VForm():
                                    get_option_widgets("output_options")
            with vuetify3.VCard(dense=True, outlined=True):
                with vuetify3.VCardTitle("{{ translations[lang]['File operations'] }}"):
                    with vuetify3.VCardActions():
                        with vuetify3.VBtn(
                            v_model=("fab", False),
                            open_on_hover=True,
                            direction="right",
                        ):
                            with vuetify3.Template(v_slot_activator=True):
                                with vuetify3.VBtn(
                                    fab=True,
                                    icon=True,
                                ):
                                    vuetify3.VIcon(
                                        "mdi-hammer-wrench",
                                        color="primary",
                                        v_if="!fab",
                                    )
                                    vuetify3.VIcon(
                                        "mdi-hammer-wrench mdi-rotate-45",
                                        color="primary",
                                        v_else=True,
                                    )
                            with vuetify3.VBtn(
                                icon=True,
                                color="primary",
                                click="files_to_convert = []",
                            ):
                                vuetify3.VIcon("mdi-refresh")
                            with vuetify3.VBtn(
                                icon=True,
                                color="primary",
                                click="""
                                for (let i = 0; i < files_to_convert.length; i++) {
                                    const file = files_to_convert[i];
                                    if (!file.name.toLowerCase().endsWith(input_format)) {
                                        files_to_convert.splice(i, 1);
                                        i--;
                                    }
                                }
                                flushState('files_to_convert')
                                """,
                            ):
                                vuetify3.VIcon("mdi-filter-variant-remove")
                    vuetify3.VSpacer()
                    with vuetify3.VCardActions():
                        with vuetify3.VBtn(
                            icon=True,
                            click="trame.refs['file_uploader'].click()",
                        ):
                            with vuetify3.VBadge(
                                content=("files_to_convert.length", ""),
                                v_if="files_to_convert.length > 0",
                            ):
                                vuetify3.VIcon("mdi-upload", color="primary")
                            vuetify3.VIcon("mdi-upload", color="primary", v_else=True)
                with vuetify3.VListItem(
                    v_for="(item, i) in files_to_convert",
                    key="i",
                    value=["item"],
                    dense=True,
                ):
                    with vuetify3.VListItem():
                        vuetify3.VListItemTitle("{{ item.name }}")
                    with vuetify3.VListItemAction():
                        with vuetify3.VBtn(
                            icon=True,
                            v_show="warning_files.includes(item.name)",
                            click="""
                            if (show_warning_index === null) {
                                show_warning_index = i;
                            }
                            else {
                                show_warning_index = null;
                            }
                            """,
                        ):
                            vuetify3.VIcon("mdi-exclamation", color="warning")
                    with vuetify3.VListItemAction():
                        with vuetify3.VBtn(
                            icon=True,
                            v_show="error_files.includes(item.name)",
                            click="""
                            if (show_error_index === null) {
                                show_error_index = i;
                            }
                            else {
                                show_error_index = null;
                            }
                            """,
                        ):
                            vuetify3.VIcon("mdi-alert-circle-outline", color="error")
                    vuetify3.VIcon(
                        "mdi-check-circle-outline",
                        color="success",
                        v_show="success_files.includes(item.name)",
                    )
                    with vuetify3.VListItemAction():
                        with vuetify3.VBtn(
                            icon=True,
                            click="files_to_convert.splice(i, 1);flushState('files_to_convert')",
                        ):
                            vuetify3.VIcon("mdi-trash-can-outline")
                with vuetify3.VCardActions():
                    with vuetify3.VBtn(
                        "{{ translations[lang]['Back'] }}",
                        click="convert_step = '1'",
                        v_if="convert_step == 2",
                    ):
                        vuetify3.VIcon("mdi-restart")
                    vuetify3.VSpacer()
                    with vuetify3.VBtn(
                        "{{ translations[lang]['Next'] }}",
                        color="primary",
                        click="convert_step = '2'",
                        v_if="convert_step == 1",
                        disabled=("files_to_convert.length == 0", True),
                    ):
                        vuetify3.VIcon("mdi-arrow-right")

                    with vuetify3.VBtn(
                        "{{ translations[lang]['Convert'] }}",
                        loading=("converting", False),
                        disabled=("converting", False),
                        color="primary",
                        v_if="convert_step == 2",
                        ref="convert_button",
                        click="converting = true;trigger('batch_convert')",
                        reset="converting = false",
                        __events=["reset"],
                    ):
                        vuetify3.VIcon("mdi-arrow-right-drop-circle-outline")
                    with vuetify3.VBtn(
                        "{{ translations[lang]['Export'] }}",
                        color="primary",
                        v_if="convert_step == 2",
                        click="""
                            if (files_to_convert.length > 1) {
                                utils.download('export.zip', trigger('batch_export'), 'application/zip')
                            }
                            else {
                                sep_index = files_to_convert[0].name.lastIndexOf('.');
                                if (sep_index > 0) {
                                    stem = files_to_convert[0].name.substring(0, sep_index);
                                }
                                else {
                                    stem = files_to_convert[0].name;
                                }
                                utils.download(
                                    stem + '.' + output_format,
                                    trigger('batch_export'), 'application/octet-stream'
                                )
                            }
                        """,
                    ):
                        vuetify3.VIcon("mdi-folder-download-outline")
    with vuetify3.VOverlay(v_if="show_error_index !== null", absolute=True):
        with vuetify3.VCard(dense=True, outlined=True, classes="text-center"):
            vuetify3.VAlert(
                "{{ convert_errors[files_to_convert[show_error_index].name] }}",
                type="error",
            )
            with vuetify3.VCardActions():
                vuetify3.VSpacer()
                vuetify3.VBtn(
                    "{{ translations[lang]['Close'] }}",
                    click="show_error_index = null",
                )
    with vuetify3.VOverlay(v_if="show_warning_index !== null", absolute=True):
        with vuetify3.VCard(dense=True, outlined=True, classes="text-center"):
            vuetify3.VAlert(
                v_for="(item, i) in convert_warnings[files_to_convert[show_warning_index].name]",
                key="i",
                v_text="item",
                type="warning",
            )
            with vuetify3.VCardActions():
                vuetify3.VSpacer()
                vuetify3.VBtn(
                    "{{ translations[lang]['Close'] }}",
                    click="show_warning_index = null",
                )
    with vuetify3.VSnackbar(
        v_model=("success_message", False),
        timeout=5000,
        bottom=True,
        ref="success_msg",
        show="success_message = true",
        __events=["show"],
    ):
        html.Span("{{ translations[lang]['Conversion Successful'] }}")
        with vuetify3.Template(v_slot_action="{ on }"):
            with vuetify3.VBtn(
                color="success",
                v_on="on",
                icon=True,
                click="success_message = false",
            ):
                vuetify3.VIcon("mdi-check-circle")
    with vuetify3.VSnackbar(
        v_model=("error_message", False),
        timeout=5000,
        bottom=True,
        ref="error_msg",
        show="error_message = true",
        __events=["show"],
    ):
        html.Span("{{ translations[lang]['Conversion Failed'] }}")
        with vuetify3.Template(v_slot_action="{ on }"):
            with vuetify3.VBtn(
                color="error",
                v_on="on",
                icon=True,
                click="error_message = false",
            ):
                vuetify3.VIcon("mdi-alert-circle")
