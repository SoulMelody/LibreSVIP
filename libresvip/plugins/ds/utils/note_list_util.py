from libresvip.core.exceptions import ParamsError
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import Note
from libresvip.utils.music_math import midi2note
from libresvip.utils.translation import gettext_lazy as _

from ..models.ds_note import (
    AspirationDsNote,
    AspirationDsPhoneme,
    DsNote,
    DsPhoneme,
    DsPhonemeItem,
    RestDsNote,
    RestDsPhoneme,
)
from . import lyric_util, pinyin_util


def encode_notes(
    os_notes: list[Note],
    synchronizer: TimeSynchronizer,
    trailing_space: float = 0.05,
) -> list[DsNote]:
    ds_notes: list[DsNote] = []
    prev_end_in_ticks = 0
    prev_actual_end_in_secs = 0.0
    prev_phoneme = DsPhoneme()
    init_pinyin_utils(os_notes)
    min_asp_len = 0.1
    max_asp_len = 0.4
    for index, note in enumerate(os_notes):
        # Calculate Positions
        prev_end_in_secs = synchronizer.get_actual_secs_from_ticks(prev_end_in_ticks)
        cur_start_in_ticks = note.start_pos
        cur_end_in_ticks = cur_start_in_ticks + note.length
        cur_start_in_secs = synchronizer.get_actual_secs_from_ticks(cur_start_in_ticks)
        cur_end_in_secs = synchronizer.get_actual_secs_from_ticks(cur_end_in_ticks)
        cur_actual_start_in_secs = cur_start_in_secs
        cur_actual_end_in_secs = cur_end_in_secs
        if note.edited_phones is not None and note.edited_phones.head_length_in_secs >= 0:
            cur_actual_start_in_secs -= note.edited_phones.head_length_in_secs
        elif "-" not in note.lyric:
            raise ParamsError(_("The source file lacks phoneme parameters."))
        if (
            index < len(os_notes) - 1
            and os_notes[index + 1].edited_phones is not None
            and os_notes[index + 1].edited_phones.head_length_in_secs >= 0  # type: ignore[union-attr]
        ):
            next_note = os_notes[index + 1]
            next_start_in_ticks = next_note.start_pos
            next_start_in_secs = synchronizer.get_actual_secs_from_ticks(next_start_in_ticks)
            next_head = os_notes[index + 1].edited_phones.head_length_in_secs  # type: ignore[union-attr]
            next_actual_start_in_secs = next_start_in_secs - next_head
            if cur_end_in_secs > next_actual_start_in_secs:
                cur_actual_end_in_secs -= cur_end_in_secs - next_actual_start_in_secs

        # Fill Note Gap
        gap = cur_actual_start_in_secs - prev_actual_end_in_secs  # 音符间隙
        if gap > 0:  # 有间隙
            if gap < min_asp_len:  # 间隙很小, 休止
                rest_phoneme = RestDsPhoneme(
                    _duration=round(cur_actual_start_in_secs - prev_actual_end_in_secs, 6)
                )
                rest_note = RestDsNote(
                    round(cur_start_in_secs - prev_end_in_secs, 6),
                    rest_phoneme,
                )
                ds_notes.append(rest_note)
                prev_phoneme = rest_phoneme
            elif gap < max_asp_len:  # 间隙适中, 换气
                asp_phoneme = AspirationDsPhoneme(
                    _duration=round(cur_actual_start_in_secs - prev_actual_end_in_secs, 6)
                )
                aps_note = AspirationDsNote(
                    round(cur_start_in_secs - prev_end_in_secs, 6), asp_phoneme
                )
                ds_notes.append(aps_note)
                prev_phoneme = asp_phoneme
            else:  # 间隙很大, 换气
                rest_phoneme = RestDsPhoneme(
                    _duration=round(
                        cur_actual_start_in_secs - prev_actual_end_in_secs - max_asp_len,
                        6,
                    )
                )
                rest_note = RestDsNote(
                    round(cur_start_in_secs - prev_end_in_secs - max_asp_len, 6),
                    rest_phoneme,
                )
                ds_notes.append(rest_note)
                asp_phoneme = AspirationDsPhoneme(_duration=round(max_asp_len, 6))
                aps_note = AspirationDsNote(round(max_asp_len, 6), asp_phoneme)
                ds_notes.append(aps_note)
                prev_phoneme = asp_phoneme

        # Convert OpenSvip Notes To DsNotes
        ds_phoneme = DsPhoneme()
        if "-" in note.lyric:  # 转音
            ds_phoneme.vowel = DsPhonemeItem(
                phoneme=prev_phoneme.vowel.phoneme,
                duration=round(cur_actual_end_in_secs - cur_actual_start_in_secs, 6),
                note_name=midi2note(note.key_number),
            )
        else:
            pinyin = note.pronunciation or pinyin_util.get_note_pinyin(note.lyric, index)
            consonant, vowel = pinyin_util.split(pinyin)
            if consonant:  # 不是纯元音
                consonant_note_name = (
                    midi2note(note.key_number)
                    if prev_phoneme.vowel.phoneme in ["SP", "AP"]
                    else prev_phoneme.vowel.note_name
                )
                ds_phoneme.consonant = DsPhonemeItem(
                    phoneme=consonant,
                    duration=round(cur_start_in_secs - cur_actual_start_in_secs, 6),
                    note_name=consonant_note_name,
                )
                ds_phoneme.vowel = DsPhonemeItem(
                    phoneme=vowel,
                    duration=round(cur_actual_end_in_secs - cur_start_in_secs, 6),
                    note_name=midi2note(note.key_number),
                )
            else:  # 纯元音
                ds_phoneme.vowel = DsPhonemeItem(
                    phoneme=vowel,
                    duration=round(cur_actual_end_in_secs - cur_actual_start_in_secs, 6),
                    note_name=midi2note(note.key_number),
                )
        ds_note = DsNote(
            lyric=lyric_util.get_symbol_removed_lyric(note.lyric),
            ds_phoneme=ds_phoneme,
            note_name=midi2note(note.key_number),
            duration=round(cur_end_in_secs - cur_start_in_secs, 6),
        )
        ds_notes.append(ds_note)

        prev_end_in_ticks = cur_end_in_ticks
        prev_actual_end_in_secs = cur_actual_end_in_secs
        prev_phoneme = ds_phoneme
    insert_end_rest_note(ds_notes, trailing_space)
    return ds_notes


def insert_end_rest_note(ds_notes: list[DsNote], trailing_space: float = 0.05) -> None:
    end_rest_phoneme = RestDsPhoneme(_duration=trailing_space)
    end_rest_note = RestDsNote(duration=trailing_space, ds_phoneme=end_rest_phoneme)
    ds_notes.append(end_rest_note)


def init_pinyin_utils(os_notes: list[Note]) -> None:
    lyric_list = [note.lyric for note in os_notes]
    pinyin_util.clear_all_pinyin()
    pinyin_util.add_pinyin_from_lyrics(lyric_list)
