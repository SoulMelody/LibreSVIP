# The buffer protocol ABI is stable since Python 3.11
from __future__ import annotations

import ctypes
import sys

if sys.version_info < (3, 11):
    msg = "ctypes_buffer.py requires Python 3.11 or later"
    raise RuntimeError(msg)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Buffer  # type: ignore[attr-defined]
    from types import TracebackType
    from typing import ClassVar

    from typing_extensions import Self


class _PyBuffer(ctypes.Structure):
    _fields_: ClassVar[list[tuple[str, ctypes.c_void_p]]] = [
        ("buf", ctypes.c_void_p),
        ("obj", ctypes.py_object),
        ("len", ctypes.c_ssize_t),
        ("readonly", ctypes.c_int),
        ("itemsize", ctypes.c_ssize_t),
        ("ndim", ctypes.c_int),
        ("format", ctypes.c_char_p),
        ("shape", ctypes.POINTER(ctypes.c_ssize_t)),
        ("strides", ctypes.POINTER(ctypes.c_ssize_t)),
        ("suboffsets", ctypes.POINTER(ctypes.c_ssize_t)),
        ("internal", ctypes.c_void_p),
    ]


_PyObject_GetBuffer = ctypes.pythonapi.PyObject_GetBuffer
_PyObject_GetBuffer.restype = ctypes.c_int
_PyObject_GetBuffer.argtypes = [ctypes.py_object, ctypes.POINTER(_PyBuffer), ctypes.c_int]

_PyBuffer_Release = ctypes.pythonapi.PyBuffer_Release
_PyBuffer_Release.restype = None
_PyBuffer_Release.argtypes = [ctypes.POINTER(_PyBuffer)]

_PyBUF_SIMPLE = 0
_PyBUF_WRITABLE = 1


class CtypesSimpleBuffer:
    """It is recommended to use ctypes._CData.from_buffer for writable buffers"""

    __slots__ = ("_view", "obj")

    def __init__(self, obj: Buffer, writable: bool = False) -> None:
        self.obj = obj
        self._view = _PyBuffer()
        flags = _PyBUF_SIMPLE
        if writable:
            flags |= _PyBUF_WRITABLE
        _PyObject_GetBuffer(self.obj, ctypes.byref(self._view), flags)
        # throws if GetBuffer fails

    def __len__(self) -> int:
        return 0 if self._view is None else self._view.len

    def __enter__(self) -> Self:
        # throws if GetBuffer fails
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        self.close()
        return False

    def __del__(self) -> None:
        self.close()

    def close(self) -> None:
        if self._view is not None:
            _PyBuffer_Release(ctypes.byref(self._view))
            self._view = None

    @property
    def _as_parameter_(self) -> ctypes.c_void_p:
        if self._view is None:
            msg = "buffer is closed"
            raise ValueError(msg)
        return self._view.buf
