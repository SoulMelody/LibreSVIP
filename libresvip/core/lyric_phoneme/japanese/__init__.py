from typing import Iterable, List

from wanakana.japanese import (
    is_japanese,  # noqa: F401
    split_into_romaji,
)


def get_romaji_series(
    japanese_series: Iterable[str],
) -> List[str]:
    japanese_str = ''.join(japanese_series)
    romaji_list = []
    for _, _, romaji in split_into_romaji(japanese_str):
        romaji_list.append(romaji)
    return romaji_list
