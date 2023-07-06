import pkgutil

import regex

from libresvip.core.constants import DEFAULT_PHONEME
from libresvip.core.lyric_phoneme.chinese import get_pinyin_series
from libresvip.model.base import json_loads

default_durations = {
    "stop": 0.10,
    "affricate": 0.125,
    "fricative": 0.125,
    "aspirate": 0.094,
    "liquid": 0.062,
    "nasal": 0.094,
    "vowel": 0.0,
    "semivowel": 0.055,
    "diphthong": 0.0,
}
default_phone_ratio = 1.8

phoneme_dictionary = json_loads(pkgutil.get_data(__package__, "phoneme_dictionary.json"))
xsampa_dictionary = json_loads(pkgutil.get_data(__package__, "xsampa_dictionary.json"))


def lyrics2pinyin(lyrics: list[str]) -> list[str]:
    pinyin_list = []
    builder = ""
    for lyric in lyrics:
        if regex.match(r"[a-zA-Z]", lyric) is not None:
            if len(builder):
                pinyin_list.extend(get_pinyin_series(builder, filter_non_chinese=False))
                builder = ""
            pinyin_list.append(lyric)
        else:
            builder += lyric
    if builder:
        pinyin_list.extend(get_pinyin_series(builder, filter_non_chinese=False))
    return pinyin_list


def xsampa2pinyin(xsampa: str) -> str:
    xsampa = regex.sub(r"\s+", " ", xsampa).strip()
    return xsampa_dictionary.get(xsampa, DEFAULT_PHONEME)


def number_of_phones(pinyin: str) -> int:
    if pinyin not in phoneme_dictionary:
        pinyin = DEFAULT_PHONEME
    return len(phoneme_dictionary[pinyin])


def default_phone_marks(pinyin: str) -> list[float]:
    res = [0.0, 0.0]
    if pinyin == "-":
        return res
    if pinyin not in phoneme_dictionary:
        pinyin = DEFAULT_PHONEME
    phone_parts = phoneme_dictionary[pinyin]
    res[0] = default_durations[phone_parts[0]]
    index = 0 if phone_parts[0] in {"vowel", "diphthong"} else 1
    res[1] = default_phone_ratio if index < len(phone_parts) else 0.0
    return res
