from typing import List

from libresvip.model.base import SongTempo, TimeSignature
from libresvip.utils import find_last_index


def skip_tempo_list(tempo_list: List[SongTempo], skip_ticks: int) -> List[SongTempo]:
    result = [
        tempo.copy(update={"position": tempo.position - skip_ticks})
        for tempo in tempo_list
        if tempo.position >= skip_ticks
    ]
    if len(result) and result[0].position <= 0:
        return result
    i = find_last_index(tempo_list, lambda tempo: tempo.position <= skip_ticks)
    result.insert(0, tempo_list[i].copy(update={"position": 0}))
    return result


def skip_beat_list(
    beat_list: List[TimeSignature], skip_bars: int
) -> List[TimeSignature]:
    result = [
        beat.copy(update={"bar_index": beat.bar_index - skip_bars})
        for beat in beat_list
        if beat.bar_index >= skip_bars
    ]
    if not result or result[0].bar_index > 0:
        result.insert(0, beat_list[0].copy(update={"bar_index": 0}))
    return result


def shift_tempo_list(tempo_list: List[SongTempo], shift_ticks: int) -> List[SongTempo]:
    result = tempo_list[:1]
    result.extend(
        [
            tempo.copy(update={"position": tempo.position + shift_ticks})
            for tempo in tempo_list[1:]
        ]
    )
    return result


def shift_beat_list(
    beat_list: List[TimeSignature], shift_bars: int
) -> List[TimeSignature]:
    result = beat_list[:1]
    result.extend(
        [
            beat.copy(update={"bar_index": beat.bar_index + shift_bars})
            for beat in beat_list[1:]
        ]
    )
    return result
