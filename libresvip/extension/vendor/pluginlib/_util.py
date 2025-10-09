# Copyright 2014 - 2025 Avram Lubkin, All Rights Reserved

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# mypy: disable-error-code="arg-type,type-arg,var-annotated"

"""
**Pluginlib Utility Module**

This module contains generic functions for use in other modules
"""

import operator
from collections.abc import Callable
from functools import update_wrapper, wraps
from inspect import isclass

OPERATORS = {
    "=": operator.eq,
    "==": operator.eq,
    "!=": operator.ne,
    "<": operator.lt,
    "<=": operator.le,
    ">": operator.gt,
    ">=": operator.ge,
}

# types.NoneType isn't available until 3.10
NoneType = type(None)


class ClassProperty:
    """
    Property decorator for class methods
    """

    def __init__(self, method: Callable[[type], object]) -> None:
        self.method = method
        update_wrapper(self, method)

    def __get__(self, instance: object, cls: type) -> object:
        return self.method(cls)


class Undefined:
    """
    Class for creating unique undefined objects for value comparisons
    """

    def __init__(self, label: str = "UNDEF") -> None:
        self.label = label

    def __str__(self) -> str:
        return self.label

    def __repr__(self) -> str:
        return self.__str__()

    def __bool__(self) -> bool:
        return False


def allow_bare_decorator(cls: type) -> object:
    """
    Wrapper for a class decorator which allows for bare decorator and argument syntax
    """

    @wraps(cls)
    def wrapper(*args: object, **kwargs: object) -> object:
        """ "Wrapper for real decorator"""

        # If we weren't only passed a bare class, return class instance
        if kwargs or len(args) != 1 or not isclass(args[0]):  # pylint: disable=no-else-return
            return cls(*args, **kwargs)
        # Otherwise, pass call to instance with default values
        else:
            return cls()(args[0])

    return wrapper


class CachingDict(dict):
    """
    A subclass of :py:class:`dict` that has a private _cache attribute

    self._cache is regular dictionary which is cleared whenever the CachingDict is changed

    Nothing is actually cached. That is the responsibility of the inheriting class
    """

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self._cache = {}

    def __setitem__(self, key: object, value: object) -> None:
        try:
            super().__setitem__(key, value)
        finally:
            self._cache.clear()

    def __delitem__(self, key: object) -> None:
        try:
            super().__delitem__(key)
        finally:
            self._cache.clear()

    def clear(self) -> None:
        try:
            super().clear()
        finally:
            self._cache.clear()

    def setdefault(self, key: object, default: object | None = None) -> object:
        try:
            return self[key]
        except KeyError:
            self[key] = default
            return default

    def pop(self, *args: object) -> object:
        value = super().pop(*args)
        self._cache.clear()
        return value

    def popitem(self) -> tuple[object, object]:
        item = super().popitem()
        self._cache.clear()
        return item


class DictWithDotNotation(dict):
    """
    Dictionary addressable by dot notation
    """

    def __getattr__(self, name: str) -> object:
        try:
            return self[name]
        except KeyError:
            msg = f"'dict' object has no attribute '{name}'"
            raise AttributeError(msg) from None


class abstractattribute:  # noqa: N801  # pylint: disable=invalid-name
    """
    A class to be used to identify abstract attributes

    .. code-block:: python

        @pluginlib.Parent
        class ParentClass:
            abstract_attribute = pluginlib.abstractattribute

    """

    __isabstractmethod__ = True
