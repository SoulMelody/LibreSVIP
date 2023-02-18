import pathlib
from typing import Callable, List, Union

import charset_normalizer
from more_itertools import locate, rlocate


def read_file(path: Union[str, pathlib.Path]) -> str:
    if not isinstance(path, pathlib.Path):
        path = pathlib.Path(path)
    content = path.read_bytes()
    guessed_charset = charset_normalizer.detect(content)
    if guessed_charset["encoding"] is None:
        encoding = "utf-8"
    else:
        encoding = guessed_charset["encoding"]
    return content.decode(encoding)


def find_index(tempo_list: List, pred: Callable) -> int:
    try:
        return next(locate(tempo_list, pred))
    except StopIteration:
        return -1


def find_last_index(tempo_list: List, pred: Callable) -> int:
    try:
        return next(rlocate(tempo_list, pred))
    except StopIteration:
        return -1
