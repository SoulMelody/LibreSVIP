import re
import textwrap
from typing import Any, Optional, cast

import charset_normalizer
import zhon
from retrie.retrie import WORD_BOUNDARY, Blacklist

LATIN_ALPHABET: re.Pattern[str] = re.compile(r"[a-zA-Z]+")
SYMBOL_PATTERN: re.Pattern[str] = re.compile(
    rf"(?!-)[\!\"\#\$%\&'\(\)\*,\./:;<=>\?\[\\\]\^_`\{{\|\}}\~{zhon.hanzi.punctuation}]+"
)


class CustomBoundriesMixin:
    def __init__(
        self,
        *args: Any,
        left_boundary: str = WORD_BOUNDARY,
        right_boundary: str = WORD_BOUNDARY,
        **kwargs: Any,
    ) -> None:
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
            # \b is non-capturing, so doesn't need to be wrapped
            lookahead = left_boundary
        else:
            lookahead = f"(?={left_boundary})" if left_boundary else ""

        if right_boundary == WORD_BOUNDARY:
            # \b is non-capturing, so doesn't need to be wrapped
            lookbehind = right_boundary
        else:
            lookbehind = f"(?<={right_boundary})" if right_boundary else ""

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


def shorten_error_message(message: Optional[str]) -> str:
    if message is None:
        return ""
    error_lines = textwrap.wrap(message, 70)
    if len(error_lines) > 30:
        message = "\n".join(error_lines[:15] + ["..."] + error_lines[-15:])
    else:
        message = "\n".join(error_lines)
    return message
