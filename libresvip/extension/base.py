import abc
import functools
import pathlib
from typing import Any, Callable, Union

from pydantic import BaseModel

from libresvip.model.base import Project


class BasePlugin(abc.ABC):
    pass


class SVSConverterBase(BasePlugin, abc.ABC):
    def __init_subclass__(cls, **kwargs: dict[str, Any]) -> None:
        cls.load = cls.ensure_path(cls.load)  # type: ignore [method-assign]
        cls.dump = cls.ensure_path(cls.dump)  # type: ignore [method-assign]
        super().__init_subclass__(**kwargs)

    @classmethod
    def ensure_path(cls, func: Callable) -> Callable:  # type: ignore [type-arg]
        @functools.wraps(func)
        def wrapper(
            self: SVSConverterBase,
            path: Union[str, pathlib.Path],
            *args: list[Any],
            **kwargs: dict[str, Any]
        ) -> Any:
            if not isinstance(path, pathlib.Path):
                path = pathlib.Path(path)
            return func(self, path, *args, **kwargs)

        return wrapper

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
