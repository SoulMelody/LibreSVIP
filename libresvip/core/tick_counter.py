import functools
import math

import more_itertools
import portion

from libresvip.model.base import SongTempo, TimeSignature
from libresvip.utils.search import find_last_index

from .time_interval import PiecewiseIntervalDict


def skip_tempo_list(tempo_list: list[SongTempo], skip_ticks: int) -> list[SongTempo]:
    result = [
        tempo.model_copy(update={"position": tempo.position - skip_ticks})
        for tempo in tempo_list
        if tempo.position >= skip_ticks
    ]
    if not result or result[0].position > 0:
        i = find_last_index(tempo_list, lambda tempo: tempo.position <= skip_ticks)
        tempo = (
            SongTempo()
            if i == -1 and not tempo_list
            else tempo_list[i].model_copy(update={"position": 0})
        )
        result.insert(0, tempo)
    return result


def skip_beat_list(beat_list: list[TimeSignature], skip_bars: int) -> list[TimeSignature]:
    result = [
        beat.model_copy(update={"bar_index": beat.bar_index - skip_bars})
        for beat in beat_list
        if beat.bar_index >= skip_bars
    ]
    if not result or result[0].bar_index > 0:
        i = find_last_index(beat_list, lambda beat: beat.bar_index <= skip_bars)
        beat = (
            TimeSignature()
            if i == -1 and not beat_list
            else beat_list[i].model_copy(update={"bar_index": 0})
        )
        result.insert(0, beat)
    return result


def shift_tempo_list(tempo_list: list[SongTempo], shift_ticks: int) -> list[SongTempo]:
    result = tempo_list[:1]
    result.extend(
        tempo.model_copy(update={"position": tempo.position + shift_ticks})
        for tempo in tempo_list[1:]
    )
    return result


def shift_beat_list(beat_list: list[TimeSignature], shift_bars: int) -> list[TimeSignature]:
    result = beat_list[:1]
    result.extend(
        beat.model_copy(update={"bar_index": beat.bar_index + shift_bars}) for beat in beat_list[1:]
    )
    return result


def calc_bar_index(tick: float, base_tick: float, beat: TimeSignature) -> int:
    return beat.bar_index + math.ceil((tick - base_tick) / beat.bar_length())


def find_bar_index(beat_list: list[TimeSignature], ticks: int) -> int:
    tick = 0
    ticks2beat_interval_dict = PiecewiseIntervalDict()
    next_tick = None
    for beat, next_beat in more_itertools.pairwise(beat_list):
        next_tick = tick + beat.bar_length() * (next_beat.bar_index - beat.bar_index)
        ticks2beat_interval_dict[portion.closedopen(tick, next_tick)] = functools.partial(
            calc_bar_index, base_tick=tick, beat=beat
        )
        tick = next_tick
    if len(beat_list):
        ticks2beat_interval_dict[portion.closedopen(tick, portion.inf)] = functools.partial(
            calc_bar_index, base_tick=tick, beat=beat_list[-1]
        )
    return ticks2beat_interval_dict[ticks]  # type: ignore[return-value]
