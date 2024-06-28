from contextvars import ContextVar

from libresvip.core.lyric_phoneme.chinese import get_pinyin_series
from libresvip.utils.translation import gettext_lazy as _

from ..phoneme_dict import get_opencpop_dict

pinyin_list_ctx: ContextVar[list[str]] = ContextVar("pinyin_list")
phoneme_table_ctx: ContextVar[dict[str, str]] = ContextVar("phoneme_table")


def split(pinyin: str) -> tuple[str, str]:
    phoneme_table = phoneme_table_ctx.get()
    if pinyin not in phoneme_table:
        raise ValueError(
            _(
                'The selected dictionary does not contain the pronunciation "{}". Please check the pronunciation or try another dictionary.'
            ).format(pinyin)
        )

    phonemes = phoneme_table[pinyin].split()
    return ("", phonemes[0]) if len(phonemes) < 2 else (phonemes[0], phonemes[1])


def add_pinyin_from_lyrics(lyric_list: list[str]) -> None:
    pinyin_array = get_pinyin_series(lyric_list)
    pinyin_list = pinyin_list_ctx.get()
    pinyin_list.extend(pinyin_array)


def load_phoneme_table(dict_name: str) -> None:
    phoneme_table_ctx.set(get_opencpop_dict(dict_name))


def clear_all_pinyin() -> None:
    pinyin_list_ctx.set([])


def get_note_pinyin(note_lyric: str, index: int) -> str:
    pinyin_list = pinyin_list_ctx.get()
    return "-" if "-" in note_lyric else pinyin_list[index]
