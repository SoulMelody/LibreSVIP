from typing import Any

from wanakana.japanese import (
    is_kana,
    is_romaji,
    to_hiragana,
    to_katakana,
)
from wanakana.japanese import to_romaji as _to_romaji

__all__ = [
    "is_kana",
    "is_romaji",
    "to_hiragana",
    "to_katakana",
    "to_romaji",
]


def to_romaji(word: str, **kwargs: Any) -> str:
    kwargs.setdefault("custom_romaji_mapping", {"っ": "cl"})
    return _to_romaji(word, **kwargs) if word else ""
