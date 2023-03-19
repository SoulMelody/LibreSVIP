import functools
import pathlib
from typing import Callable, List

import charset_normalizer
from more_itertools import locate, rlocate


def ensure_path(func):
    @functools.wraps(func)
    def wrapper(self, path, *args, **kwargs):
        if not isinstance(path, pathlib.Path):
            path = pathlib.Path(path)
        return func(self, path, *args, **kwargs)

    return wrapper


def to_unicode(content: bytes) -> str:
    guessed_charset = charset_normalizer.detect(content)
    if guessed_charset["encoding"] is None:
        encoding = "utf-8"
    else:
        encoding = guessed_charset["encoding"]
    return content.decode(encoding)


@ensure_path
def read_file(path: pathlib.Path) -> str:
    content = path.read_bytes()
    return to_unicode(content)


def find_index(tempo_list: List, pred: Callable) -> int:
    return next(locate(tempo_list, pred), -1)


def find_last_index(tempo_list: List, pred: Callable) -> int:
    return next(rlocate(tempo_list, pred), -1)
