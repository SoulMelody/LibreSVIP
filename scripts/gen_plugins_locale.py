import enum
import io
import json
import pathlib
import shutil
import sys
import tempfile
import traceback
from typing import get_args, get_type_hints

from pydantic.color import Color
from translate.convert.json2po import convertjson
from translate.tools.pomerge import mergestore

from libresvip.extension.manager import plugin_locator, plugin_manager, plugin_registry
from libresvip.model.base import BaseComplexModel

if __name__ == "__main__":
    plugin_manager._component.locatePlugins()
    for info_path, _, _ in plugin_manager._component._candidates:
        info_path = pathlib.Path(info_path)
        try:
            _, _, plugin_conf = plugin_locator.getPluginNameAndModuleFromStream(
                info_path.open("r", encoding="utf-8")
            )
            plugin_suffix = plugin_conf.get("Documentation", "Suffix")
            plugin_info = plugin_registry[plugin_suffix]
            plugin_metadata = {
                "format_desc": f"{plugin_info.file_format} (*.{plugin_info.suffix})"
            }
            if plugin_info.description:
                plugin_metadata["description"] = plugin_info.description
            for method in ("load", "dump"):
                if not hasattr(plugin_info.plugin_object, method):
                    continue
                option_class = get_type_hints(
                    getattr(plugin_info.plugin_object, method)
                )["options"]
                conv_fields = []
                for option in option_class.__fields__.values():
                    option_key = option.name
                    if issubclass(option.type_, bool):
                        field_metadata = {
                            "title": option.field_info.title,
                        }
                        if option.field_info.description:
                            field_metadata[
                                "description"
                            ] = option.field_info.description
                        conv_fields.append(field_metadata)
                    elif issubclass(
                        option.type_, (str, int, float, Color, BaseComplexModel)
                    ):
                        field_metadata = {
                            "title": option.field_info.title,
                        }
                        if option.field_info.description:
                            field_metadata[
                                "description"
                            ] = option.field_info.description
                        conv_fields.append(field_metadata)
                    elif issubclass(option.type_, enum.Enum):
                        annotations = get_type_hints(option.type_, include_extras=True)
                        choices = []
                        for enum_item in option.type_:
                            if enum_item.name in annotations:
                                annotated_args = list(
                                    get_args(annotations[enum_item.name])
                                )
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
                            field_metadata[
                                "description"
                            ] = option.field_info.description
                        conv_fields.append(field_metadata)
                plugin_metadata[method] = conv_fields
            with tempfile.NamedTemporaryFile(suffix=".po") as tmp_po:
                convertjson(
                    json.dumps(
                        {plugin_suffix: plugin_metadata},
                    ),
                    tmp_po,
                    None,
                    duplicatestyle="merge",
                )

                tmp_po.seek(0)

                i18n_file = info_path.parent / f"{info_path.stem}-zh_CN.po"
                if i18n_file.exists():
                    ori_content = i18n_file.read_bytes()
                    if ori_content:
                        orig_po = io.BytesIO(ori_content)
                        mergestore(
                            orig_po,
                            i18n_file.open("wb"),
                            tmp_po,
                        )
                        continue
                shutil.copyfileobj(tmp_po, i18n_file.open("wb"))
        except Exception:
            print(traceback.format_exc(), file=sys.stderr)
