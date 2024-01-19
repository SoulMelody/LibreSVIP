import re
from collections.abc import Iterable

from libresvip.core.compat import json, package_path
from libresvip.core.constants import DEFAULT_PHONEME
from libresvip.core.lyric_phoneme.chinese import get_pinyin_series
from libresvip.core.lyric_phoneme.japanese import to_romaji

from .constants import DEFAULT_DURATIONS, DEFAULT_PHONE_RATIO
from .model import SVDatabase, SVNoteAttributes

resource_dir = package_path("libresvip.plugins.svp")
phoneme_dictionary = json.loads(
    (resource_dir / "phoneme_dictionary.json").read_text(encoding="utf-8")
)
xsampa_dictionary = json.loads(
    (resource_dir / "xsampa_dictionary.json").read_text(encoding="utf-8")
)


def sv_g2p(
    lyrics: Iterable[str], note_attributes: Iterable[SVNoteAttributes], database: SVDatabase
) -> list[str]:
    phoneme_list = []
    builder = []
    for lyric, note_attribute in zip(lyrics, note_attributes):
        if re.match(r"[a-zA-Z]", lyric) is not None:
            if len(builder):
                phoneme_list.extend(
                    (to_romaji(part) for part in builder)
                    if note_attribute.default_language(database) == "japanese"
                    else get_pinyin_series(builder, filter_non_chinese=False)
                )
                builder.clear()
            phoneme_list.append(lyric)
        else:
            builder.append(lyric)
    if builder:
        phoneme_list.extend(
            (to_romaji(part) for part in builder)
            if note_attribute.default_language(database) == "japanese"
            else get_pinyin_series(builder, filter_non_chinese=False)
        )
    return phoneme_list


def xsampa2pinyin(xsampa: str) -> str:
    xsampa = re.sub(r"\s+", " ", xsampa).strip()
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
    res[0] = getattr(DEFAULT_DURATIONS, phone_parts[0])
    index = 0 if phone_parts[0] in {"vowel", "diphthong"} else 1
    res[1] = DEFAULT_PHONE_RATIO if index < len(phone_parts) else 0.0
    return res
