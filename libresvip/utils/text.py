import re
import textwrap
from typing import Optional, cast

import charset_normalizer
import zhon

LATIN_ALPHABET: re.Pattern[str] = re.compile(r"[a-zA-Z]+")
SYMBOL_PATTERN = re.compile(
    rf"(?!-)[\!\"\#\$%\&'\(\)\*,\./:;<=>\?\[\\\]\^_`\{{\|\}}\~{zhon.hanzi.punctuation}]+"
)


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
