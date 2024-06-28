from retrie.retrie import Blacklist

symbols_blacklist = Blacklist([",", ".", "?", "!", "，", "。", "？", "！"], match_substrings=True)


def get_symbol_removed_lyric(lyric: str) -> str:
    if len(lyric) > 1:
        lyric = symbols_blacklist.cleanse_text(lyric)
    return lyric
