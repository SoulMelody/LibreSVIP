from __future__ import annotations

import dataclasses
import math
from typing import NamedTuple, Optional

import more_itertools

from libresvip.model.base import ParamCurve, Point, Points, SongTempo
from libresvip.utils import hz2midi, midi2hz

from .constants import (
    TEMP_VALUE_AS_NULL,
    TICK_RATE,
    TIME_UNIT_AS_TICKS_PER_BPM,
)


class CeVIOPitchEvent(NamedTuple):
    index: Optional[int]
    repeat: Optional[int]
    value: float


class CeVIOPitchEventFloat(NamedTuple):
    index: Optional[float]
    repeat: Optional[float]
    value: Optional[float]

    @classmethod
    def from_event(cls, event: CeVIOPitchEvent) -> CeVIOPitchEventFloat:
        return cls(float(event.index) if event.index is not None else None,
                   float(event.repeat) if event.repeat is not None else None,
                   event.value)


@dataclasses.dataclass
class CeVIOTrackPitchData:
    events: list[CeVIOPitchEvent]
    tempos: list[SongTempo]
    tick_prefix: int

def pitch_from_cevio_track(data: CeVIOTrackPitchData) -> Optional[ParamCurve]:
    converted_points = [
        Point.start_point()
    ]
    current_value = -100

    events_normalized = shape_events(normalize_to_tick(append_ending_points(data)))

    next_pos = None
    for event in events_normalized:
        pos = event.index + data.tick_prefix
        length = event.repeat
        value = round(hz2midi(math.e ** event.value) * 100) if event.value is not None else -100
        if value != current_value or next_pos != pos:
            converted_points.append(Point(x=round(pos), y=value))
            if value == -100:
                converted_points.append(Point(x=round(pos), y=value))
            current_value = value
        next_pos = pos + length
    converted_points.append(Point.end_point())

    return ParamCurve(points=Points(root=converted_points)) if len(converted_points) > 2 else None

def append_ending_points(data: CeVIOTrackPitchData) -> CeVIOTrackPitchData:
    result = []
    next_pos = None
    for event in data.events:
        pos = event.index if event.index is not None else next_pos
        length = event.repeat if event.repeat is not None else 1
        if next_pos is not None and next_pos < pos:
            result.append(CeVIOPitchEvent(next_pos, None, TEMP_VALUE_AS_NULL))
        result.append(CeVIOPitchEvent(pos, length, event.value))
        next_pos = pos + length
    if next_pos is not None:
        result.append(CeVIOPitchEvent(next_pos, None, TEMP_VALUE_AS_NULL))
    return CeVIOTrackPitchData(result, data.tempos, data.tick_prefix)

def normalize_to_tick(data: CeVIOTrackPitchData) -> list[CeVIOPitchEventFloat]:
    tempos = expand(data.tempos, data.tick_prefix)
    events = [CeVIOPitchEventFloat.from_event(event) for event in data.events]
    events_normalized: list[CeVIOPitchEventFloat] = []
    current_tempo_index = 0
    next_pos = 0.0
    next_tick_pos = 0.0
    for event in events:
        pos = event.index if event.index is not None else next_pos
        tick_pos = next_tick_pos if event.index is None else None
        if event.index is not None:
            while current_tempo_index + 1 < len(tempos) and tempos[current_tempo_index + 1][0] <= event.index:
                current_tempo_index += 1
            ticks_in_time_unit = TIME_UNIT_AS_TICKS_PER_BPM * tempos[current_tempo_index][2]
            tick_pos = tempos[current_tempo_index][1] + (event.index - tempos[current_tempo_index][0]) * ticks_in_time_unit
        repeat = event.repeat if event.repeat is not None else 1.0
        remaining_repeat = repeat
        repeat_in_ticks = 0.0
        while current_tempo_index + 1 < len(tempos) and tempos[current_tempo_index + 1][0] < pos + repeat:
            repeat_in_ticks += tempos[current_tempo_index + 1][1] - max(tempos[current_tempo_index][1], tick_pos)
            remaining_repeat -= tempos[current_tempo_index + 1][0] - max(tempos[current_tempo_index][0], pos)
            current_tempo_index += 1
        repeat_in_ticks += remaining_repeat * TIME_UNIT_AS_TICKS_PER_BPM * tempos[current_tempo_index][2]
        next_pos = pos + repeat
        next_tick_pos = tick_pos + repeat_in_ticks
        events_normalized.append(CeVIOPitchEventFloat(tick_pos, repeat_in_ticks, event.value))
    return [CeVIOPitchEventFloat(tick.index, tick.repeat, tick.value if tick.value != TEMP_VALUE_AS_NULL else None) for tick in events_normalized]

def shape_events(events_with_full_params: list[CeVIOPitchEventFloat]) -> list[CeVIOPitchEventFloat]:
    result: list[CeVIOPitchEventFloat] = []
    for event in events_with_full_params:
        if event.repeat is not None and event.repeat > 0:
            if result:
                last = result[-1]
                if last.index == event.index:
                    result[-1] = event
                else:
                    result.append(event)
            else:
                result.append(event)
    return result

def expand(tempos: list[SongTempo], tick_prefix: int) -> list[tuple[int, float, float]]:
    result: list[tuple[int, float, float]] = []
    for i, tempo in enumerate(tempos):
        if i == 0:
            result.append((0, tick_prefix, tempo.bpm))
        else:
            last_pos, last_tick_pos, last_bpm = result[-1]
            ticks_in_time_unit = TIME_UNIT_AS_TICKS_PER_BPM * last_bpm
            new_pos = last_pos + (tempo.position - last_tick_pos) / ticks_in_time_unit
            result.append((new_pos, tempo.position, tempo.bpm))
    return result

def generate_for_cevio(pitch: ParamCurve, tick_prefix: int) -> Optional[list[CeVIOPitchEvent]]:
    events = []
    has_index = False
    for point, next_point in more_itertools.pairwise(pitch.points.root):
        if point.y != -100:
            event = CeVIOPitchEvent(
                index=round(
                    (point.x - tick_prefix) * TICK_RATE
                ) if has_index else None, repeat=None, value=math.log(midi2hz(point.y / 100)))
            events.append(event)
        has_index = point.y == -100 and next_point.y != -100
    return events or None
