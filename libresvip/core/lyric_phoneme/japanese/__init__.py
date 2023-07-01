from typing import Iterable

from wanakana.japanese import (
    is_japanese,  # noqa: F401
    split_into_romaji,
)


def get_romaji_series(
    japanese_series: Iterable[str],
) -> list[str]:
    japanese_str = "".join(japanese_series)
    return [romaji for _, _, romaji in split_into_romaji(japanese_str)]
