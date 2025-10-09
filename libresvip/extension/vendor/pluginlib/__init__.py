# Copyright 2014 - 2025 Avram Lubkin, All Rights Reserved

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
**Pluginlib Package**

A framework for creating and importing plugins
"""

__version__ = "0.10.0"

__all__ = [
    "BlacklistEntry",
    "Parent",
    "Plugin",
    "PluginImportError",
    "PluginLoader",
    "PluginlibError",
    "abstractattribute",
    "abstractmethod",
]

from abc import abstractmethod

from libresvip.extension.vendor.pluginlib._loader import PluginLoader
from libresvip.extension.vendor.pluginlib._objects import BlacklistEntry
from libresvip.extension.vendor.pluginlib._parent import Parent, Plugin
from libresvip.extension.vendor.pluginlib._util import (
    abstractattribute,
)
from libresvip.extension.vendor.pluginlib.exceptions import (
    PluginImportError,
    PluginlibError,
)
