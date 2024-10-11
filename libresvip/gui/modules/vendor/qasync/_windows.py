# © 2018 Gerard Marull-Paretas <gerard@teslabs.com>
# © 2014 Mark Harviston <mark.harviston@gmail.com>
# © 2014 Arve Knudsen <arve.knudsen@gmail.com>
# BSD License

# mypy: disable-error-code="attr-defined"

"""Windows specific Quamash functionality."""

from __future__ import annotations

import asyncio
import contextlib
import math
import sys
from typing import IO, TYPE_CHECKING, Any, Optional, Union

from loguru import logger
from PySide6 import QtCore

with contextlib.suppress(
    ImportError
):  # w/o guarding this import py.test can't gather doctests on platforms w/o _winapi
    import _overlapped
    import _winapi
    from asyncio import windows_events

if TYPE_CHECKING:
    import socket
    from _winapi import Overlapped
    from asyncio import windows_utils
    from collections.abc import Callable

    from _typeshed import Incomplete, ReadableBuffer, WriteableBuffer

    ProactorEvent = tuple[
        asyncio.Future[Any],
        Callable[[Incomplete, Incomplete, Overlapped], Any],
        Incomplete,
        Incomplete,
        Overlapped,
    ]

from ._common import make_signaller

UINT32_MAX = 0xFFFFFFFF


class _ProactorEventLoop(asyncio.ProactorEventLoop):  # type: ignore[name-defined]
    """Proactor based event loop."""

    def __init__(self) -> None:
        super().__init__(_IocpProactor())

        self.__event_signaller = make_signaller(list)
        self.__event_signal = self.__event_signaller.signal
        self.__event_signal.connect(self._process_events)
        self.__event_poller = _EventPoller(self.__event_signal)

    def _process_events(self, events: list[ProactorEvent]) -> None:
        """Process events from proactor."""
        for event in events:
            self._process_event(event)

    def _process_event(self, event: ProactorEvent) -> None:
        f, callback, transferred, key, ov = event
        try:
            logger.debug("Invoking event callback {}", callback)
            value = callback(transferred, key, ov)
        except OSError as e:
            logger.exception("Event callback failed", exc_info=sys.exc_info())
            if not f.done():
                f.set_exception(e)
        else:
            if not f.cancelled():
                f.set_result(value)

    def _before_run_forever(self) -> None:
        self.__event_poller.start(self._proactor)

    def _after_run_forever(self) -> None:
        self.__event_poller.stop()


class _IocpProactor(windows_events.IocpProactor):  # type: ignore[name-defined]
    def __init__(self) -> None:
        self.__events: list[ProactorEvent] = []
        super().__init__()
        self._lock = QtCore.QMutex()

    def select(self, timeout: Optional[float] = None) -> list[ProactorEvent]:  # type: ignore[override]
        """Override in order to handle events in a threadsafe manner."""
        if not self.__events:
            self._poll(timeout)
        tmp = self.__events
        self.__events = []
        return tmp

    def close(self) -> None:
        logger.debug("Closing")
        super().close()

    # Wrap all I/O submission methods to acquire the internal lock first; listed
    # in the order they appear in the base class source code.

    def recv(self, conn: socket.socket, nbytes: int, flags: int = 0) -> asyncio.Future[bytes]:
        with QtCore.QMutexLocker(self._lock):
            return super().recv(conn, nbytes, flags)

    def recv_into(
        self, conn: socket.socket, buf: WriteableBuffer, flags: int = 0
    ) -> asyncio.Future[Any]:
        with QtCore.QMutexLocker(self._lock):
            return super().recv_into(conn, buf, flags)

    def recvfrom(
        self, conn: socket.socket, nbytes: int, flags: int = 0
    ) -> asyncio.Future[tuple[bytes, socket._RetAddress]]:
        with QtCore.QMutexLocker(self._lock):
            return super().recvfrom(conn, nbytes, flags)

    def recvfrom_into(
        self, conn: socket.socket, buf: WriteableBuffer, flags: int = 0
    ) -> asyncio.Future[tuple[int, socket._RetAddress]]:
        if sys.version_info >= (3, 11):
            with QtCore.QMutexLocker(self._lock):
                return super().recvfrom_into(conn, buf, flags)

    def sendto(
        self,
        conn: socket.socket,
        buf: ReadableBuffer,
        flags: int = 0,
        addr: Optional[socket._RetAddress] = None,
    ) -> asyncio.Future[int]:
        with QtCore.QMutexLocker(self._lock):
            return super().sendto(conn, buf, flags, addr)

    def send(
        self, conn: socket.socket, buf: WriteableBuffer, flags: int = 0
    ) -> asyncio.Future[Any]:
        with QtCore.QMutexLocker(self._lock):
            return super().send(conn, buf, flags)

    def accept(self, listener: socket.socket) -> asyncio.Future[Any]:
        with QtCore.QMutexLocker(self._lock):
            return super().accept(listener)

    def connect(
        self,
        conn: socket.socket,
        address: Union[
            tuple[Incomplete, Incomplete],
            tuple[Incomplete, Incomplete, Incomplete, Incomplete],
        ],
    ) -> asyncio.Future[Any]:
        with QtCore.QMutexLocker(self._lock):
            return super().connect(conn, address)

    def sendfile(
        self, sock: socket.socket, file: IO[bytes], offset: int, count: int
    ) -> asyncio.Future[Any]:
        with QtCore.QMutexLocker(self._lock):
            return super().sendfile(sock, file, offset, count)

    def accept_pipe(self, pipe: socket.socket) -> asyncio.Future[Any]:
        with QtCore.QMutexLocker(self._lock):
            return super().accept_pipe(pipe)

    # connect_pipe() does not actually use the delayed completion machinery.

    def _wait_for_handle(
        self,
        handle: windows_utils.PipeHandle,  # type: ignore[name-defined]
        timeout: int,
        _is_cancel: bool,
    ) -> bool:
        with QtCore.QMutexLocker(self._lock):
            return super()._wait_for_handle(  # type: ignore[misc]
                handle, timeout, _is_cancel
            )

    def _poll(self, timeout: Optional[float] = None) -> None:
        """Override in order to handle events in a threadsafe manner."""
        if timeout is None:
            ms = UINT32_MAX  # wait for eternity
        elif timeout < 0:
            msg = "negative timeout"
            raise ValueError(msg)
        else:
            # GetQueuedCompletionStatus() has a resolution of 1 millisecond,
            # round away from zero to wait *at least* timeout seconds.
            ms = math.ceil(timeout * 1e3)
            if ms >= UINT32_MAX:
                msg = "timeout too big"
                raise ValueError(msg)

        while True:
            status = _overlapped.GetQueuedCompletionStatus(self._iocp, ms)
            if status is None:
                break
            ms = 0

            with QtCore.QMutexLocker(self._lock):
                err, transferred, key, address = status
                try:
                    f, ov, obj, callback = self._cache.pop(address)
                except KeyError:
                    # key is either zero, or it is used to return a pipe
                    # handle which should be closed to avoid a leak.
                    if key not in (0, _overlapped.INVALID_HANDLE_VALUE):
                        _winapi.CloseHandle(key)
                    continue

                if obj in self._stopped_serving:
                    f.cancel()
                # Futures might already be resolved or cancelled
                elif not f.done():
                    self.__events.append((f, callback, transferred, key, ov))

        # Remove unregistered futures
        for ov in self._unregistered:
            self._cache.pop(ov.address, None)
        self._unregistered.clear()


class _EventPoller:
    sig_events: QtCore.SignalInstance

    """Polling of events in separate thread."""

    def __init__(self, sig_events: QtCore.SignalInstance) -> None:
        self.sig_events = sig_events

    def start(self, proactor: _IocpProactor) -> None:
        logger.debug("Starting (proactor: {})...", proactor)
        self.__worker = _EventWorker(proactor, self)
        self.__worker.start()

    def stop(self) -> None:
        logger.debug("Stopping worker thread...")
        self.__worker.stop()


class _EventWorker(QtCore.QThread):
    def __init__(self, proactor: _IocpProactor, parent: _EventPoller) -> None:
        super().__init__()

        self.__stop = False
        self.__proactor = proactor
        self.__sig_events: QtCore.SignalInstance = parent.sig_events
        self.__semaphore = QtCore.QSemaphore()

    def start(self) -> None:
        super().start()
        self.__semaphore.acquire()

    def stop(self) -> None:
        self.__stop = True
        # Wait for thread to end
        self.wait()

    def run(self) -> None:
        logger.debug("Thread started")
        self.__semaphore.release()

        while not self.__stop:
            if events := self.__proactor.select(0.01):  # type: ignore[arg-type]
                logger.debug("Got events from poll: {}", events)
                self.__sig_events.emit(events)

        logger.debug("Exiting thread")
