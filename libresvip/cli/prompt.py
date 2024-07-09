import enum
from typing import Any

from pydantic_core import PydanticUndefined
from pydantic_extra_types.color import Color
from rich.prompt import Confirm, FloatPrompt, IntPrompt, Prompt

from libresvip.core.config import get_ui_settings
from libresvip.model.base import BaseComplexModel, BaseModel
from libresvip.utils.text import supported_charset_names
from libresvip.utils.translation import gettext_lazy as _


def prompt_fields(option_class: BaseModel) -> dict[str, Any]:
    option_kwargs = {}
    if hasattr(option_class, "model_fields"):
        for i, (option_key, field_info) in enumerate(option_class.model_fields.items()):
            default_value = None if field_info.default is PydanticUndefined else field_info.default
            if field_info.title is None or field_info.annotation is None:
                continue
            translated_title = f"{i + 1}. {{}}".format(_(field_info.title))
            if option_key == "lyric_replacement_preset_name":
                choice = Prompt.ask(
                    translated_title,
                    choices=list(get_ui_settings().lyric_replace_rules),
                    default=default_value,
                )
                option_kwargs[option_key] = choice
            elif option_key in ["encoding", "lyric_encoding"]:
                choice = Prompt.ask(
                    translated_title,
                    choices=supported_charset_names(),
                    default=default_value,
                )
                option_kwargs[option_key] = choice
            elif issubclass(field_info.annotation, enum.Enum):
                default_value = str(default_value.value) if default_value else None
                choice = Prompt.ask(
                    translated_title,
                    choices=[str(x.value) for x in field_info.annotation],
                    default=default_value,
                )
                option_kwargs[option_key] = choice
            elif issubclass(field_info.annotation, bool):
                option_kwargs[option_key] = Confirm.ask(
                    translated_title,
                    default=default_value,
                )
            elif issubclass(field_info.annotation, int):
                option_kwargs[option_key] = IntPrompt.ask(
                    translated_title,
                    default=default_value,
                )
            elif issubclass(field_info.annotation, float):
                option_kwargs[option_key] = FloatPrompt.ask(
                    translated_title,
                    default=default_value,
                )
            elif issubclass(field_info.annotation, (str, Color)):
                option_kwargs[option_key] = Prompt.ask(
                    translated_title,
                    default=default_value,
                )
            elif issubclass(field_info.annotation, BaseComplexModel):
                value_str = Prompt.ask(
                    translated_title,
                    default=field_info.annotation.default_repr(),
                )
                option_kwargs[option_key] = field_info.annotation.from_str(value_str)
    return option_kwargs
