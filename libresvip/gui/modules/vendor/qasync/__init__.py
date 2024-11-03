"""
Implementation of the PEP 3156 Event-Loop with Qt.

Copyright (c) 2018 Gerard Marull-Paretas <gerard@teslabs.com>
Copyright (c) 2014 Mark Harviston <mark.harviston@gmail.com>
Copyright (c) 2014 Arve Knudsen <arve.knudsen@gmail.com>

BSD License
"""

# mypy: disable-error-code="attr-defined"

from __future__ import annotations

__author__ = (
    "Sam McCormack",
    "Gerard Marull-Paretas <gerard@teslabs.com>, "
    "Mark Harviston <mark.harviston@gmail.com>, "
    "Arve Knudsen <arve.knudsen@gmail.com>",
)
__all__ = ["QEventLoop", "QThreadExecutor"]

import asyncio
import itertools
import os
import sys
import time
from concurrent.futures import Future
from queue import Queue
from typing import TYPE_CHECKING, Any, Optional

from loguru import logger
from PySide6 import QtCore, QtWidgets
from typing_extensions import ParamSpec, Self, TypeVar, TypeVarTuple, Unpack

from ._common import _fileno, make_signaller

from __feature__ import snake_case, true_property  # isort: skip  # noqa: F401

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable
    from concurrent.futures import Executor
    from contextvars import Context
    from types import TracebackType

    from _typeshed import FileDescriptor

    _T = TypeVar("_T")
    _P = ParamSpec("_P")
    _Ts = TypeVarTuple("_Ts")

Slot = QtCore.Slot
QApplication = QtWidgets.QApplication


class _QThreadWorker(QtCore.QThread):
    """
    Read jobs from the queue and then execute them.

    For use by the QThreadExecutor
    """

    def __init__(
        self,
        queue: Queue[
            Optional[
                tuple[
                    Future[_T],
                    Callable[_P, _T],
                    _P.args,
                    _P.kwargs,
                ]
            ]
        ],
        num: int,
        stack_size: Optional[int] = None,
    ) -> None:
        self.__queue = queue
        self.__num = num
        super().__init__()
        if stack_size is not None:
            self.stack_size = stack_size

    def run(self) -> None:
        queue = self.__queue
        while True:
            command = queue.get()
            if command is None:
                # Stopping...
                break

            future, callback, args, kwargs = command
            logger.debug(
                "#{} got callback {} with args {} and kwargs {} from queue",
                self.__num,
                callback,
                args,
                kwargs,
            )
            if future.set_running_or_notify_cancel():
                logger.debug("Invoking callback")
                try:
                    r = callback(*args, **kwargs)
                except Exception as err:
                    logger.debug("Setting Future exception: {}", err)
                    future.set_exception(err)
                else:
                    logger.debug("Setting Future result: {}", r)
                    future.set_result(r)
            else:
                logger.debug("Future was canceled")

        logger.debug("Thread #{} stopped", self.__num)

    def wait(self) -> None:
        logger.debug("Waiting for thread #{} to stop...", self.__num)
        super().wait()


class QThreadExecutor:
    """
    ThreadExecutor that produces QThreads.

    Same API as `concurrent.futures.Executor`

    >>> from qasync import QThreadExecutor
    >>> with QThreadExecutor(5) as executor:
    ...     f = executor.submit(lambda x: 2 + x, 2)
    ...     r = f.result()
    ...     assert r == 4
    """

    def __init__(self, max_workers: int = 10, stack_size: Optional[int] = None) -> None:
        super().__init__()
        self.__max_workers = max_workers
        self.__queue: Queue[Optional[Any]] = Queue()
        if stack_size is None:
            # Match cpython/Python/thread_pthread.h
            if sys.platform.startswith("darwin"):
                stack_size = 16 * 2**20
            elif sys.platform.startswith("freebsd"):
                stack_size = 4 * 2**20
            elif sys.platform.startswith("aix"):
                stack_size = 2 * 2**20
        self.__workers = [
            _QThreadWorker(self.__queue, i + 1, stack_size) for i in range(max_workers)
        ]
        self.__been_shutdown = False

        for w in self.__workers:
            w.start()

    def submit(self, callback: Callable[_P, _T], *args: _P.args, **kwargs: _P.kwargs) -> Future[_T]:
        if self.__been_shutdown:
            msg = "QThreadExecutor has been shutdown"
            raise RuntimeError(msg)
        future: Future[_T] = Future()
        logger.debug(
            "Submitting callback {} with args {} and kwargs {} to thread worker queue",
            callback,
            args,
            kwargs,
        )
        self.__queue.put((future, callback, args, kwargs))
        return future

    def shutdown(self, wait: bool = True, *, cancel_futures: bool = False) -> None:
        if self.__been_shutdown:
            msg = "QThreadExecutor has been shutdown"
            raise RuntimeError(msg)

        self.__been_shutdown = True

        logger.debug("Shutting down")
        for _ in range(len(self.__workers)):
            # Signal workers to stop
            self.__queue.put(None)
        if wait:
            for w in self.__workers:
                w.wait()

    def __enter__(self) -> Self:
        if self.__been_shutdown:
            msg = "QThreadExecutor has been shutdown"
            raise RuntimeError(msg)
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        self.shutdown()


class _SimpleTimer(QtCore.QObject):
    def __init__(self) -> None:
        super().__init__()
        self.__callbacks: dict[int, asyncio.Handle] = {}
        self._stopped = False
        self.__debug_enabled = False

    def add_callback(self, handle: asyncio.TimerHandle, delay: float = 0) -> asyncio.TimerHandle:
        timerid = self.start_timer(int(max(0, delay) * 1000))
        self.__log_debug("Registering timer id {}", timerid)
        assert timerid not in self.__callbacks
        self.__callbacks[timerid] = handle
        return handle

    def timer_event(self, event: QtCore.QTimerEvent) -> None:
        timerid = event.timer_id()
        self.__log_debug("Timer event on id {}", timerid)
        if self._stopped:
            self.__log_debug("Timer stopped, killing {}", timerid)
            self.kill_timer(timerid)
            del self.__callbacks[timerid]
        else:
            try:
                handle = self.__callbacks[timerid]
            except KeyError as e:
                self.__log_debug(e)
            else:
                if handle._cancelled:
                    self.__log_debug("Handle {} cancelled", handle)
                else:
                    self.__log_debug("Calling handle {}", handle)
                    handle._run()
            finally:
                del self.__callbacks[timerid]
            self.kill_timer(timerid)

    def stop(self) -> None:
        self.__log_debug("Stopping timers")
        self._stopped = True

    def set_debug(self, enabled: bool) -> None:
        self.__debug_enabled = enabled

    def __log_debug(self, *args: _P.args, **kwargs: _P.kwargs) -> None:
        if self.__debug_enabled:
            logger.debug(*args, **kwargs)


class _QEventLoop(asyncio.AbstractEventLoop):
    """
    Implementation of asyncio event loop that uses the Qt Event loop.

    >>> import asyncio
    >>>
    >>> app = getfixture('application')
    >>>
    >>> async def xplusy(x, y):
    ...     await asyncio.sleep(.1)
    ...     assert x + y == 4
    ...     await asyncio.sleep(.1)
    >>>
    >>> loop = QEventLoop(app)
    >>> asyncio.set_event_loop(loop)
    >>> with loop:
    ...     loop.run_until_complete(xplusy(2, 2))

    If the event loop shall be used with an existing and already running QApplication
    it must be specified in the constructor via already_running=True
    In this case the user is responsible for loop cleanup with stop() and close()

    The set_running_loop parameter is there for backwards compatibility and does nothing.
    """

    def __init__(
        self,
        app: Optional[QtCore.QCoreApplication] = None,
        set_running_loop: bool = False,
        already_running: bool = False,
    ) -> None:
        self.__app = app or QApplication.instance()
        assert self.__app is not None, "No QApplication has been instantiated"
        self.__is_running = False
        self.__debug_enabled = False
        self.__default_executor = None
        self.__exception_handler = None
        self._read_notifiers: dict[FileDescriptor, QtCore.QSocketNotifier] = {}
        self._write_notifiers: dict[FileDescriptor, QtCore.QSocketNotifier] = {}
        self._timer = _SimpleTimer()

        signaller = make_signaller(object, tuple)
        self.__call_soon_signal = signaller.signal
        signaller.signal.connect(lambda callback, args: self.call_soon(callback, *args))

        assert self.__app is not None
        super().__init__()

        # We have to set __is_running to True after calling
        # super().__init__() because of a bug in BaseEventLoop.
        if already_running:
            self.__is_running = True

            # it must be ensured that all pre- and
            # postprocessing for the eventloop is done
            self._before_run_forever()
            self.__app.aboutToQuit.connect(self._after_run_forever)

            # for asyncio to recognize the already running loop
            asyncio.events._set_running_loop(self)

    def run_forever(self) -> None:
        """Run eventloop forever."""

        if self.__is_running:
            msg = "Event loop already running"
            raise RuntimeError(msg)

        self.__is_running = True
        self._before_run_forever()

        try:
            self.__log_debug("Starting Qt event loop")
            asyncio.events._set_running_loop(self)
            rslt = self.__app.exec()
            self.__log_debug("Qt event loop ended with result {}", rslt)
        finally:
            asyncio.events._set_running_loop(None)
            self._after_run_forever()
            self.__is_running = False

    def run_until_complete(self, future: Awaitable[_T]) -> _T:  # type: ignore[override]
        """Run until Future is complete."""

        if self.__is_running:
            msg = "Event loop already running"
            raise RuntimeError(msg)

        self.__log_debug("Running {} until complete", future)
        future = asyncio.ensure_future(future, loop=self)

        def stop(*args: Any) -> None:
            self.stop()

        future.add_done_callback(stop)
        try:
            self.run_forever()
        finally:
            future.remove_done_callback(stop)
        self.__app.process_events()  # run loop one last time to process all the events
        if not future.done():
            msg = "Event loop stopped before Future completed."
            raise RuntimeError(msg)

        self.__log_debug("Future {} finished running", future)
        return future.result()

    def stop(self) -> None:
        """Stop event loop."""
        if not self.__is_running:
            self.__log_debug("Already stopped")
            return

        self.__log_debug("Stopping event loop...")
        self.__is_running = False
        self.__app.exit()
        self.__log_debug("Stopped event loop")

    def is_running(self) -> bool:
        """Return True if the event loop is running, False otherwise."""
        return self.__is_running

    def close(self) -> None:
        """
        Release all resources used by the event loop.

        The loop cannot be restarted after it has been closed.
        """
        if self.is_running():
            msg = "Cannot close a running event loop"
            raise RuntimeError(msg)
        if self.is_closed():
            return

        self.__log_debug("Closing event loop...")
        if self.__default_executor is not None:
            self.__default_executor.shutdown()

        super().close()

        self._timer.stop()
        self.__app = None

        for notifier in itertools.chain(
            self._read_notifiers.values(), self._write_notifiers.values()
        ):
            notifier.set_enabled(False)

        self._read_notifiers.clear()
        self._write_notifiers.clear()

    def call_later(
        self,
        delay: float,
        callback: Callable[[Unpack[_Ts]], object],
        *args: Unpack[_Ts],
        context: Optional[Context] = None,
    ) -> asyncio.TimerHandle:
        """Register callback to be invoked after a certain delay."""
        if asyncio.iscoroutinefunction(callback):
            msg = "coroutines cannot be used with call_later"
            raise TypeError(msg)
        if not callable(callback):
            msg = f"callback must be callable: {type(callback).__name__}"
            raise TypeError(msg)

        self.__log_debug(
            "Registering callback {} to be invoked with arguments {} after {} second(s)",
            callback,
            args,
            delay,
        )

        return self._add_callback(asyncio.TimerHandle(delay, callback, args, self, context=context))

    def _add_callback(self, handle: asyncio.TimerHandle, delay: float = 0) -> asyncio.TimerHandle:
        return self._timer.add_callback(handle, delay)

    def call_soon(
        self,
        callback: Callable[[Unpack[_Ts]], object],
        *args: Unpack[_Ts],
        context: Optional[Context] = None,
    ) -> asyncio.Handle:
        """Register a callback to be run on the next iteration of the event loop."""
        return self.call_later(0, callback, *args, context=context)

    def call_at(
        self,
        when: float,
        callback: Callable[[Unpack[_Ts]], object],
        *args: Unpack[_Ts],
        context: Optional[Context] = None,
    ) -> asyncio.TimerHandle:
        """Register callback to be invoked at a certain time."""
        return self.call_later(when - self.time(), callback, *args, context=context)

    def time(self) -> float:
        """Get time according to event loop's clock."""
        return time.monotonic()

    def _add_reader(
        self,
        fd: FileDescriptor,
        callback: Callable[[Unpack[_Ts]], object],
        *args: Unpack[_Ts],
    ) -> None:
        """Register a callback for when a file descriptor is ready for reading."""
        self._check_closed()

        try:
            existing = self._read_notifiers[fd]
        except KeyError:
            pass
        else:
            # this is necessary to avoid race condition-like issues
            existing.set_enabled(False)
            existing.activated["int"].disconnect()
            # will get overwritten by the assignment below anyways

        notifier = QtCore.QSocketNotifier(_fileno(fd), QtCore.QSocketNotifier.Type.Read)
        notifier.set_enabled(True)
        self.__log_debug("Adding reader callback for file descriptor {}", fd)
        notifier.activated["int"].connect(
            lambda: self.__on_notifier_ready(self._read_notifiers, notifier, fd, callback, *args)
        )
        self._read_notifiers[fd] = notifier

    def _remove_reader(self, fd: FileDescriptor) -> Optional[bool]:
        """Remove reader callback."""
        if self.is_closed():
            return None

        self.__log_debug("Removing reader callback for file descriptor {}", fd)
        try:
            notifier = self._read_notifiers.pop(fd)
        except KeyError:
            return False
        else:
            notifier.set_enabled(False)
            return True

    def _add_writer(
        self,
        fd: FileDescriptor,
        callback: Callable[[Unpack[_Ts]], object],
        *args: Unpack[_Ts],
    ) -> None:
        """Register a callback for when a file descriptor is ready for writing."""
        self._check_closed()
        try:
            existing = self._write_notifiers[fd]
        except KeyError:
            pass
        else:
            # this is necessary to avoid race condition-like issues
            existing.set_enabled(False)
            existing.activated["int"].disconnect()
            # will get overwritten by the assignment below anyways

        notifier = QtCore.QSocketNotifier(
            _fileno(fd),
            QtCore.QSocketNotifier.Type.Write,
        )
        notifier.set_enabled(True)
        self.__log_debug("Adding writer callback for file descriptor {}", fd)
        notifier.activated["int"].connect(
            lambda: self.__on_notifier_ready(self._write_notifiers, notifier, fd, callback, *args)
        )
        self._write_notifiers[fd] = notifier

    def _remove_writer(self, fd: FileDescriptor) -> Optional[bool]:
        """Remove writer callback."""
        if self.is_closed():
            return None

        self.__log_debug("Removing writer callback for file descriptor {}", fd)
        try:
            notifier = self._write_notifiers.pop(fd)
        except KeyError:
            return False
        else:
            notifier.set_enabled(False)
            return True

    def __notifier_cb_wrapper(
        self,
        notifiers: dict[FileDescriptor, QtCore.QSocketNotifier],
        notifier: QtCore.QSocketNotifier,
        fd: FileDescriptor,
        callback: Callable[[Unpack[_Ts]], _T],
        *args: Unpack[_Ts],
    ) -> None:
        # This wrapper gets called with a certain delay. We cannot know
        # for sure that the notifier is still the current notifier for
        # the fd.
        if notifiers.get(fd) is not notifier:
            return
        try:
            callback(*args)
        finally:
            # The notifier might have been overriden by the
            # callback. We must not re-enable it in that case.
            if notifiers.get(fd) is notifier:
                notifier.set_enabled(True)
            else:
                notifier.activated["int"].disconnect()

    def __on_notifier_ready(
        self,
        notifiers: dict[FileDescriptor, QtCore.QSocketNotifier],
        notifier: QtCore.QSocketNotifier,
        fd: FileDescriptor,
        callback: Callable[[Unpack[_Ts]], _T],
        *args: Unpack[_Ts],
    ) -> None:
        if fd not in notifiers:
            logger.warning(
                "Socket notifier for fd {} is ready, even though it should "
                "be disabled, not calling {} and disabling",
                fd,
                callback,
            )
            notifier.set_enabled(False)
            return

        # It can be necessary to disable QSocketNotifier when e.g. checking
        # ZeroMQ sockets for events
        assert notifier.is_enabled()
        self.__log_debug("Socket notifier for fd {} is ready", fd)
        notifier.set_enabled(False)
        self.call_soon(
            self.__notifier_cb_wrapper,
            notifiers,
            notifier,
            fd,
            callback,
            *args,
        )

    # Methods for interacting with threads.

    def call_soon_threadsafe(  # type: ignore[return-value]
        self,
        callback: Callable[[Unpack[_Ts]], _T],
        *args: Unpack[_Ts],
        context: Optional[Context] = None,
    ) -> asyncio.Handle:
        """Thread-safe version of call_soon."""
        self.__call_soon_signal.emit(callback, args)

    def run_in_executor(
        self,
        executor: Executor,
        callback: Callable[[Unpack[_Ts]], _T],
        *args: Unpack[_Ts],
    ) -> asyncio.Future[_T]:
        """Run callback in executor.

        If no executor is provided, the default executor will be used, which defers execution to
        a background thread.
        """
        self.__log_debug("Running callback {} with args {} in executor", callback, args)
        if isinstance(callback, asyncio.Handle):
            assert not args
            assert not isinstance(callback, asyncio.TimerHandle)
            if callback._cancelled:
                f: asyncio.Future[Any] = asyncio.Future()
                f.set_result(None)
                return f
            callback, args = callback.callback, callback.args

        if executor is None:
            self.__log_debug("Using default executor")
            executor = self.__default_executor

        if executor is None:
            self.__log_debug("Creating default executor")
            executor = QThreadExecutor()
            self.__default_executor = executor

        return asyncio.wrap_future(executor.submit(callback, *args))

    def set_default_executor(self, executor: Any) -> None:
        self.__default_executor = executor

    # Error handlers.

    def set_exception_handler(self, handler: Optional[asyncio.events._ExceptionHandler]) -> None:
        self.__exception_handler = handler  # type: ignore[assignment]

    def default_exception_handler(self, context: asyncio.events._Context) -> None:
        """Handle exceptions.

        This is the default exception handler.

        This is called when an exception occurs and no exception
        handler is set, and can be called by a custom exception
        handler that wants to defer to the default behavior.

        context parameter has the same meaning as in
        `call_exception_handler()`.
        """
        self.__log_debug("Default exception handler executing")
        message = context.get("message") or "Unhandled exception in event loop"

        try:
            exception = context["exception"]
        except KeyError:
            exc_info = sys.exc_info()
        else:
            exc_info = (type(exception), exception, exception.__traceback__)

        log_lines = [message]
        log_lines.extend(
            f"{key}: {context[key]!r}"
            for key in [k for k in sorted(context) if k not in {"message", "exception"}]
        )
        self.__log_error("\n".join(log_lines), exc_info=exc_info)

    def call_exception_handler(self, context: asyncio.events._Context) -> None:
        if self.__exception_handler is None:
            try:
                self.default_exception_handler(context)
            except Exception:
                # Second protection layer for unexpected errors
                # in the default implementation, as well as for subclassed
                # event loops with overloaded "default_exception_handler".
                self.__log_error("Exception in default exception handler", exc_info=True)

            return

        try:
            self.__exception_handler(self, context)
        except Exception as exc:
            # Exception in the user set custom exception handler.
            try:
                # Let's try the default handler.
                self.default_exception_handler(
                    {
                        "message": "Unhandled error in custom exception handler",
                        "exception": exc,
                        "context": context,
                    }
                )
            except Exception:
                # Guard 'default_exception_handler' in case it's
                # overloaded.
                self.__log_error(
                    "Exception in default exception handler while handling an unexpected error "
                    "in custom exception handler",
                    exc_info=True,
                )

    # Debug flag management.

    def get_debug(self) -> bool:
        return self.__debug_enabled

    def set_debug(self, enabled: bool) -> None:
        super().set_debug(enabled)
        self.__debug_enabled = enabled
        self._timer.set_debug(enabled)

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        self.stop()
        self.close()

    def __log_debug(self, *args: _P.args, **kwargs: _P.kwargs) -> None:
        if self.__debug_enabled:
            logger.debug(*args, **kwargs)

    @classmethod
    def __log_error(cls, *args: _P.args, **kwds: _P.kwargs) -> None:
        # In some cases, the error method itself fails, don't have a lot of options in that case
        try:
            logger.exception(*args, **kwds)
        except Exception:
            sys.stderr.write(f"{args!r}, {kwds!r}\n")


if os.name == "nt":
    from ._windows import _ProactorEventLoop

    QIOCPEventLoop = type("QIOCPEventLoop", (_QEventLoop, _ProactorEventLoop), {})
    QEventLoop = QIOCPEventLoop
else:
    from ._unix import _SelectorEventLoop

    QSelectorEventLoop = type("QSelectorEventLoop", (_QEventLoop, _SelectorEventLoop), {})
    QEventLoop = QSelectorEventLoop
