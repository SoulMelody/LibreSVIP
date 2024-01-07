from collections.abc import Iterable

from wanakana.japanese import (
    is_kana,
    is_romaji,
    split_into_romaji,
)

__all__ = [
    "is_kana",
    "is_romaji",
    "get_romaji_series",
]


def get_romaji_series(
    japanese_series: Iterable[str],
) -> list[str]:
    japanese_str = "".join(japanese_series)
    return [romaji for _, _, romaji in split_into_romaji(japanese_str)]
