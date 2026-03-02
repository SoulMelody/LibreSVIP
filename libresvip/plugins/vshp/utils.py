import contextlib


def ansi2unicode(content: bytes) -> str:
    result = None
    for possible_encoding in [
        "utf-8",
        "gbk",
        "shift-jis",
        "euc-kr",
        "big5",
    ]:
        with contextlib.suppress(UnicodeDecodeError):
            result = content.decode(possible_encoding)
            break
    if result is None:
        result = content.decode(errors="replace")
    return result
