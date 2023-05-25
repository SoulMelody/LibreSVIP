import enum
import io
import json
import tempfile
from typing import get_args, get_type_hints

from pydantic.color import Color
from translate.convert.json2po import convertjson
from translate.tools.pomerge import mergestore

from libresvip.core.constants import res_dir
from libresvip.extension.manager import plugin_registry
from libresvip.model.base import BaseComplexModel

if __name__ == "__main__":
    plugin_metadatas = {}

    for plugin_info in plugin_registry.values():
        plugin_metadata = {
            "format_desc": f"{plugin_info.file_format} (*.{plugin_info.suffix})"
        }
        if plugin_info.description:
            plugin_metadata["description"] = plugin_info.description
        for method in ("load", "dump"):
            if not hasattr(plugin_info.plugin_object, method):
                continue
            option_class = get_type_hints(getattr(plugin_info.plugin_object, method))[
                "options"
            ]
            conv_fields = []
            for option in option_class.__fields__.values():
                option_key = option.name
                if issubclass(option.type_, bool):
                    field_metadata = {
                        "title": option.field_info.title,
                    }
                    if option.field_info.description:
                        field_metadata["description"] = option.field_info.description
                    conv_fields.append(field_metadata)
                elif issubclass(
                    option.type_, (str, int, float, Color, BaseComplexModel)
                ):
                    field_metadata = {
                        "title": option.field_info.title,
                    }
                    if option.field_info.description:
                        field_metadata["description"] = option.field_info.description
                    conv_fields.append(field_metadata)
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
                                    "text": enum_field.title,
                                }
                            )
                        else:
                            print(enum_item.name)
                    field_metadata = {
                        "title": option.field_info.title,
                        "choices": choices,
                    }
                    if option.field_info.description:
                        field_metadata["description"] = option.field_info.description
                    conv_fields.append(field_metadata)
            plugin_metadata[method] = conv_fields
        plugin_metadatas[plugin_info.name] = plugin_metadata

    with tempfile.NamedTemporaryFile(suffix=".po") as tmp_po:
        convertjson(
            json.dumps(
                plugin_metadatas,
            ),
            tmp_po,
            None,
            duplicatestyle="merge",
        )

        tmp_po.seek(0)

        mergestore(
            io.BytesIO((res_dir / "i18n" / "libresvip_plugins-zh_CN.po").read_bytes()),
            (res_dir / "i18n" / "libresvip_plugins-zh_CN.po").open("wb"),
            tmp_po,
        )
