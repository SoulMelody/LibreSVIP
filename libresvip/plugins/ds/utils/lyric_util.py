class LyricUtil:
    symbols_to_remove = [",", ".", "?", "!", "，", "。", "？", "！"]

    @classmethod
    def get_symbol_removed_lyric(cls, lyric: str) -> str:
        if len(lyric) > 1:
            for symbol in cls.symbols_to_remove:
                lyric = lyric.replace(symbol, "")
        return lyric
