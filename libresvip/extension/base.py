import abc
import pathlib
from typing import Any, ClassVar, TypeAlias, TypeVar, final

import pluginlib
from pydantic import BaseModel

from libresvip.model.base import Project

from .meta_info import FormatProviderPluginInfo, MiddlewarePluginInfo

BasePlugin_co = TypeVar("BasePlugin_co", bound="BasePlugin", covariant=True)
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


class BasePlugin(abc.ABC):
    pass


class SVSConverterBase(BasePlugin):
    @abc.abstractmethod
    def load(self, path: pathlib.Path, options: BaseModel) -> Project: ...

    @abc.abstractmethod
    def dump(self, path: pathlib.Path, project: Project, options: BaseModel) -> None: ...


class WriteOnlyConverterBase(SVSConverterBase, abc.ABC):
    @final
    def load(self, path: pathlib.Path, options: BaseModel) -> Project:
        raise NotImplementedError


class ReadOnlyConverterBase(SVSConverterBase, abc.ABC):
    @final
    def dump(self, path: pathlib.Path, project: Project, options: BaseModel) -> None:
        raise NotImplementedError


__all__ = [
    "BasePlugin",
    "FormatProviderPluginInfo",
    "Middleware",
    "MiddlewarePluginInfo",
    "ReadOnlyConverterBase",
    "ReadOnlyConverterMixin",
    "SVSConverter",
    "SVSConverterBase",
    "WriteOnlyConverterBase",
    "WriteOnlyConverterMixin",
]
