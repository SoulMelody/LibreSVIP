#!/usr/bin/env python3

import enum
import io
import json
import os
import pathlib
import shutil
import sys
import tempfile
from collections.abc import Iterator
from typing import Any, cast, get_args, get_type_hints

from babel.messages import setuptools_frontend
from loguru import logger
from pydantic_extra_types.color import Color
from translate.convert.json2po import convertjson
from translate.storage import factory
from translate.tools.pomerge import mergestore

from libresvip.core.compat import package_path
from libresvip.extension.manager import plugin_manager
from libresvip.model.base import BaseComplexModel, BaseModel


def messages_iterator() -> Iterator[tuple[str, dict[str, Any], pathlib.Path]]:
    for plugin_info in plugin_manager.plugin_registry.values():
        info_path = package_path(sys.modules[plugin_info.plugin_object.__module__])
        plugin_suffix = plugin_info.suffix
        plugin_info = plugin_manager.plugin_registry[plugin_suffix]
        plugin_metadata: dict[str, Any] = {
            "name": plugin_info.name,
            "file_format": plugin_info.file_format,
        }
        if plugin_info.description:
            plugin_metadata["description"] = plugin_info.description
        for method in ("load", "dump"):
            if not hasattr(plugin_info.plugin_object, method):
                continue
            option_class: BaseModel = get_type_hints(getattr(plugin_info.plugin_object, method))[
                "options"
            ]
            conv_fields = []
            for option_key, field_info in option_class.model_fields.items():
                if issubclass(
                    field_info.annotation,
                    (bool, str, int, float, Color, BaseComplexModel),
                ):
                    field_metadata = {
                        "title": field_info.title,
                    }
                    if field_info.description:
                        field_metadata["description"] = field_info.description
                    conv_fields.append(field_metadata)
                elif issubclass(field_info.annotation, enum.Enum):
                    annotations = get_type_hints(field_info.annotation, include_extras=True)
                    choices = []
                    for enum_item in field_info.annotation:
                        if enum_item.name in annotations:
                            annotated_args = list(get_args(annotations[enum_item.name]))
                            if len(annotated_args) >= 2:
                                _, enum_field = annotated_args[:2]
                            else:
                                continue
                            choice = {
                                "text": enum_field.title,
                            }
                            if enum_field.description:
                                choice["description"] = enum_field.description
                            choices.append(choice)
                        else:
                            logger.warning(enum_item.name)
                    field_metadata = {
                        "title": field_info.title,
                        "choices": choices,
                    }
                    if field_info.description:
                        field_metadata["description"] = field_info.description
                    conv_fields.append(field_metadata)
            plugin_metadata[method] = conv_fields
        yield plugin_suffix, plugin_metadata, cast(pathlib.Path, info_path)


if __name__ == "__main__":
    locale_name = os.environ.get("LIBRESVIP_LOCALE", "zh_CN")

    for plugin_suffix, plugin_metadata, info_path in messages_iterator():
        with tempfile.NamedTemporaryFile(suffix=".po") as tmp_po:
            with tempfile.TemporaryDirectory() as tmp_dir:
                tmp_pot_name = tempfile.mktemp(suffix=".pot", dir=tmp_dir)
                cmdinst = setuptools_frontend.extract_messages()
                cmdinst.initialize_options()
                cmdinst.input_paths = [str(info_path)]
                cmdinst.output_file = tmp_pot_name
                cmdinst.finalize_options()
                cmdinst.run()
                python_store = factory.getobject(tmp_pot_name)
                plugin_metadata["messages"] = list(python_store.getids())
            convertjson(
                json.dumps(
                    {plugin_suffix: plugin_metadata},
                ),
                tmp_po,
                None,
                duplicatestyle="merge",
            )

            tmp_po.seek(0)

            plugin_info_path = next(info_path.glob("*.yapsy-plugin"))
            i18n_file = info_path / f"{plugin_info_path.stem}-{locale_name}.po"
            if i18n_file.exists():
                if ori_content := i18n_file.read_bytes():
                    orig_po = io.BytesIO(ori_content)
                    mergestore(
                        orig_po,
                        i18n_file.open("wb"),
                        tmp_po,
                    )
                    continue
            shutil.copyfileobj(tmp_po, i18n_file.open("wb"))
