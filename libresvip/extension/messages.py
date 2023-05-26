import enum
import pathlib
import sys
import traceback
from typing import get_args, get_type_hints

from pydantic.color import Color

from libresvip.extension.manager import plugin_locator, plugin_manager, plugin_registry
from libresvip.model.base import BaseComplexModel


def messages_iterator():
    plugin_manager._component.locatePlugins()
    for info_path, _, _ in plugin_manager._component._candidates:
        info_path = pathlib.Path(info_path)
        try:
            _, _, plugin_conf = plugin_locator.getPluginNameAndModuleFromStream(
                info_path.open("r", encoding="utf-8")
            )
            plugin_suffix = plugin_conf.get("Documentation", "Suffix")
            if plugin_suffix not in plugin_registry:
                continue
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
            yield plugin_suffix, plugin_metadata, info_path
        except Exception:
            traceback.print_exc()
