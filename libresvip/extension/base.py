import abc

from pydantic import BaseSettings
from yapsy.IPlugin import IPlugin

from ..model.base import Project


class SVSConverterBase(IPlugin, abc.ABC):
    @abc.abstractmethod
    def load(self, path: str, options: BaseSettings) -> Project:
        pass

    @abc.abstractmethod
    def dump(self, path: str, project: Project, options: BaseSettings):
        pass


class WriteOnlyConverterBase(SVSConverterBase, abc.ABC):
    def load(self, path: str, options: BaseSettings) -> Project:
        raise NotImplementedError


class ReadOnlyConverterBase(SVSConverterBase, abc.ABC):
    def dump(self, path: str, project: Project, options: BaseSettings):
        raise NotImplementedError
