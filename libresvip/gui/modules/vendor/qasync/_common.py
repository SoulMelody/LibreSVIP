# © 2018 Gerard Marull-Paretas <gerard@teslabs.com>
# © 2014 Mark Harviston <mark.harviston@gmail.com>
# © 2014 Arve Knudsen <arve.knudsen@gmail.com>
# BSD License

"""Mostly irrelevant, but useful utilities common to UNIX and Windows."""

import selectors

from PySide6 import QtCore

_fileno = selectors._fileobj_to_fd  # type: ignore[attr-defined]


def make_signaller(*types: type) -> QtCore.QObject:
    class Signaller(QtCore.QObject):
        signal = QtCore.Signal(*types)

    return Signaller()
