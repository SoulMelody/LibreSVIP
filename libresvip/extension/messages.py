import enum
import pathlib
import sys
from importlib.resources import files
from typing import get_args, get_type_hints

from loguru import logger
from pydantic_extra_types.color import Color

from libresvip.extension.manager import plugin_manager
from libresvip.model.base import BaseComplexModel


def messages_iterator():
    for plugin_info in plugin_manager.plugin_registry.values():
        info_path : pathlib.Path = files(sys.modules[plugin_info.plugin_object.__module__])
        plugin_suffix = plugin_info.suffix
        plugin_info = plugin_manager.plugin_registry[plugin_suffix]
        plugin_metadata = {
            "name": plugin_info.name,
            "file_format": plugin_info.file_format
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
            for option_key, field_info in option_class.model_fields.items():
                if issubclass(field_info.annotation, bool):
                    field_metadata = {
                        "title": field_info.title,
                    }
                    if field_info.description:
                        field_metadata["description"] = field_info.description
                    conv_fields.append(field_metadata)
                elif issubclass(
                    field_info.annotation,
                    (str, int, float, Color, BaseComplexModel),
                ):
                    field_metadata = {
                        "title": field_info.title,
                    }
                    if field_info.description:
                        field_metadata["description"] = field_info.description
                    conv_fields.append(field_metadata)
                elif issubclass(field_info.annotation, enum.Enum):
                    annotations = get_type_hints(
                        field_info.annotation, include_extras=True
                    )
                    choices = []
                    for enum_item in field_info.annotation:
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
                            logger.warning(enum_item.name)
                    field_metadata = {
                        "title": field_info.title,
                        "choices": choices,
                    }
                    if field_info.description:
                        field_metadata["description"] = field_info.description
                    conv_fields.append(field_metadata)
            plugin_metadata[method] = conv_fields
        yield plugin_suffix, plugin_metadata, info_path
