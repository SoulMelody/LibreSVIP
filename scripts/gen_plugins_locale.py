#!/usr/bin/env python3

import pathlib
from collections.abc import Iterator
from configparser import RawConfigParser
from typing import Any, BinaryIO, Optional, Union

from babel.messages import setuptools_frontend

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


if __name__ == "__main__":
    cmdinst = setuptools_frontend.extract_messages()
    cmdinst.initialize_options()
    cmdinst.input_paths = [
        str(path) for path in pathlib.Path("../libresvip").rglob("**/*.yapsy-plugin")
    ]
    cmdinst.output_file = "../translations/libresvip_plugins.pot"
    cmdinst.mapping_file = "babel.cfg"
    cmdinst.finalize_options()
    cmdinst.run()
