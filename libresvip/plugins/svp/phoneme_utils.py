import re
from collections.abc import Iterable

from bidict import bidict

from libresvip.core.compat import json, package_path
from libresvip.core.constants import DEFAULT_PHONEME
from libresvip.core.lyric_phoneme.chinese import get_pinyin_series
from libresvip.core.lyric_phoneme.japanese import to_romaji

from .constants import DEFAULT_DURATIONS, DEFAULT_PHONE_RATIO

resource_dir = package_path("libresvip.plugins.svp")
phoneme_dictionary = json.loads(
    (resource_dir / "phoneme_dictionary.json").read_text(encoding="utf-8")
)
xsampa_dictionary = {
    language: bidict(xsampa_dict)
    for language, xsampa_dict in json.loads(
        (resource_dir / "xsampa_dictionary.json").read_text(encoding="utf-8")
    ).items()
}


def sv_g2p(lyrics: Iterable[str], languages: Iterable[str]) -> list[str]:
    phoneme_list = []
    builder = []
    for lyric, language in zip(lyrics, languages):
        if re.match(r"[a-zA-Z]", lyric) is not None:
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
    return xsampa_dictionary[language].inverse.get(xsampa, DEFAULT_PHONEME)


def get_phoneme_categories(phoneme_parts: list[str], language: str) -> list[str]:
    if language in phoneme_dictionary:
        phoneme_categories = [
            phoneme_dictionary[language].get(phoneme) for phoneme in phoneme_parts
        ]
        if all(phoneme_category is not None for phoneme_category in phoneme_categories):
            return phoneme_categories
    return []


def number_of_phones(phoneme: str, language: str) -> int:
    phoneme_parts = phoneme.split()
    phoneme_categories = get_phoneme_categories(phoneme_parts, language)
    return len(phoneme_categories) if phoneme_categories else 2


def default_phone_marks(phoneme: str, language: str) -> list[float]:
    res = [0.0, 0.0]
    if phoneme == "-":
        return res
    phoneme_parts = phoneme.split()
    if phoneme_categories := get_phoneme_categories(phoneme_parts, language):
        res[0] = getattr(DEFAULT_DURATIONS, phoneme_categories[0])
        index = 0 if phoneme_categories[0] in {"vowel", "diphthong"} else 1
        res[1] = DEFAULT_PHONE_RATIO if index < len(phoneme_categories) else 0.0
    return res
