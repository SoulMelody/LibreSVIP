import pathlib
import subprocess
from collections.abc import Iterator
from configparser import RawConfigParser
from typing import Any, BinaryIO, Optional, Union

from babel.messages import setuptools_frontend
from ts_model import TranslationType, Ts
from xsdata.formats.dataclass.parsers.config import ParserConfig
from xsdata_pydantic.bindings import XmlParser

from libresvip.extension.meta_info import BasePluginInfo


class DummyPluginInfo(BasePluginInfo):
    identifier = "dummy"

    def __post_init__(self, _config: RawConfigParser) -> None:
        super().__post_init__(_config)
        self.file_format = _config.get("Documentation", "Format", fallback="")


def extract_from_plugin_metadata(
    fileobj: BinaryIO,
    keywords: list[str],
    comment_tags: list[str],
    options: dict[str, Any],
) -> Iterator[tuple[int, str, Union[Optional[str], tuple[Optional[str], ...]], list[str]]]:
    try:
        plugin_info = DummyPluginInfo.load_from_string(fileobj.read().decode("utf-8"))
    except UnicodeDecodeError:
        return
    if plugin_info is not None:
        yield 1, "gettext", plugin_info.name, ""
        if plugin_info.file_format:
            yield 2, "gettext", plugin_info.file_format, ""
        if plugin_info.description:
            yield 3, "gettext", plugin_info.description, ""


def extract_plugin_metadata_msgs() -> None:
    cmdinst = setuptools_frontend.extract_messages()
    cmdinst.initialize_options()
    cmdinst.omit_header = True
    cmdinst.input_paths = [
        str(path) for path in pathlib.Path("../libresvip").rglob("**/*.yapsy-plugin")
    ]
    cmdinst.output_file = "../translations/libresvip_plugins.pot"
    cmdinst.mapping_file = "babel.cfg"
    cmdinst.finalize_options()
    cmdinst.run()


def extract_from_qt_ts(
    fileobj: BinaryIO,
    keywords: list[str],
    comment_tags: list[str],
    options: dict[str, Any],
) -> Iterator[tuple[int, str, Union[str, tuple[str, str]], str]]:
    xml_parser = XmlParser(config=ParserConfig(fail_on_unknown_properties=False))
    ts = xml_parser.from_bytes(fileobj.read(), Ts)
    for context in ts.context:
        context_name = context.name.content[0]
        for message in context.message:
            if (
                message.translation is not None
                and message.translation.type_value == TranslationType.OBSOLETE
            ):
                continue
            if message.location:
                for location in message.location:
                    yield (
                        int(location.line),
                        "pgettext",
                        (context_name, message.source.content[0]),
                        "",
                    )
            else:
                yield 0, "pgettext", (context_name, message.source.content[0]), ""
    for message in ts.message:
        if (
            message.translation is not None
            and message.translation.type_value == TranslationType.OBSOLETE
        ):
            continue
        for location in message.location:
            yield int(location.line), "gettext", message.source.content[0], ""


def extract_qt_ts_msgs() -> None:
    subprocess.call(
        [
            "pyside6-lupdate",
            "-I",
            *(str(qml_path) for qml_path in pathlib.Path("../libresvip/res/qml").rglob("**/*.qml")),
            "-no-obsolete",
            "-ts",
            "../translations/libresvip_gui.ts",
        ]
    )
    cmdinst = setuptools_frontend.extract_messages()
    cmdinst.initialize_options()
    cmdinst.omit_header = True
    cmdinst.no_location = True
    cmdinst.input_paths = [
        "../translations/libresvip_gui.ts",
        "../translations/qt_standard_buttons.ts",
    ]
    cmdinst.output_file = "../translations/libresvip_gui.pot"
    cmdinst.mapping_file = "babel.cfg"
    cmdinst.finalize_options()
    cmdinst.run()


def extract_python_msgs() -> None:
    subprocess.call(
        ["pybabel", "extract", "../libresvip/", "-o", "../translations/libresvip_python.pot"]
    )


if __name__ == "__main__":
    extract_python_msgs()
    extract_plugin_metadata_msgs()
    extract_qt_ts_msgs()