import abc
import functools
import pathlib
from collections.abc import Callable
from typing import Any, Union, cast

from typing_extensions import ParamSpec

from libresvip.model.base import BaseModel, Project

LoadParams = ParamSpec("LoadParams")
DumpParams = ParamSpec("DumpParams")


class BasePlugin(abc.ABC):
    pass


class SVSConverterBase(BasePlugin, abc.ABC):
    def __init_subclass__(cls, **kwargs: dict[str, Any]) -> None:
        cls.load = cls.ensure_load_path(cls.load)
        cls.dump = cls.ensure_dump_path(cls.dump)
        super().__init_subclass__(**kwargs)

    @staticmethod
    def ensure_load_path(func: Callable[LoadParams, Project]) -> Callable[LoadParams, Project]:
        @functools.wraps(func)
        def wrapper(
            *args: LoadParams.args,
            **kwargs: LoadParams.kwargs,
        ) -> Project:
            args_list = list(args)
            self: SVSConverterBase = args_list.pop(0)
            path = cast(
                Union[str, pathlib.Path], args_list.pop(0) if len(args_list) else kwargs.pop("path")
            )
            if not isinstance(path, pathlib.Path):
                path = pathlib.Path(path)
            return func(self, path, *args_list, **kwargs)

        return wrapper

    @staticmethod
    def ensure_dump_path(func: Callable[DumpParams, None]) -> Callable[DumpParams, None]:
        @functools.wraps(func)
        def wrapper(
            *args: DumpParams.args,
            **kwargs: DumpParams.kwargs,
        ) -> None:
            args_list = list(args)
            self: SVSConverterBase = args_list.pop(0)
            path = cast(
                Union[str, pathlib.Path], args_list.pop(0) if len(args_list) else kwargs.pop("path")
            )
            if not isinstance(path, pathlib.Path):
                path = pathlib.Path(path)
            return func(self, path, *args_list, **kwargs)

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
