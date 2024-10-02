import contextlib
import encodings
import functools
import importlib
import pkgutil
import re
import textwrap
from collections.abc import Callable
from typing import Any, Optional, cast

import charset_normalizer.constant
import zhon
from retrie.retrie import WORD_BOUNDARY, Blacklist

LATIN_ALPHABET: re.Pattern[str] = re.compile(r"[a-zA-Z]+")
SYMBOL_PATTERN: re.Pattern[str] = re.compile(
    rf"(?!-)[\!\"\#\$%\&'\(\)\*,\./:;<=>\?\[\\\]\^_`\{{\|\}}\~{zhon.hanzi.punctuation}]+"
)


class CustomBoundriesMixin:
    re_flags: int
    parse_re_flags: Callable[[int], int]
    pattern: Callable[[], str]

    def __init__(
        self,
        *args: Any,
        left_boundary: Optional[str] = None,
        right_boundary: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        default_word_boundary = "" if kwargs.get("match_substrings") is True else WORD_BOUNDARY
        if left_boundary is None:
            left_boundary = default_word_boundary
        if right_boundary is None:
            right_boundary = default_word_boundary
        self.left_boundary = left_boundary
        self.right_boundary = right_boundary
        super().__init__(*args, **kwargs)

    def compile(
        self,
        word_boundary: Optional[str] = None,
        re_flags: int = -1,
    ) -> re.Pattern[str]:
        left_boundary = self.left_boundary if word_boundary is None else word_boundary
        right_boundary = self.right_boundary if word_boundary is None else word_boundary
        re_flags = self.re_flags if re_flags == -1 else re_flags

        if left_boundary == WORD_BOUNDARY:
            lookbehind = left_boundary
        else:
            lookbehind = f"(?<={left_boundary})" if left_boundary else ""

        if right_boundary == WORD_BOUNDARY:
            lookahead = right_boundary
        else:
            lookahead = f"(?={right_boundary})" if right_boundary else ""

        return re.compile(
            lookbehind + self.pattern() + lookahead,
            flags=self.parse_re_flags(re_flags),
        )


class CustomBoundriesBlacklist(CustomBoundriesMixin, Blacklist):
    pass


def to_unicode(content: bytes) -> str:
    guessed_charset = charset_normalizer.detect(content)
    encoding = (
        "utf-8" if guessed_charset["encoding"] is None else cast(str, guessed_charset["encoding"])
    )
    return content.decode(encoding)


@functools.cache
def supported_charset_names() -> list[str]:
    encoding_names = []
    for module_info in pkgutil.walk_packages(encodings.__path__):
        cp_name = module_info.name
        sub_module = importlib.import_module(f"encodings.{cp_name}")
        if not cp_name.endswith("_codec") and hasattr(sub_module, "getregentry"):
            with contextlib.suppress(ValueError):
                iana_name = charset_normalizer.utils.iana_name(cp_name)
                encoding_names.append(
                    charset_normalizer.constant.CHARDET_CORRESPONDENCE.get(iana_name, iana_name)
                )
    return sorted(encoding_names)


def shorten_error_message(message: Optional[str]) -> str:
    if message is None:
        return ""
    error_lines = textwrap.wrap(message, 70)
    if len(error_lines) > 30:
        message = "\n".join(error_lines[:15] + ["..."] + error_lines[-15:])
    else:
        message = "\n".join(error_lines)
    return message
