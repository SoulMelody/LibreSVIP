import inspect
from typing import Any

from pydantic.alias_generators import to_camel, to_snake
from PySide6.QtCore import QObject


class CamelCaseMixin:
    def __getattribute__(self, name: str) -> Any:
        try:
            return super().__getattribute__(name)
        except AttributeError:
            camel_name = to_camel(name)
            return super().__getattribute__(camel_name)


class AutoCaseObject(type(QObject)):  # type: ignore[misc]
    def __new__(cls, name: str, bases: tuple[type], attrs: dict[str, Any]) -> type[QObject]:
        for base in bases:
            methods = inspect.getmembers(base, predicate=inspect.ismethoddescriptor)
            for method_name, method in methods:
                if method_name.startswith("_"):
                    continue
                snake_name = to_snake(method_name)
                if snake_name == method_name:
                    continue
                if snake_name in attrs:
                    attrs[method_name] = attrs[snake_name]
        return super().__new__(cls, name, (CamelCaseMixin, *bases), attrs)
