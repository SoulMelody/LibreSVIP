# Copyright 2014 - 2025 Avram Lubkin, All Rights Reserved

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
**Pluginlib Exceptions Submodule**

Provides exceptions classes
"""


class PluginlibError(Exception):
    """
    **Base exception class for Pluginlib exceptions**

    All Pluginlib exceptions are derived from this class.

    Subclass of :py:exc:`Exception`

    **Custom Instance Attributes**

        .. py:attribute:: friendly
            :annotation: = None

            :py:class:`str` -- Optional friendly output
    """

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args)
        self.friendly = kwargs.get("friendly")


class PluginImportError(PluginlibError):
    """
    **Exception class for Pluginlib import errors**

    Subclass of :py:exc:`PluginlibError`

    **Custom Instance Attributes**

        .. py:attribute:: friendly
            :annotation: = None

            :py:class:`str` -- May contain abbreviated traceback

            When an exception is raised while importing a module, an attempt is made to create a
            "friendly" version of the output with a traceback limited to the plugin itself
            or, failing that, the loader module.

    """
