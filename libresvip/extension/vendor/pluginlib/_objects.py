# Copyright 2014 - 2025 Avram Lubkin, All Rights Reserved

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# mypy: disable-error-code="arg-type,assignment,operator,return-value"
"""
**Pluginlib Object Module**

This module contains pluginlib object classes
"""

from __future__ import annotations

from collections import OrderedDict
from typing import TYPE_CHECKING

from packaging.version import parse as parse_version

from libresvip.extension.vendor.pluginlib._util import OPERATORS, CachingDict, DictWithDotNotation

if TYPE_CHECKING:
    from collections.abc import Iterable

    from libresvip.extension.vendor.pluginlib._parent import Parent


class BlacklistEntry:
    """
    Args:
        plugin_type(str): Parent type
        name(str): Plugin name
        version(str): Plugin version
        operator(str): Comparison operator ('=', '==', '!=', '<', '<=', '>', '>=')

    **Container for blacklist entry**

    If ``operator`` is :py:data:`None` or not specified, it defaults to '=='.

    One of ``plugin_type``, ``name``, or ``version`` must be specified.
    If any are unspecified or :py:data:`None`, they are treated as a wildcard.

    In order to be more compatible with parsed text,
    the order of ``operator`` and ``version`` can be swapped. The following are equivalent:

    .. code-block:: python

        BlacklistEntry('parser', 'json', '1.0', '>=')

    .. code-block:: python

            BlacklistEntry('parser', 'json', '>=', '1.0')

    ``version`` is evaluated using :py:func:`packaging.version.parse`
    and should conform to `PEP 440`_

    .. _PEP 440: https://www.python.org/dev/peps/pep-0440/
    """

    __slots__ = ("name", "operator", "type", "version")

    def __init__(
        self,
        plugin_type: str | None = None,
        name: str | None = None,
        version: str | None = None,
        operator: str | None = None,
    ) -> None:
        if plugin_type is name is version is None:
            msg = "plugin_type, name, or version must be specified"
            raise AttributeError(msg)

        self.type = plugin_type
        self.name = name
        if version in OPERATORS:
            self.operator = version
            self.version = operator

            if self.version is None:
                msg = "version must be specifed when operator is specified"
                raise AttributeError(msg)

        else:
            self.version = version
            self.operator = operator

        if self.version is not None and not isinstance(self.version, str):
            msg = f"version must be a string, received {type(self.version).__name__}"
            raise TypeError(msg)

        if self.operator is None:
            self.operator = "=="
        elif self.operator not in OPERATORS:
            msg = f"Unsupported operator '{self.operator}'"
            raise AttributeError(msg)

    def __repr__(self) -> str:
        attrs = (self.type, self.name, self.operator, self.version)
        return f"{self.__class__.__name__}({', '.join([repr(attr) for attr in attrs])})"


class GroupDict(DictWithDotNotation):
    """
    Container for a plugin group
    """

    _skip_empty = False
    _key_attr = "type"
    _bl_skip_attrs = ("name", "version")
    _bl_empty = DictWithDotNotation

    def _items(
        self, type_filter: tuple[str, ...] | None = None, name: str | None = None
    ) -> Iterable[tuple[str, PluginDict]]:
        """
        Args:
            type_filter(tuple): Optional iterable of types to return (GroupDict only)
            name(str): Only return key by this name

        Alternative generator for items() method
        """

        if name:
            if type_filter and self._key_attr == "type":
                if name in type_filter and name in self:
                    yield name, self[name]
            elif name in self:
                yield name, self[name]

        elif type_filter and self._key_attr == "type":
            for key, val in self.items():
                if key in type_filter:
                    yield key, val
        else:
            yield from self.items()

    def _filter(
        self,
        blacklist: tuple[BlacklistEntry, ...] | None = None,
        newest_only: bool = False,
        type_filter: tuple[str, ...] | None = None,
        **kwargs: object,
    ) -> DictWithDotNotation:
        """
        Args:
            blacklist(tuple): Iterable of of BlacklistEntry objects
            newest_only(bool): Only the newest version of each plugin is returned
            type(str): Plugin type to retrieve
            name(str): Plugin name to retrieve
            version(str): Plugin version to retrieve

        Returns nested dictionary of plugins

        If a blacklist is supplied, plugins are evaluated against the blacklist entries
        """

        plugins = DictWithDotNotation()
        filtered_name = kwargs.get(self._key_attr, None)

        for key, val in self._items(type_filter, filtered_name):
            plugin_blacklist = None
            skip = False

            if blacklist:
                # Assume blacklist is correct format since it is checked by PluginLoade

                plugin_blacklist = []
                for entry in blacklist:
                    if getattr(entry, self._key_attr) not in (key, None):
                        continue
                    if all(getattr(entry, attr) is None for attr in self._bl_skip_attrs):
                        if not self._skip_empty:
                            plugins[key] = None if filtered_name else self._bl_empty()
                        skip = True
                        break

                    plugin_blacklist.append(entry)

            if not skip:
                # pylint: disable=protected-access
                result = val._filter(plugin_blacklist, newest_only=newest_only, **kwargs)

                if result or not self._skip_empty:
                    plugins[key] = result

        if filtered_name:
            return plugins.get(filtered_name, None)
        return plugins


class TypeDict(GroupDict):
    """
    Container for a plugin type
    """

    _skip_empty = True
    _key_attr = "name"
    _bl_skip_attrs = ("version",)
    _bl_empty = None  # Not callable, but never called since _skip_empty is True

    def __init__(self, parent: Parent, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self._parent = parent


class PluginDict(CachingDict):
    """
    Dictionary with properties for retrieving plugins
    """

    def _sorted_keys(self) -> list[str]:
        """
        Return list of keys sorted by version

        Sorting is done based on :py:func:`packaging.version.parse`
        """

        try:
            keys = self._cache["sorted_keys"]
        except KeyError:
            keys = self._cache["sorted_keys"] = sorted(self.keys(), key=parse_version)

        return keys

    def _process_blacklist(
        self, blacklist: tuple[BlacklistEntry, ...]
    ) -> dict[tuple[str, str], set[str]]:
        """
        Process blacklist into set of excluded versions
        """

        # Assume blacklist is correct format since it is checked by PluginLoader

        blacklist_cache = {}
        blacklist_cache_old = self._cache.get("blacklist", {})

        for entry in blacklist:
            blackkey = (entry.version, entry.operator)

            if blackkey in blacklist_cache:
                continue

            if blackkey in blacklist_cache_old:
                blacklist_cache[blackkey] = blacklist_cache_old[blackkey]
            elif entry.operator is not None:
                entry_cache = blacklist_cache[blackkey] = set()
                blackversion = parse_version(entry.version or "0")
                blackop = OPERATORS[entry.operator]

                for key in self:
                    if blackop(parse_version(key), blackversion):
                        entry_cache.add(key)

        self._cache["blacklist"] = blacklist_cache
        return set().union(*blacklist_cache.values())

    def _filter(
        self,
        blacklist: tuple[BlacklistEntry, ...] | None = None,
        newest_only: bool = False,
        **kwargs: object,
    ) -> dict[str, object]:
        """
        Args:
            blacklist(tuple): Iterable of of BlacklistEntry objects
            newest_only(bool): Only the newest version of each plugin is returned
            version(str): Specific version to retrieve

        Returns dictionary of plugins

        If a blacklist is supplied, plugins are evaluated against the blacklist entries
        """

        version = kwargs.get("version")
        rtn = None

        if self:  # Dict is not empty
            if blacklist:
                blacklist = self._process_blacklist(blacklist)

                if version:
                    if version not in blacklist:
                        rtn = self.get(version, None)

                elif newest_only:
                    for key in reversed(self._sorted_keys()):
                        if key not in blacklist:
                            rtn = self[key]
                            break
                    # If no keys are left, None will be returned
                else:
                    rtn = OrderedDict()
                    for key in self._sorted_keys():
                        if key not in blacklist:
                            rtn[key] = self[key]

            elif version:
                rtn = self.get(version, None)

            elif newest_only:
                rtn = self[self._sorted_keys()[-1]]

            else:
                rtn = OrderedDict((key, self[key]) for key in self._sorted_keys())

        return rtn
