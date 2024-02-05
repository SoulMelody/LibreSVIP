import abc
import pathlib

from libresvip.model.base import BaseModel, Project


class BasePlugin(abc.ABC):
    pass


class SVSConverterBase(BasePlugin, abc.ABC):
    @abc.abstractmethod
    def load(self, path: pathlib.Path, options: BaseModel) -> Project:
        pass

    @abc.abstractmethod
    def dump(self, path: pathlib.Path, project: Project, options: BaseModel) -> None:
        pass


class WriteOnlyConverterBase(SVSConverterBase, abc.ABC):
    def load(self, path: pathlib.Path, options: BaseModel) -> Project:
        raise NotImplementedError


class ReadOnlyConverterBase(SVSConverterBase, abc.ABC):
    def dump(self, path: pathlib.Path, project: Project, options: BaseModel) -> None:
        raise NotImplementedError
