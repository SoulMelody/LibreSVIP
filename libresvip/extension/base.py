import abc

from pydantic import BaseSettings
from yapsy.IPlugin import IPlugin

from ..model.base import Project


class WriteOnlyConverterBase(IPlugin, abc.ABC):
    @abc.abstractmethod
    def dump(self, path: str, project: Project, options: BaseSettings):
        pass


class ReadOnlyConverterBase(IPlugin, abc.ABC):
    @abc.abstractmethod
    def load(self, path: str, options: BaseSettings) -> Project:
        pass


class SVSConverterBase(WriteOnlyConverterBase, ReadOnlyConverterBase, abc.ABC):
    pass
