import enum

from pydantic.color import Color
from rich.prompt import Confirm, FloatPrompt, IntPrompt, Prompt

from libresvip.model.base import BaseComplexModel, BaseModel


def prompt_fields(option_class: BaseModel) -> dict:
    option_kwargs = {}
    for i, option in enumerate(option_class.__fields__.values()):
        if issubclass(option.type_, enum.Enum):
            choice = Prompt.ask(
                f"{i + 1}. {option.field_info.title}",
                choices=[x.name for x in option.type_],
                default=option.field_info.default.name,
            )
            option_kwargs[option.name] = option.type_[choice]
        elif issubclass(option.type_, bool):
            option_kwargs[option.name] = Confirm.ask(
                f"{i + 1}. {option.field_info.title}", default=option.field_info.default
            )
        elif issubclass(option.type_, int):
            option_kwargs[option.name] = IntPrompt.ask(
                f"{i + 1}. {option.field_info.title}", default=option.field_info.default
            )
        elif issubclass(option.type_, float):
            option_kwargs[option.name] = FloatPrompt.ask(
                f"{i + 1}. {option.field_info.title}", default=option.field_info.default
            )
        elif issubclass(option.type_, (str, Color)):
            option_kwargs[option.name] = Prompt.ask(
                f"{i + 1}. {option.field_info.title}", default=option.field_info.default
            )
        elif issubclass(option.type_, BaseComplexModel):
            value_str = Prompt.ask(
                f"{i + 1}. {option.field_info.title}",
                default=option.type_.default_repr(),
            )
            option_kwargs[option.name] = option.type_.from_str(value_str)
    return option_kwargs
