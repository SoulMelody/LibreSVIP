import abc
import pathlib
from typing import Any

from pydantic import BaseModel

from libresvip.model.base import Project
from libresvip.utils import ensure_path


class BasePlugin(abc.ABC):
    pass


class SVSConverterBase(BasePlugin, abc.ABC):
    def __init_subclass__(cls, **kwargs: dict[str, Any]) -> None:
        cls.load = ensure_path(cls.load)
        cls.dump = ensure_path(cls.dump)
        super().__init_subclass__(**kwargs)

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
