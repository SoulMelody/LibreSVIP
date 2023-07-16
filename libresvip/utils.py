import contextlib
import functools
import pathlib
from types import FunctionType
from typing import Callable, Optional, TypeVar

import charset_normalizer
from more_itertools import locate, rlocate

T = TypeVar("T")


def ensure_path(func: FunctionType) -> FunctionType:
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


def find_index(tempo_list: list[T], pred: Callable[[T], bool]) -> int:
    return next(locate(tempo_list, pred), -1)


def find_last_index(tempo_list: list[T], pred: Callable[[T], bool]) -> int:
    return next(rlocate(tempo_list, pred), -1)


def download_and_setup_ffmpeg():
    with contextlib.suppress(ImportError):
        import static_ffmpeg
        import static_ffmpeg.run

        # static_ffmpeg.run.PLATFORM_ZIP_FILES = {
        #     platform: "https://ghproxy.com/" + url
        #     for platform, url in static_ffmpeg.run.PLATFORM_ZIP_FILES.items()
        # }

        static_ffmpeg.add_paths()


def gettext_lazy(message: str) -> str:
    try:
        return gettext(message)
    except NameError:
        return message


def shorten_error_message(message: Optional[str]) -> str:
    if message is None:
        return ""
    error_lines = message.splitlines()
    if len(error_lines) > 30:
        message = "\n".join(error_lines[:15] + ["..."] + error_lines[-15:])
    return message
