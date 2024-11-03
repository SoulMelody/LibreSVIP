# © 2018 Gerard Marull-Paretas <gerard@teslabs.com>
# © 2014 Mark Harviston <mark.harviston@gmail.com>
# © 2014 Arve Knudsen <arve.knudsen@gmail.com>
# BSD License

"""UNIX specific Quamash functionality."""

from __future__ import annotations

import asyncio
import selectors
from collections.abc import Iterator, Mapping
from typing import TYPE_CHECKING, Any, Optional

from loguru import logger
from PySide6 import QtCore

from ._common import _fileno

if TYPE_CHECKING:
    from _typeshed import FileDescriptor, FileDescriptorLike


EVENT_READ = 1 << 0
EVENT_WRITE = 1 << 1


class _SelectorMapping(Mapping[int, selectors.SelectorKey]):
    """Mapping of file objects to selector keys."""

    def __init__(self, selector: _Selector) -> None:
        self._selector = selector

    def __len__(self) -> int:
        return len(self._selector._fd_to_key)

    def __getitem__(self, fileobj: FileDescriptorLike) -> selectors.SelectorKey:
        try:
            fd = self._selector._fileobj_lookup(fileobj)
            return self._selector._fd_to_key[fd]
        except KeyError as e:
            msg = f"{fileobj!r} is not registered"
            raise KeyError(msg) from e

    def __iter__(self) -> Iterator[FileDescriptor]:
        yield from iter(self._selector._fd_to_key)


class _Selector(selectors.BaseSelector):
    def __init__(self, parent: _SelectorEventLoop) -> None:
        # this maps file descriptors to keys
        self._fd_to_key: dict[FileDescriptor, selectors.SelectorKey] = {}
        # read-only mapping returned by get_map()
        self.__map = _SelectorMapping(self)
        self.__read_notifiers: dict[FileDescriptorLike, QtCore.QSocketNotifier] = {}
        self.__write_notifiers: dict[FileDescriptorLike, QtCore.QSocketNotifier] = {}
        self.__parent = parent

    def select(self, timeout: Optional[float] = None) -> list[tuple[selectors.SelectorKey, int]]:
        """Implement abstract method even though we don't need it."""
        raise NotImplementedError

    def _fileobj_lookup(self, fileobj: FileDescriptorLike) -> FileDescriptor:
        """Return a file descriptor from a file object.

        This wraps _fileno() to do an exhaustive search in case
        the object is invalid but we still have it in our map.  This
        is used by unregister() so we can unregister an object that
        was previously registered even if it is closed.  It is also
        used by _SelectorMapping.
        """
        try:
            return _fileno(fileobj)
        except ValueError:
            # Do an exhaustive search.
            for key in self._fd_to_key.values():
                if key.fileobj is fileobj:
                    return key.fd
            # Raise ValueError after all.
            raise

    def register(
        self,
        fileobj: FileDescriptorLike,
        events: int,
        data: Optional[Any] = None,
    ) -> selectors.SelectorKey:
        if (not events) or (events & ~(EVENT_READ | EVENT_WRITE)):
            msg = f"Invalid events: {events!r}"
            raise ValueError(msg)

        key = selectors.SelectorKey(fileobj, self._fileobj_lookup(fileobj), events, data)

        if key.fd in self._fd_to_key:
            msg = f"{fileobj!r} (FD {key.fd}) is already registered"
            raise KeyError(msg)

        self._fd_to_key[key.fd] = key

        if events & EVENT_READ:
            notifier = QtCore.QSocketNotifier(key.fd, QtCore.QSocketNotifier.Read)
            notifier.activated["int"].connect(self.__on_read_activated)
            self.__read_notifiers[key.fd] = notifier
        if events & EVENT_WRITE:
            notifier = QtCore.QSocketNotifier(key.fd, QtCore.QSocketNotifier.Write)
            notifier.activated["int"].connect(self.__on_write_activated)
            self.__write_notifiers[key.fd] = notifier

        return key

    def __on_read_activated(self, fd: FileDescriptor) -> None:
        logger.debug("File {} ready to read", fd)
        if key := self._key_from_fd(fd):
            self.__parent._process_event(key, EVENT_READ & key.events)

    def __on_write_activated(self, fd: FileDescriptor) -> None:
        logger.debug("File {} ready to write", fd)
        if key := self._key_from_fd(fd):
            self.__parent._process_event(key, EVENT_WRITE & key.events)

    def unregister(self, fileobj: FileDescriptorLike) -> selectors.SelectorKey:
        def drop_notifier(
            notifiers: dict[FileDescriptorLike, QtCore.QSocketNotifier],
        ) -> None:
            try:
                notifier = notifiers.pop(key.fd)
            except KeyError:
                pass
            else:
                notifier.activated["int"].disconnect()

        try:
            key = self._fd_to_key.pop(self._fileobj_lookup(fileobj))
        except KeyError:
            msg = f"{fileobj!r} is not registered"
            raise KeyError(msg) from None

        drop_notifier(self.__read_notifiers)
        drop_notifier(self.__write_notifiers)

        return key

    def modify(
        self,
        fileobj: FileDescriptorLike,
        events: int,
        data: Optional[Any] = None,
    ) -> selectors.SelectorKey:
        try:
            key = self._fd_to_key[self._fileobj_lookup(fileobj)]
        except KeyError:
            msg = f"{fileobj!r} is not registered"
            raise KeyError(msg) from None
        if events != key.events:
            self.unregister(fileobj)
            key = self.register(fileobj, events, data)
        elif data != key.data:
            # Use a shortcut to update the data.
            key = key._replace(data=data)
            self._fd_to_key[key.fd] = key
        return key

    def close(self) -> None:
        logger.debug("Closing")
        self._fd_to_key.clear()
        self.__read_notifiers.clear()
        self.__write_notifiers.clear()

    def get_map(self) -> Mapping[FileDescriptorLike, selectors.SelectorKey]:
        return self.__map  # type: ignore[return-value]

    def _key_from_fd(self, fd: FileDescriptor) -> Optional[selectors.SelectorKey]:
        """
        Return the key associated to a given file descriptor.

        Parameters:
        fd -- file descriptor

        Returns:
        corresponding key, or None if not found

        """
        try:
            return self._fd_to_key[fd]
        except KeyError:
            return None


class _SelectorEventLoop(asyncio.SelectorEventLoop):
    def __init__(self) -> None:
        selector = _Selector(self)
        super().__init__(selector)

    def _before_run_forever(self) -> None:
        pass

    def _after_run_forever(self) -> None:
        pass

    def _process_event(self, key: selectors.SelectorKey, mask: int) -> None:
        """Selector has delivered us an event."""
        logger.debug("Processing event with key {} and mask {}", key, mask)
        fileobj, (reader, writer) = key.fileobj, key.data
        if mask & selectors.EVENT_READ and reader is not None:
            if reader._cancelled:
                self.remove_reader(fileobj)
            else:
                logger.debug("Invoking reader callback: {}", reader)
                reader._run()
        if mask & selectors.EVENT_WRITE and writer is not None:
            if writer._cancelled:
                self.remove_writer(fileobj)
            else:
                logger.debug("Invoking writer callback: {}", writer)
                writer._run()
