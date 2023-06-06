from gettext import gettext as _

from libresvip.core.lyric_phoneme.chinese import get_pinyin_series

from ..phoneme_dict import get_opencpop_dict


class PinyinUtil:
    pinyin_list = []
    phoneme_table = {}

    @staticmethod
    def split(pinyin: str) -> tuple[str, str]:
        phoneme_table = PinyinUtil.phoneme_table
        if pinyin not in phoneme_table:
            raise Exception(
                _("The selected dictionary does not contain the pronunciation “{}”. Please check the pronunciation or try another dictionary.").format(pinyin)
            )

        phonemes = phoneme_table[pinyin]
        return ("", phonemes[0]) if len(phonemes) < 2 else (phonemes[0], phonemes[1])

    @classmethod
    def add_pinyin_from_lyrics(cls, lyric_list: list[str]) -> None:
        pinyinArray = get_pinyin_series(lyric_list)
        cls.pinyin_list.extend(pinyinArray)

    @classmethod
    def load_phoneme_table(cls, dict_name: str) -> None:
        cls.phoneme_table = get_opencpop_dict(dict_name)

    @classmethod
    def clear_all_pinyin(cls) -> None:
        cls.pinyin_list.clear()

    @classmethod
    def get_note_pinyin(cls, note_lyric: str, index: int) -> str:
        return "-" if "-" in note_lyric else cls.pinyin_list[index]
