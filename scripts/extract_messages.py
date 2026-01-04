import itertools
import pathlib
import subprocess
from collections.abc import Iterator
from configparser import RawConfigParser
from importlib.resources import files
from typing import Any, BinaryIO, cast

from babel.messages import setuptools_frontend
from ts_model import TranslationType, Ts
from xsdata.formats.dataclass.parsers.config import ParserConfig
from xsdata_pydantic.bindings import XmlParser

from libresvip.extension.manager import middleware_manager, plugin_manager
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
) -> Iterator[tuple[int, str, str | None | tuple[str | None, ...], str]]:
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
        yield 4, "gettext", plugin_info.author, ""


def extract_plugin_msgs() -> None:
    for plugin_id, plugin in itertools.chain(
        plugin_manager.plugins.get("svs", {}).items(),
        middleware_manager.plugins.get("middleware", {}).items(),
    ):
        plugin_dir = cast("pathlib.Path", files(plugin.__module__))
        cmdinst = setuptools_frontend.extract_messages()
        cmdinst.initialize_options()
        cmdinst.omit_header = True
        cmdinst.no_location = True
        cmdinst.input_dirs = [str(plugin_dir)]
        cmdinst.output_file = str(plugin_dir / f"{plugin_id}.po")
        cmdinst.mapping_file = "babel.cfg"
        cmdinst.finalize_options()
        cmdinst.run()


def extract_from_qt_ts(
    fileobj: BinaryIO,
    keywords: list[str],
    comment_tags: list[str],
    options: dict[str, Any],
) -> Iterator[tuple[int, str, str | tuple[str, str], str]]:
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
                yield (
                    0,
                    "pgettext",
                    (context_name, message.source.content[0]),
                    "",
                )
    for message in ts.message:
        if (
            message.translation is not None
            and message.translation.type_value == TranslationType.OBSOLETE
        ):
            continue
        for location in message.location:
            yield int(location.line), "gettext", message.source.content[0], ""


def extract_main_msgs() -> None:
    subprocess.call(
        [
            "pyside6-lupdate",
            "-I",
            *(str(qml_path) for qml_path in pathlib.Path("../libresvip/res/qml").rglob("**/*.qml")),
            "-no-obsolete",
            "-ts",
            "../libresvip/res/locales/libresvip_gui.ts",
        ]
    )
    cmdinst = setuptools_frontend.extract_messages()
    cmdinst.initialize_options()
    cmdinst.omit_header = True
    cmdinst.input_dirs = ["../libresvip/"]
    cmdinst.ignore_dirs = ["*middlewares*", "*plugins*"]
    cmdinst.output_file = "../libresvip/res/libresvip.po"
    cmdinst.mapping_file = "babel.cfg"
    cmdinst.finalize_options()
    cmdinst.run()


if __name__ == "__main__":
    extract_main_msgs()
    extract_plugin_msgs()
