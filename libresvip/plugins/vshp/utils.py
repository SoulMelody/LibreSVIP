import contextlib


def ansi2unicode(content: bytes) -> str:
    for possible_encoding in [
        "utf-8",
        "gbk",
        "shift-jis",
        "euc-kr",
        "big5",
    ]:
        with contextlib.suppress(UnicodeDecodeError):
            return content.decode(possible_encoding)
    return content.decode(errors="replace")
