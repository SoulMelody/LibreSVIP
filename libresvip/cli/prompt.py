import enum
from gettext import gettext as _

from pydantic_core import PydanticUndefined
from pydantic_extra_types.color import Color
from rich.prompt import Confirm, FloatPrompt, IntPrompt, Prompt

from libresvip.model.base import BaseComplexModel, BaseModel


def prompt_fields(option_class: BaseModel) -> dict:
    option_kwargs = {}
    if hasattr(option_class, "model_fields"):
        for i, (option_key, field_info) in enumerate(option_class.model_fields.items()):
            default_value = (
                None if field_info.default is PydanticUndefined else field_info.default
            )
            translated_title = f"{i + 1}. {{}}".format(_(field_info.title))
            if issubclass(field_info.annotation, enum.Enum):
                default_value = default_value.value if default_value else None
                choice = Prompt.ask(
                    translated_title,
                    choices=[x.name for x in field_info.annotation],
                    default=default_value.name if default_value else None,
                )
                option_kwargs[option_key] = field_info.annotation[choice]
            elif issubclass(field_info.annotation, bool):
                option_kwargs[option_key] = Confirm.ask(
                    translated_title, default=default_value
                )
            elif issubclass(field_info.annotation, int):
                option_kwargs[option_key] = IntPrompt.ask(
                    translated_title, default=default_value
                )
            elif issubclass(field_info.annotation, float):
                option_kwargs[option_key] = FloatPrompt.ask(
                    translated_title, default=default_value
                )
            elif issubclass(field_info.annotation, (str, Color)):
                option_kwargs[option_key] = Prompt.ask(
                    translated_title, default=default_value
                )
            elif issubclass(field_info.annotation, BaseComplexModel):
                value_str = Prompt.ask(
                    translated_title,
                    default=field_info.annotation.default_repr(),
                )
                option_kwargs[option_key] = field_info.annotation.from_str(value_str)
    return option_kwargs
