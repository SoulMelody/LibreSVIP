import pathlib
from typing import Any, ClassVar, TypeAlias

from pydantic import BaseModel

from libresvip.extension.vendor import pluginlib
from libresvip.model.base import Project

from .meta_info import FormatProviderPluginInfo, MiddlewarePluginInfo

OptionsDict: TypeAlias = dict[str, Any]


@pluginlib.Parent("svs")
class SVSConverter:
    input_option_cls: ClassVar[type[BaseModel]]
    output_option_cls: ClassVar[type[BaseModel]]
    info: ClassVar[FormatProviderPluginInfo | None]

    @classmethod
    @pluginlib.abstractmethod
    def load(cls, path: pathlib.Path, options: OptionsDict) -> Project: ...  # type: ignore[empty-body]

    @classmethod
    @pluginlib.abstractmethod
    def dump(cls, path: pathlib.Path, project: Project, options: OptionsDict) -> None: ...


class WriteOnlyConverterMixin:
    input_option_cls: ClassVar[type[BaseModel]] = BaseModel

    @classmethod
    def load(cls, path: pathlib.Path, options: OptionsDict) -> Project:
        raise NotImplementedError


class ReadOnlyConverterMixin:
    output_option_cls: ClassVar[type[BaseModel]] = BaseModel

    @classmethod
    def dump(cls, path: pathlib.Path, project: Project, options: OptionsDict) -> None:
        raise NotImplementedError


@pluginlib.Parent("middleware")
class Middleware:
    process_option_cls: ClassVar[type[BaseModel]]
    info: ClassVar[MiddlewarePluginInfo | None]

    @classmethod
    @pluginlib.abstractmethod
    def process(cls, project: Project, options: OptionsDict) -> Project: ...  # type: ignore[empty-body]


__all__ = [
    "FormatProviderPluginInfo",
    "Middleware",
    "MiddlewarePluginInfo",
    "ReadOnlyConverterMixin",
    "SVSConverter",
    "WriteOnlyConverterMixin",
]
