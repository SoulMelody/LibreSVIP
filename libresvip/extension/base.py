import abc
import pathlib
from typing import TypeVar

from libresvip.model.base import BaseModel, Project

BasePlugin_co = TypeVar("BasePlugin_co", bound="BasePlugin", covariant=True)


class BasePlugin(abc.ABC):
    pass


class SVSConverterBase(BasePlugin):
    @abc.abstractmethod
    def load(self, path: pathlib.Path, options: BaseModel) -> Project: ...

    @abc.abstractmethod
    def dump(self, path: pathlib.Path, project: Project, options: BaseModel) -> None: ...


class MiddlewareBase(BasePlugin):
    @abc.abstractmethod
    def process(self, project: Project, options: BaseModel) -> Project: ...


class WriteOnlyConverterBase(SVSConverterBase, abc.ABC):
    def load(self, path: pathlib.Path, options: BaseModel) -> Project:
        raise NotImplementedError


class ReadOnlyConverterBase(SVSConverterBase, abc.ABC):
    def dump(self, path: pathlib.Path, project: Project, options: BaseModel) -> None:
        raise NotImplementedError
