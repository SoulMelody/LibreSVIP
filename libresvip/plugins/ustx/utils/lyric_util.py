from libresvip.utils.text import CustomBoundriesBlacklist

unsupported_symbols = CustomBoundriesBlacklist(
    [",", "，", ".", "。", "?", "？", "!", "！"],
    right_boundary="$",
    match_substrings=True,
)


def is_punctuation(c: str) -> bool:
    return unsupported_symbols.is_blacklisted(c)


def get_symbol_removed_lyric(lyric: str) -> str:
    return unsupported_symbols.cleanse_text(lyric)
