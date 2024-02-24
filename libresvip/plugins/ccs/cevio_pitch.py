from __future__ import annotations

import dataclasses
import itertools
import math
import warnings
from typing import NamedTuple, Optional

import more_itertools

from libresvip.core.tick_counter import shift_tempo_list
from libresvip.core.warning_types import ParamsWarning
from libresvip.model.base import ParamCurve, Points, SongTempo
from libresvip.model.point import Point
from libresvip.utils.music_math import hz2midi, midi2hz
from libresvip.utils.search import find_last_index
from libresvip.utils.translation import gettext_lazy as _

from .constants import (
    MIN_DATA_LENGTH,
    TEMP_VALUE_AS_NULL,
    TIME_UNIT_AS_TICKS_PER_BPM,
)


class CeVIOParamEvent(NamedTuple):
    idx: Optional[int]
    repeat: Optional[int]
    value: float


class CeVIOParamEventFloat(NamedTuple):
    idx: Optional[float]
    repeat: Optional[float]
    value: Optional[float]

    @classmethod
    def from_event(cls, event: CeVIOParamEvent) -> CeVIOParamEventFloat:
        return cls(
            float(event.idx) if event.idx is not None else None,
            float(event.repeat) if event.repeat is not None else None,
            event.value,
        )


@dataclasses.dataclass
class CeVIOTrackPitchData:
    events: list[CeVIOParamEvent]
    tempos: list[SongTempo]
    tick_prefix: int
    vibrato_amplitude_events: list[CeVIOParamEvent] = dataclasses.field(default_factory=list)
    vibrato_frequency_events: list[CeVIOParamEvent] = dataclasses.field(default_factory=list)

    @property
    def length(self) -> int:
        last_has_index = find_last_index(self.events, lambda event: event.idx is not None)
        length = self.events[last_has_index].idx + sum(
            event.repeat or 1 for event in self.events[last_has_index:]
        )
        return length + MIN_DATA_LENGTH


def pitch_from_cevio_track(data: CeVIOTrackPitchData) -> Optional[ParamCurve]:
    converted_points = [Point.start_point()]
    current_value = -100

    events_normalized = shape_events(
        normalize_to_tick(append_ending_points(data.events), data.tempos, data.tick_prefix)
    )

    next_pos = None
    for event in events_normalized:
        pos = event.idx - data.tick_prefix
        length = event.repeat
        try:
            value = round(hz2midi(math.e**event.value) * 100) if event.value is not None else -100
            if value != current_value or next_pos != pos:
                converted_points.append(Point(x=round(pos), y=value))
                if value == -100:
                    converted_points.append(Point(x=round(pos), y=value))
                current_value = value
        except OverflowError:
            warnings.warn(_("Pitch value is out of bounds"), ParamsWarning)
        next_pos = pos + length
    converted_points.append(Point.end_point())

    return ParamCurve(points=Points(root=converted_points)) if len(converted_points) > 2 else None


def append_ending_points(events: list[CeVIOParamEvent]) -> list[CeVIOParamEvent]:
    result = []
    next_pos = None
    for event in events:
        pos = event.idx if event.idx is not None else next_pos
        length = event.repeat if event.repeat is not None else 1
        if next_pos is not None and next_pos < pos:
            result.append(CeVIOParamEvent(next_pos, None, TEMP_VALUE_AS_NULL))
        result.append(CeVIOParamEvent(pos, length, event.value))
        next_pos = pos + length
    if next_pos is not None:
        result.append(CeVIOParamEvent(next_pos, None, TEMP_VALUE_AS_NULL))
    return result


def normalize_to_tick(
    events: list[CeVIOParamEvent], tempo_list: list[SongTempo], tick_prefix: int
) -> list[CeVIOParamEventFloat]:
    tempos = expand(tempo_list, tick_prefix)
    events = [CeVIOParamEventFloat.from_event(event) for event in events]
    events_normalized: list[CeVIOParamEventFloat] = []
    current_tempo_index = 0
    next_pos = 0.0
    next_tick_pos = 0.0
    for event in events:
        pos = event.idx if event.idx is not None else next_pos
        if event.idx is None:
            tick_pos = next_tick_pos
        else:
            while (
                current_tempo_index + 1 < len(tempos)
                and tempos[current_tempo_index + 1][0] <= event.idx
            ):
                current_tempo_index += 1
            ticks_in_time_unit = TIME_UNIT_AS_TICKS_PER_BPM * tempos[current_tempo_index][2]
            tick_pos = (
                tempos[current_tempo_index][1]
                + (event.idx - tempos[current_tempo_index][0]) * ticks_in_time_unit
            )
        repeat = event.repeat if event.repeat is not None else 1.0
        remaining_repeat = repeat
        repeat_in_ticks = 0.0
        while (
            current_tempo_index + 1 < len(tempos)
            and tempos[current_tempo_index + 1][0] < pos + repeat
        ):
            repeat_in_ticks += tempos[current_tempo_index + 1][1] - max(
                tempos[current_tempo_index][1], tick_pos
            )
            remaining_repeat -= tempos[current_tempo_index + 1][0] - max(
                tempos[current_tempo_index][0], pos
            )
            current_tempo_index += 1
        repeat_in_ticks += (
            remaining_repeat * TIME_UNIT_AS_TICKS_PER_BPM * tempos[current_tempo_index][2]
        )
        next_pos = pos + repeat
        next_tick_pos = tick_pos + repeat_in_ticks
        events_normalized.append(CeVIOParamEventFloat(tick_pos, repeat_in_ticks, event.value))
    return [
        CeVIOParamEventFloat(
            tick.idx + tick_prefix,
            tick.repeat,
            tick.value if tick.value != TEMP_VALUE_AS_NULL else None,
        )
        for tick in events_normalized
    ]


def shape_events(
    events_with_full_params: list[CeVIOParamEventFloat],
) -> list[CeVIOParamEventFloat]:
    result: list[CeVIOParamEventFloat] = []
    for event in events_with_full_params:
        if event.repeat is not None and event.repeat > 0:
            if result:
                last = result[-1]
                if last.idx == event.idx:
                    result[-1] = event
                else:
                    result.append(event)
            else:
                result.append(event)
    return result


def expand(tempos: list[SongTempo], tick_prefix: int) -> list[tuple[int, int, float]]:
    result: list[tuple[int, int, float]] = []
    for i, tempo in enumerate(tempos):
        if i == 0:
            result.append((0, tick_prefix, tempo.bpm))
        else:
            last_pos, last_tick_pos, last_bpm = result[-1]
            ticks_in_time_unit = TIME_UNIT_AS_TICKS_PER_BPM * last_bpm
            new_pos = last_pos + (tempo.position - last_tick_pos) / ticks_in_time_unit
            result.append((int(new_pos), tempo.position, tempo.bpm))
    return result


def generate_for_cevio(
    pitch: ParamCurve, tempos: list[SongTempo], tick_prefix: int
) -> Optional[CeVIOTrackPitchData]:
    events_with_full_params = []
    for i, this_point in enumerate(pitch.points.root):
        next_point = pitch.points[i + 1] if i + 1 < len(pitch.points) else None
        end_tick = next_point.x - tick_prefix if next_point else None
        index = this_point.x - tick_prefix
        repeat = end_tick - index if end_tick else 1
        repeat = max(repeat, 1)
        value = math.log(midi2hz(this_point.y / 100)) if this_point.y != -100 else None
        if value is not None:
            events_with_full_params.append(
                CeVIOParamEventFloat(float(index), float(repeat), float(value))
            )
    are_events_connected_to_next = [
        this_event.idx + this_event.repeat >= next_event.idx if next_event else False
        for this_event, next_event in zip(
            events_with_full_params, events_with_full_params[1:] + [None]
        )
    ]
    events = denormalize_from_tick(events_with_full_params, tempos, tick_prefix)
    events = restore_connection(events, are_events_connected_to_next)
    events = merge_events_if_possible(events)
    events = remove_redundant_index(events)
    events = remove_redundant_repeat(events)
    if not events:
        return None
    last_event_with_index = next(
        (event for event in reversed(events) if event.idx is not None), None
    )
    if last_event_with_index is not None:
        length = last_event_with_index.idx
        for event in events[events.index(last_event_with_index) :]:
            length += event.repeat or 1
    return CeVIOTrackPitchData(events, [], tick_prefix)


def denormalize_from_tick(
    events_with_full_params: list[CeVIOParamEventFloat],
    tempos_in_ticks: list[SongTempo],
    tick_prefix: int,
) -> list[CeVIOParamEvent]:
    tempos = expand(
        shift_tempo_list(tempos_in_ticks, tick_prefix),
        tick_prefix,
    )
    events_with_full_params = [
        event if event.idx is None else event._replace(idx=event.idx + tick_prefix)
        for event in events_with_full_params
    ]
    events = []
    current_tempo_index = 0
    for event_double in events_with_full_params:
        if event_double.idx is not None:
            tick_pos = event_double.idx
        while (
            current_tempo_index + 1 < len(tempos) and tempos[current_tempo_index + 1][1] < tick_pos
        ):
            current_tempo_index += 1
        ticks_per_time_unit = tempos[current_tempo_index][2] * TIME_UNIT_AS_TICKS_PER_BPM
        pos = (
            tempos[current_tempo_index][0]
            + (event_double.idx - tempos[current_tempo_index][1]) / ticks_per_time_unit
        )
        repeat_in_ticks = event_double.repeat
        repeat = 0.0
        while (current_tempo_index + 1 < len(tempos)) and (
            tempos[current_tempo_index + 1][1] < tick_pos + repeat_in_ticks
        ):
            repeat += tempos[current_tempo_index + 1][0] - max(tempos[current_tempo_index][0], pos)
            repeat_in_ticks -= tempos[current_tempo_index + 1][1] - max(
                tempos[current_tempo_index][1], tick_pos
            )
            current_tempo_index += 1
        repeat += repeat_in_ticks / (TIME_UNIT_AS_TICKS_PER_BPM * tempos[current_tempo_index][2])
        events.append(
            CeVIOParamEvent(round(pos), int(round(max(repeat, 1))), event_double.value or 0)
        )
    return events


def restore_connection(
    events: list[CeVIOParamEvent], are_events_connected_to_next: list[bool]
) -> list[CeVIOParamEvent]:
    new_events = []
    for (prev_event, next_event), is_connected_to_next in zip(
        more_itertools.windowed(itertools.chain(events, [None]), 2), are_events_connected_to_next
    ):
        if next_event is None:
            new_events.append(prev_event)
            continue
        if not is_connected_to_next:
            new_events.append(prev_event)
        else:
            new_events.append(prev_event._replace(repeat=next_event.idx - prev_event.idx))
    return new_events


def merge_events_if_possible(events: list[CeVIOParamEvent]) -> list[CeVIOParamEvent]:
    new_events = []
    for event, next_event in more_itertools.windowed(itertools.chain(events, [None]), 2):
        if (
            next_event
            and event.value == next_event.value
            and event.idx + event.repeat == next_event.idx
        ):
            new_events.append(
                CeVIOParamEvent(event.idx, event.repeat + next_event.repeat, event.value)
            )
        else:
            new_events.append(event)
    return new_events


def remove_redundant_index(events: list[CeVIOParamEvent]) -> list[CeVIOParamEvent]:
    new_events = []
    for prev_event, event in more_itertools.windowed(more_itertools.prepend(None, events), 2):
        if (
            prev_event is not None
            and prev_event.idx is not None
            and prev_event.repeat is not None
            and prev_event.idx + prev_event.repeat == event.idx
        ):
            new_events.append(CeVIOParamEvent(None, event.repeat, event.value))
        else:
            new_events.append(event)
    return new_events


def remove_redundant_repeat(events: list[CeVIOParamEvent]) -> list[CeVIOParamEvent]:
    return [event if event.repeat != 1 else event._replace(repeat=None) for event in events]
