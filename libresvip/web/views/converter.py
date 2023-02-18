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

from trame.widgets import html, trame, vuetify
from trame_server.core import Server

from libresvip.core.warning_types import BaseWarning
from libresvip.extension.manager import plugin_registry
from libresvip.model.base import BaseComplexModel


def get_dialog_widget(prefix: str):
    template = vuetify.Template()
    with template:
        with vuetify.VBtn(
            icon=True,
            click=f"{prefix}_format_info = true",
        ):
            vuetify.VIcon(
                "mdi-information-outline",
            )
        with vuetify.VDialog(
            v_model=(f"{prefix}_format_info", False), max_width="600px"
        ):
            with vuetify.VCard():
                with vuetify.VListItem(three_line=True):
                    with vuetify.VListItemAvatar(size="100"):
                        vuetify.VImg(
                            src=(
                                f"'data:image/png;base64,' + plugin_details[{prefix}_format].icon_base64",
                                "",
                            ),
                        )
                    with vuetify.VListItemContent():
                        vuetify.VListItemTitle(
                            v_text=f"plugin_details[{prefix}_format].name",
                        )
                        with vuetify.VListItemSubtitle():
                            vuetify.VIcon("mdi-tag", left=True)
                            html.Span(
                                color="primary",
                                v_text=f"plugin_details[{prefix}_format].version",
                            )
                            vuetify.VListItemAvatar()
                            vuetify.VIcon("mdi-account-circle", left=True)
                            html.A(
                                v_text=f"plugin_details[{prefix}_format].author",
                                href=(f"plugin_details[{prefix}_format].website", "#"),
                                target="_blank",
                            )
                        with vuetify.VListItemSubtitle():
                            vuetify.VIcon("mdi-file-outline", left=True)
                            html.Span(
                                color="primary",
                                v_text=f"plugin_details[{prefix}_format].format_desc",
                            )
                vuetify.VDivider()
                with vuetify.VCardSubtitle("{{ translations[lang]['Introduction'] }}"):
                    vuetify.VCardText(
                        v_html=f"plugin_details[{prefix}_format].description",
                    )
                with vuetify.VCardActions():
                    vuetify.VSpacer()
                    vuetify.VBtn(
                        "{{ translations[lang]['Close'] }}",
                        color="grey",
                        click=f"{prefix}_format_info = false",
                    )
    return template


def get_option_widgets(prefix: str):
    with vuetify.VRow(
        v_for=f"(field, i) in {prefix}_fields",
        key="i",
        value="field",
    ):
        vuetify.VCheckbox(
            label=("field.title", ""),
            v_model=f"{prefix}[field.name]",
            value=("field.default", False),
            v_if="field.type === 'bool'",
        )
        with vuetify.VTooltip(bottom=True):
            with vuetify.Template(v_slot_activator="{ on, attrs }"):
                vuetify.VIcon(
                    "mdi-help-circle-outline",
                    v_bind="attrs",
                    v_on="on",
                    slot="append",
                    v_if="field.type === 'bool'",
                    __properties=["slot"],
                )
            html.Span(
                "{{ field.description }}",
            )
        vuetify.VTextField(
            label=("field.title", ""),
            v_model=f"{prefix}[field.name]",
            value=("field.default", ""),
            hint=("field.description", ""),
            v_if="field.type === 'other'",
        )
        vuetify.VSelect(
            label=("field.title", ""),
            v_model=f"{prefix}[field.name]",
            value=("field.default", ""),
            items=("field.choices", []),
            hint=("field.description", ""),
            v_if="field.type === 'enum'",
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
    state.setdefault("input_format", plugin_identifiers[0])
    state.setdefault("output_format", plugin_identifiers[0])
    state.setdefault(
        "plugin_details",
        {
            identifier: {
                "name": plugin.name,
                "author": plugin.author,
                "website": plugin.website,
                "description": plugin.description.replace("\n", "<br>"),
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
            elif issubclass(option.type_, (str, int, float, BaseComplexModel)):
                if issubclass(option.type_, BaseComplexModel):
                    default_value = option.type_.default_repr()
                else:
                    default_value = option.default
                option_info[f"{prefix}_fields"].append(
                    {
                        "type": "other",
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
                input_path.write_bytes(each["content"])
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
                    convert_errors[basename] = traceback.format_exc()
                    state.error_files = state.error_files + [basename]
        state.convert_errors = convert_errors
        state.convert_results = convert_results
        state.convert_warnings = convert_warnings
        if len(state.error_files) > 0:
            ctrl.call_js("reset", 1)
        elif len(state.success_files) > 0:
            ctrl.call_js("reset", 0)
        else:
            ctrl.call_js("reset", 2)

    @ctrl.trigger("batch_export")
    def batch_export():
        buffer = io.BytesIO()
        if len(state.files_to_convert) > 1:
            with zipfile.ZipFile(buffer, "w") as zf:
                for src_name, tmp_path in state.convert_results.items():
                    src_path = pathlib.Path(src_name)
                    tmp_path = pathlib.Path(tmp_path)
                    zf.writestr(
                        src_path.stem + "." + state.output_format, tmp_path.read_bytes()
                    )
        else:
            tmp_path = list(state.convert_results.values())[0]
            tmp_path = pathlib.Path(tmp_path)
            buffer.write(tmp_path.read_bytes())
        return server.protocol.addAttachment(memoryview(buffer.getvalue()))

    client_triggers = trame.ClientTriggers(
        ref="convert_trigger",
        reset="""
            getRef('convert_button').$emit('reset');
            if ($event == 1) {
                getRef('error_msg').$emit('show');
            } else if ($event == 0) {
                getRef('success_msg').$emit('show');
            }
        """,
    )
    ctrl.call_js = client_triggers.call
    with vuetify.VStepper(v_model=("convert_step", 1), dense=True):
        with vuetify.VStepperHeader():
            vuetify.VStepperStep(
                "{{ translations[lang]['Choose file format'] }}", step=1, editable=True
            )
            vuetify.VStepperStep(
                "{{ translations[lang]['Advanced Options'] }}",
                step=2,
                editable=("files_to_convert.length > 0", False),
            )
        with vuetify.VStepperItems():
            with vuetify.VStepperContent(step=1):
                with vuetify.VCard(outlined=True):
                    with vuetify.VCol():
                        with vuetify.VRow(dense=True):
                            with vuetify.VCol(cols=11):
                                vuetify.VSelect(
                                    dense=True,
                                    label=(
                                        "translations[lang]['Import format']",
                                        "Import format",
                                    ),
                                    v_model="input_format",
                                    items=("input_formats", id2file_format),
                                )
                            with vuetify.VCol(cols=1):
                                get_dialog_widget("input")
                        with vuetify.VRow(dense=True):
                            with vuetify.VCol(cols=6):
                                vuetify.VSwitch(
                                    dense=True,
                                    label=(
                                        "translations[lang]['Auto detect import format']",
                                        "Auto detect import format",
                                    ),
                                    v_model=("auto_detect", True),
                                )
                            with vuetify.VCol(cols=5):
                                vuetify.VSwitch(
                                    dense=True,
                                    label=(
                                        "translations[lang]['Reset list when import format changed']",
                                        "Reset list when import format changed",
                                    ),
                                    v_model=("auto_reset", True),
                                )
                            with vuetify.VCol(cols=1):
                                with vuetify.VBtn(
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
                                    vuetify.VIcon("mdi-swap-vertical-circle-outline")
                        with vuetify.VRow(dense=True):
                            with vuetify.VCol(cols=11):
                                vuetify.VSelect(
                                    dense=True,
                                    label=(
                                        "translations[lang]['Export format']",
                                        "Export format",
                                    ),
                                    v_model="output_format",
                                    items=("output_formats", id2file_format),
                                )
                            with vuetify.VCol(cols=1):
                                get_dialog_widget("output")
                with vuetify.VCard(
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
                    click="getRef('file_uploader').click()",
                    dragover="""event.preventDefault()""",
                    dragenter="""this.hover_count++""",
                    dragleave="""this.hover_count--""",
                    __events=["drop", "dragover", "dragenter", "dragleave", "click"],
                ):
                    vuetify.VCardTitle("{{ translations[lang]['Import project'] }}")
                    vuetify.VDivider()
                    with vuetify.VFlex():
                        with vuetify.VCardText():
                            vuetify.VIcon("mdi-file-upload-outline")
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
                            file = event.target.files.item(i);
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
            with vuetify.VStepperContent(step=2):
                with vuetify.VCard(outlined=True, dense=True):
                    with vuetify.VExpansionPanels(hover=True, popout=True):
                        with vuetify.VExpansionPanel():
                            with vuetify.VExpansionPanelHeader():
                                html.B("{{ translations[lang]['Import Options'] }} ")
                                html.Span(
                                    "[ {{ translations[lang]['Import from'] }} {{ plugin_details[input_format].format_desc }} ]"
                                )
                            with vuetify.VExpansionPanelContent():
                                with vuetify.VForm():
                                    get_option_widgets("input_options")
                        with vuetify.VExpansionPanel():
                            with vuetify.VExpansionPanelHeader():
                                html.B("{{ translations[lang]['Export Options'] }} ")
                                html.Span(
                                    "[ {{ translations[lang]['Export to'] }} {{ plugin_details[output_format].format_desc }} ]"
                                )
                            with vuetify.VExpansionPanelContent():
                                with vuetify.VForm():
                                    get_option_widgets("output_options")
            with vuetify.VCard(dense=True, outlined=True):
                vuetify.VCardTitle("{{ translations[lang]['File operations'] }}")
                with vuetify.VListItem(
                    v_for="(item, i) in files_to_convert",
                    key="i",
                    value=["item"],
                    dense=True,
                ):
                    with vuetify.VListItemContent():
                        vuetify.VListItemTitle("{{ item.name }}")
                    with vuetify.VListItemAction():
                        with vuetify.VBtn(
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
                            vuetify.VIcon("mdi-exclamation", color="warning")
                    with vuetify.VListItemAction():
                        with vuetify.VBtn(
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
                            vuetify.VIcon("mdi-alert-circle-outline", color="error")
                    vuetify.VIcon(
                        "mdi-check-circle-outline",
                        color="success",
                        v_show="success_files.includes(item.name)",
                    )
                    with vuetify.VListItemAction():
                        with vuetify.VBtn(
                            icon=True,
                            click="files_to_convert.splice(i, 1);flushState('files_to_convert')",
                        ):
                            vuetify.VIcon("mdi-trash-can-outline")
                with vuetify.VCardActions():
                    with vuetify.VBtn(
                        "{{ translations[lang]['Back'] }}",
                        click="convert_step = 1",
                        v_if="convert_step == 2",
                    ):
                        vuetify.VIcon("mdi-restart")
                    vuetify.VSpacer()
                    with vuetify.VBtn(
                        "{{ translations[lang]['Next'] }}",
                        color="primary",
                        click="convert_step = 2",
                        v_if="convert_step == 1",
                        disabled=("files_to_convert.length == 0", True),
                    ):
                        vuetify.VIcon("mdi-arrow-right")

                    with vuetify.VBtn(
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
                        vuetify.VIcon("mdi-arrow-right-drop-circle-outline")
                    with vuetify.VBtn(
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
                        vuetify.VIcon("mdi-folder-download-outline")
    with vuetify.VOverlay(v_if="show_error_index !== null", absolute=True):
        with vuetify.VCard(dense=True, outlined=True, classes="text-center"):
            vuetify.VAlert(
                "{{ convert_errors[files_to_convert[show_error_index].name] }}",
                type="error",
            )
            with vuetify.VCardActions():
                vuetify.VSpacer()
                vuetify.VBtn(
                    "{{ translations[lang]['Close'] }}",
                    click="show_error_index = null",
                )
    with vuetify.VOverlay(v_if="show_warning_index !== null", absolute=True):
        with vuetify.VCard(dense=True, outlined=True, classes="text-center"):
            vuetify.VAlert(
                v_for="(item, i) in convert_warnings[files_to_convert[show_warning_index].name]",
                key="i",
                v_text="item",
                type="warning",
            )
            with vuetify.VCardActions():
                vuetify.VSpacer()
                vuetify.VBtn(
                    "{{ translations[lang]['Close'] }}",
                    click="show_warning_index = null",
                )
    with vuetify.VSpeedDial(
        v_model=("fab", False),
        bottom=True,
        left=True,
        open_on_hover=True,
        direction="right",
        style="bottom: 0; position: absolute; margin-left: 16px; margin-bottom: 16px;",
    ):
        with vuetify.Template(v_slot_activator=True):
            with vuetify.VBtn(
                fab=True,
                icon=True,
            ):
                vuetify.VIcon("mdi-hammer-wrench", color="primary", v_if="!fab")
                vuetify.VIcon(
                    "mdi-hammer-wrench mdi-rotate-45", color="primary", v_else=True
                )
        with vuetify.VBtn(
            icon=True,
            color="primary",
            click="files_to_convert = []",
        ):
            vuetify.VIcon("mdi-refresh")
        with vuetify.VBtn(
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
            vuetify.VIcon("mdi-filter-variant-remove")
    with vuetify.VBtn(
        icon=True,
        large=True,
        click="getRef('file_uploader').click()",
        style="bottom: 0; right: 0; position: absolute; margin-right: 20px; margin-bottom: 20px;",
    ):
        with vuetify.VBadge(
            content=("files_to_convert.length", ""),
            v_if="files_to_convert.length > 0",
        ):
            vuetify.VIcon("mdi-upload", color="primary")
        vuetify.VIcon("mdi-upload", color="primary", v_else=True)
    with vuetify.VSnackbar(
        v_model=("success_message", False),
        timeout=5000,
        bottom=True,
        ref="success_msg",
        show="success_message = true",
        __events=["show"],
    ):
        html.Span("{{ translations[lang]['Conversion Successful'] }}")
        with vuetify.Template(v_slot_action="{ attrs }"):
            with vuetify.VBtn(
                color="success",
                v_bind="attrs",
                icon=True,
                click="success_message = false",
            ):
                vuetify.VIcon("mdi-check-circle")
    with vuetify.VSnackbar(
        v_model=("error_message", False),
        timeout=5000,
        bottom=True,
        ref="error_msg",
        show="error_message = true",
        __events=["show"],
    ):
        html.Span("{{ translations[lang]['Conversion Failed'] }}")
        with vuetify.Template(v_slot_action="{ attrs }"):
            with vuetify.VBtn(
                color="error",
                v_bind="attrs",
                icon=True,
                click="error_message = false",
            ):
                vuetify.VIcon("mdi-alert-circle")
