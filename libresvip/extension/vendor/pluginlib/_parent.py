# Copyright 2014 - 2025 Avram Lubkin, All Rights Reserved

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# mypy: disable-error-code="arg-type,assignment,attr-defined,union-attr,var-annotated"
"""
**Pluginlib Parent Submodule**

Provides plugin bases class and Parent decorator
"""

import sys
from collections.abc import Callable
from inspect import FullArgSpec, getfullargspec, iscoroutinefunction, isfunction

from loguru import logger

from libresvip.extension.vendor.pluginlib._objects import GroupDict, PluginDict, TypeDict
from libresvip.extension.vendor.pluginlib._util import (
    ClassProperty,
    DictWithDotNotation,
    Undefined,
    allow_bare_decorator,
)

DEFAULT = "_default"
UNDEFINED = Undefined()


class ClassInspector:
    """
    Args:
        cls(:py:class:`Plugin`): Parent class
        subclass(:py:class:`Plugin`): Subclass to evaluate

    Inspects subclass for inclusion
    After initialization, the following attributes are set:

    errorcode
        A code corresponding to the error condition

    message
        Error message

    Values for errorcode:

        * 0: No error

        Error codes between 0 and 100 are not intended for import

        * 50 Skipload flag is True

        Error codes between 99 and 200 are excluded from import

        * 156: Skipload call returned True

        Error codes 200 and above are malformed classes

        * 210: Missing abstract property
        * 211: Missing abstract static method
        * 212: Missing abstract class method
        * 213: Missing abstract method
        * 214: Missing abstract attribute
        * 215: Missing abstract coroutine
        * 216: Type annotations differ
        * 220: Argument spec does not match
    """

    def __init__(self, cls: type["Plugin"], subclass: type["Plugin"]) -> None:
        self.message = None
        self.errorcode = 0
        self.cls = cls
        self.subclass = subclass

        self._check_skipload()
        if not self.errorcode:
            self._check_methods()

    def __bool__(self) -> bool:
        return self.errorcode == 0

    def _check_skipload(self) -> None:
        """
        Determine if subclass should be skipped
        _skipload_ is either a Boolean or callable that returns a Boolean
        """

        # pylint: disable=protected-access
        if callable(self.subclass._skipload_):
            result = self.subclass._skipload_()

            if isinstance(result, tuple):
                skip, self.message = result
            else:
                skip = result

            if skip:
                self.errorcode = 156

        elif self.subclass._skipload_:
            self.errorcode = 50
            self.message = "Skipload flag is True"

    def _check_methods(self) -> None:
        """
        Validate abstract methods are defined in subclass
        """

        for name, method in self.cls.__abstractmethods__.items():
            if self.errorcode:
                break

            # Need to get attribute from dictionary for instance tests to work
            for base in self.subclass.__mro__:  # pragma: no branch
                if name in base.__dict__:
                    submethod = base.__dict__[name]
                    break

            # If we found our abstract method, we didn't find anything
            if submethod is method:
                submethod = UNDEFINED

            if isinstance(method, property):
                self._check_property(name, submethod)
            elif isinstance(method, staticmethod):
                self._check_static_method(name, method, submethod)
            elif isinstance(method, classmethod):
                self._check_class_method(name, method, submethod)
            elif isfunction(method):
                self._check_generic_method(name, method, submethod)

            # If it's not a type we're specifically checking, just check for existence
            elif submethod is UNDEFINED:
                self.errorcode = 214
                self.message = f"Does not contain required attribute ({name})"

            if not self.errorcode:
                self._check_coroutine_method(name, method, submethod)

            if not self.errorcode:
                self._check_annotations(name, method, submethod)

    def _check_property(self, name: str, submethod: property) -> None:
        """
        Args:
            name(str): Method name
            method(:py:class:`function`): Abstract method object
            submethod(:py:class:`function`): Subclass method object

        Check for class properties
        """

        if submethod is UNDEFINED or not isinstance(submethod, property):
            self.errorcode = 210
            self.message = f"Does not contain required property ({name})"

    def _check_static_method(
        self, name: str, method: Callable[..., object], submethod: Callable[..., object]
    ) -> None:
        """
        Args:
            name(str): Method name
            method(:py:class:`function`): Abstract method object
            submethod(:py:class:`function`): Subclass method object

        Check for static methods
        """

        if submethod is UNDEFINED or not isinstance(submethod, staticmethod):
            self.errorcode = 211
            self.message = f"Does not contain required static method ({name})"
        else:
            self._compare_argspec(
                name, getfullargspec(method.__func__), getfullargspec(submethod.__func__)
            )

    def _check_class_method(
        self, name: str, method: Callable[..., object], submethod: Callable[..., object]
    ) -> None:
        """
        Args:
            name(str): Method name
            method(:py:class:`function`): Abstract method object
            submethod(:py:class:`function`): Subclass method object

        Check for class methods
        """

        if submethod is UNDEFINED or not isinstance(submethod, classmethod):
            self.errorcode = 212
            self.message = f"Does not contain required class method ({name})"
        else:
            self._compare_argspec(
                name, getfullargspec(method.__func__), getfullargspec(submethod.__func__)
            )

    def _check_generic_method(
        self, name: str, method: Callable[..., object], submethod: Callable[..., object]
    ) -> None:
        """
        Args:
            name(str): Method name
            method(:py:class:`function`): Abstract method object
            submethod(:py:class:`function`): Subclass method object

        Check for generic methods
        """

        if submethod is UNDEFINED or not isfunction(submethod):
            self.errorcode = 213
            self.message = f"Does not contain required method ({name})"
        else:
            self._compare_argspec(name, getfullargspec(method), getfullargspec(submethod))

    def _check_coroutine_method(
        self, name: str, method: Callable[..., object], submethod: Callable[..., object]
    ) -> None:
        """
        Args:
            name(str): Method name
            method(:py:class:`function`): Abstract method object
            submethod(:py:class:`function`): Subclass method object

        If abstract is a coroutine method, child should be too
        """

        if iscoroutinefunction(method) and not iscoroutinefunction(submethod):
            self.errorcode = 215
            self.message = f"Does not contain required coroutine method ({name})"

    def _check_annotations(
        self, name: str, method: Callable[..., object], submethod: Callable[..., object]
    ) -> None:
        """
        Args:
            name(str): Method name
            method(:py:class:`function`): Abstract method object
            submethod(:py:class:`function`): Subclass method object

        If abstract has type annotations and the child has type annotations, they should match
        """

        meth_annotations = getattr(method, "__annotations__", {})
        if meth_annotations:
            submeth_annotations = getattr(submethod, "__annotations__", {})
            if submeth_annotations and meth_annotations != submeth_annotations:
                self.errorcode = 216
                self.message = f"Type annotations differ for ({name})"

    def _compare_argspec(self, name: str, spec_1: FullArgSpec, spec_2: FullArgSpec) -> None:
        spec_1_dict = spec_1._asdict()
        spec_2_dict = spec_2._asdict()

        matches = True

        for key, val in spec_1_dict.items():
            # Annotations are checked separately
            if key == "annotations":
                continue
            if spec_2_dict[key] != val:
                matches = False
                break

        if not matches:
            self.errorcode = 220
            self.message = f"Argument spec does not match parent for method {name}"


class PluginType(type):
    """
    Metaclass for plugins
    """

    __plugins = DictWithDotNotation([(DEFAULT, GroupDict())])

    # pylint: disable=bad-mcs-classmethod-argument
    def __new__(
        cls, name: str, bases: tuple[type, ...], namespace: dict[str, object], **kwargs: object
    ) -> type:
        # Make sure '_parent_', '_skipload_' are set explicitly or ignore
        for attr in ("_parent_", "_skipload_"):
            if attr not in namespace:
                namespace[attr] = False

        new = super().__new__(cls, name, bases, namespace, **kwargs)

        # Determine group
        group = cls.__plugins.setdefault(new._group_ or DEFAULT, GroupDict())

        if new._type_ in group:
            if new._parent_:
                msg = f"parent must be unique: {new._type_}"
                raise ValueError(msg)

            plugindict = group[new._type_].get(new.name, UNDEFINED)
            version = str(new.version or 0)

            # Check for duplicates. Warn and ignore
            if plugindict and version in plugindict:
                existing = plugindict[version]
                logger.warning(
                    f"Duplicate plugins found for {new}: {new.__module__}.{new.__name__} and "
                    f"{existing.__module__}.{existing.__name__}",
                )

            else:
                result = ClassInspector(group[new._type_]._parent, new)

                if result:
                    group[new._type_].setdefault(new.name, PluginDict())[version] = new

                else:
                    skipmsg = "Skipping %s class %s.%s: Reason: %s"
                    args = (new, new.__module__, new.__name__, result.message)

                    if result.errorcode < 100:
                        logger.debug(skipmsg, *args)
                    elif result.errorcode < 200:
                        logger.info(skipmsg, *args)
                    else:
                        logger.warning(skipmsg % args)

        elif new._parent_:
            group[new._type_] = TypeDict(new)

            new.__abstractmethods__ = {}

            # Get abstract methods by walking the MRO
            for base in reversed(new.__mro__):
                for method_name, method in base.__dict__.items():
                    if getattr(method, "__isabstractmethod__", False):
                        new.__abstractmethods__[method_name] = method

        else:
            msg = f"Unknown parent type: {new._type_}"
            raise ValueError(msg)

        return new

    @classmethod
    def _get_plugins(cls) -> dict[str, type]:
        """
        Return registered plugins
        """

        return cls.__plugins[cls._group_ or DEFAULT][cls._type_]


class Plugin:
    """
    **Mixin class for plugins.
    All parents and child plugins will inherit from this class automatically.**

    **Class Attributes**

        *The following attributes can be set as class attributes in subclasses*

        .. autoattribute:: _alias_
        .. autoattribute:: _skipload_
        .. autoattribute:: _version_

    **Class Properties**

        .. autoattribute:: name
            :annotation:

            :py:class:`str` -- :attr:`_alias_` if set or falls back to class name

        .. autoattribute:: plugin_group

        .. autoattribute:: plugin_type

        .. autoattribute:: version
            :annotation:

            :py:class:`str` -- Returns :attr:`_version_` if set,
            otherwise falls back to module ``__version__`` or :py:data:`None`

    """

    __slots__ = ()

    _alias_ = None
    """:py:class:`str` -- Friendly name to refer to plugin.
       Accessed through :attr:`~Plugin.name` property."""
    _skipload_ = False
    """:py:class:`bool` -- When True, plugin is not loaded.
       Can also be a static or class method that returns a tuple ``(bool, message)``"""
    _version_ = None
    """:py:class:`str` -- Plugin version. Should adhere to `PEP 440`_.
       Accessed through :attr:`~Plugin.version` property.

       .. _PEP 440: https://www.python.org/dev/peps/pep-0440/"""

    @ClassProperty
    def version(cls) -> str | None:  # noqa: N805  # pylint: disable=no-self-argument
        """
        :py:class:`str` -- Returns :attr:`_version_` if set,
        otherwise falls back to module `__version__` or None
        """
        return cls._version_ or getattr(sys.modules.get(cls.__module__, None), "__version__", None)

    @ClassProperty
    def name(cls) -> str:  # noqa: N805  # pylint: disable=no-self-argument
        """
        :py:class:`str` -- :attr:`_alias_` if set or falls back to class name
        """

        return cls._alias_ or cls.__name__  # pylint: disable=no-member

    @ClassProperty
    def plugin_type(cls) -> str | None:  # noqa: N805  # pylint: disable=no-self-argument
        """
        :py:class:`str` -- ``plugin_type`` of :py:class:`~pluginlib.Parent` class
        """

        return cls._type_  # pylint: disable=no-member

    @ClassProperty
    def plugin_group(cls) -> str | None:  # noqa: N805  # pylint: disable=no-self-argument
        """
        :py:class:`str` -- ``group`` of :py:class:`~pluginlib.Parent` class
        """

        return cls._group_  # pylint: disable=no-member


@allow_bare_decorator
class Parent:
    """
    Args:
        plugin_type(str): Plugin type
        group(str): Group to store plugins

    **Class Decorator for plugin parents**

    ``plugin_type`` determines under what attribute child plugins will be accessed in
    :py:attr:`PluginLoader.plugins`.
    When not specified, the class name is used.

    ``group`` specifies the parent and all child plugins are members of
    the specified plugin group. A :py:attr:`PluginLoader` instance only accesses the
    plugins group specified when it was initialized.
    When not specified, the default group is used.
    ``group`` should be specified if plugins for different projects could be accessed
    in an single program, such as in libraries and frameworks.
    """

    __slots__ = "group", "plugin_type"

    def __init__(self, plugin_type: str | None = None, group: str | None = None) -> None:
        self.plugin_type = plugin_type
        self.group = group

    def __call__(self, cls: type) -> type:
        # In case we're inheriting another parent, clean registry
        if isinstance(cls, PluginType):
            plugins = cls._get_plugins().get(cls.name, {})
            remove = [pver for pver, pcls in plugins.items() if cls is pcls]

            if plugins and len(remove) == len(plugins):
                del cls._get_plugins()[cls.name]

            else:
                for key in remove:
                    del plugins[key]

        dict_ = cls.__dict__.copy()
        dict_.pop("__dict__", None)
        dict_.pop("__weakref__", None)

        # Clean out slot members
        for member in dict_.get("__slots__", ()):
            dict_.pop(member, None)

        # Set type
        dict_["_type_"] = self.plugin_type or cls.__name__
        dict_["_group_"] = self.group

        # Mark as parents
        for attr in ("_parent_", "_skipload_"):
            dict_[attr] = True

        # Reorder bases so any overrides are hit first in the MRO
        bases = [base for base in cls.__bases__ if base not in (object, Plugin)]
        bases.append(Plugin)
        bases = tuple(bases)

        return PluginType(cls.__name__, bases, dict_)


def get_plugins() -> dict[str, dict[str, type]]:
    """
    Convenience method for accessing all imported plugins
    """

    # pylint: disable=protected-access
    return PluginType._PluginType__plugins
