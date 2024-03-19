import re
from collections.abc import Iterable

from bidict import bidict

from libresvip.core.compat import json, package_path
from libresvip.core.constants import DEFAULT_PHONEME
from libresvip.core.lyric_phoneme.chinese import get_pinyin_series
from libresvip.core.lyric_phoneme.japanese import to_romaji
from libresvip.utils.text import LATIN_ALPHABET

from .constants import DEFAULT_DURATIONS, DEFAULT_PHONE_RATIO

resource_dir = package_path("libresvip.plugins.svp")
phoneme_categories_by_language = json.loads(
    (resource_dir / "phoneme_categories.json").read_text(encoding="utf-8")
)
phoneme_dictionary = {
    language: bidict(xsampa_dict) if language in ["mandarin", "cantonese"] else xsampa_dict
    for language, xsampa_dict in json.loads(
        (resource_dir / "phoneme_dictionary.json").read_text(encoding="utf-8")
    ).items()
}


def sv_g2p(lyrics: Iterable[str], languages: Iterable[str]) -> list[str]:
    phoneme_list: list[str] = []
    builder: list[str] = []
    for lyric, language in zip(lyrics, languages):
        if LATIN_ALPHABET.match(lyric) is not None:
            if len(builder):
                phoneme_list.extend(
                    (to_romaji(part) for part in builder)
                    if language == "japanese"
                    else get_pinyin_series(builder, filter_non_chinese=False)
                )
                builder.clear()
            phoneme_list.append(lyric)
        else:
            builder.append(lyric)
    if builder:
        phoneme_list.extend(
            (to_romaji(part) for part in builder)
            if language == "japanese"
            else get_pinyin_series(builder, filter_non_chinese=False)
        )
    return phoneme_list


def xsampa2pinyin(xsampa: str, language: str) -> str:
    xsampa = re.sub(r"\s+", " ", xsampa).strip()
    return phoneme_dictionary[language].inverse.get(xsampa, DEFAULT_PHONEME)


def get_phoneme_categories(phoneme_parts: list[str], language: str) -> list[str]:
    if language in phoneme_categories_by_language:
        phoneme_categories = [
            phoneme_categories_by_language[language].get(phoneme) for phoneme in phoneme_parts
        ]
        if all(phoneme_category is not None for phoneme_category in phoneme_categories):
            return phoneme_categories
    return []


def number_of_phones(phoneme: str, language: str) -> int:
    phoneme_parts = phoneme.split()
    phoneme_categories = get_phoneme_categories(phoneme_parts, language)
    return len(phoneme_categories) if phoneme_categories else 2


def default_phone_marks(phoneme: str, language: str) -> list[float]:
    phoneme_parts = phoneme.split()
    res_len = max(len(phoneme_parts), 2)
    res = [0.0] * res_len
    if phoneme == "-":
        return res
    elif phoneme_categories := get_phoneme_categories(phoneme_parts, language):
        index = 0
        if phoneme_categories[index] in {"vowel", "diphthong"}:
            res[index] = getattr(DEFAULT_DURATIONS, phoneme_categories[index])
            index += 1
        if res_len > index:
            res[index:res_len] = [DEFAULT_PHONE_RATIO if index < res_len else 0.0] * (
                res_len - index
            )
    return res
