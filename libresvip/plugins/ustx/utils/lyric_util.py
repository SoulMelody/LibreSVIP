from libresvip.core.lyric_phoneme.chinese import CHINESE_RE


class LyricUtil:
    unsupported_symbols = "".join((",", ".", "?", "!", "，", "。", "？", "！"))

    @staticmethod
    def is_hanzi(c: str) -> bool:
        return CHINESE_RE.match(c) is not None

    @classmethod
    def is_punctuation(cls, c: str) -> bool:
        return c in cls.unsupported_symbols

    @classmethod
    def get_symbol_removed_lyric(cls, lyric: str) -> str:
        return lyric.rstrip(cls.unsupported_symbols)
