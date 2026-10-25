"""Shared file access for the archive-based formats.

Rust's `libresvip_core::io` exposes `read_shared` because an `Arc<[u8]>` can be
handed to several consumers without copying. Python's `bytes` is already an
immutable, reference-counted buffer, so there is no `Arc` equivalent to build —
what *does* cost is the pattern it replaces:

    zipfile.Path(io.BytesIO(path.read_bytes()))

`read_bytes()` produces one copy of the archive and `io.BytesIO` produces a
second, both alive for as long as the archive is open. A 200 MiB project
therefore peaks at 400 MiB before a single entry is parsed. `zipfile.ZipFile`
seeks its source itself, so opening the path directly needs no copy at all.
"""

import pathlib
import zipfile
from collections.abc import Generator
from contextlib import contextmanager


@contextmanager
def open_shared_archive(path: pathlib.Path) -> Generator[zipfile.ZipFile, None, None]:
    """Open `path` as a zip archive without copying it into memory.

    The archive reads straight from the file, so memory use stays flat regardless
    of project size. Entries are read on demand, which is why the handle has to
    outlive the caller's use of it — hence the context manager rather than a
    plain function.
    """
    with zipfile.ZipFile(path) as archive:
        yield archive


@contextmanager
def open_shared_archive_path(path: pathlib.Path) -> Generator[zipfile.Path, None, None]:
    """`open_shared_archive` in the `zipfile.Path` form the plugins index into.

    Callers use `(archive / "entry.json").read_bytes()`; `zipfile.Path` keeps
    that shape while sharing the single archive handle.
    """
    with open_shared_archive(path) as archive:
        yield zipfile.Path(archive)
