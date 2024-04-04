unsupported_symbols = ",.?!，。？！"


def is_punctuation(c: str) -> bool:
    return c in unsupported_symbols


def get_symbol_removed_lyric(lyric: str) -> str:
    return lyric.rstrip(unsupported_symbols)
