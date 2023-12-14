from __future__ import annotations

import dataclasses
import math
from typing import NamedTuple, Optional

from libresvip.model.base import ParamCurve, Points, SongTempo
from libresvip.model.point import Point
from libresvip.utils import hz2midi, midi2hz

from .constants import (
    MIN_DATA_LENGTH,
    TEMP_VALUE_AS_NULL,
    TIME_UNIT_AS_TICKS_PER_BPM,
)


class VoiSonaPitchEvent(NamedTuple):
    index: Optional[int]
    repeat: Optional[int]
    value: float


class VoiSonaPitchEventFloat(NamedTuple):
    index: Optional[float]
    repeat: Optional[float]
    value: Optional[float]

    @classmethod
    def from_event(cls, event: VoiSonaPitchEvent) -> VoiSonaPitchEventFloat:
        return cls(
            float(event.index) if event.index is not None else None,
            float(event.repeat) if event.repeat is not None else None,
            event.value,
        )


@dataclasses.dataclass
class VoiSonaTrackPitchData:
    events: list[VoiSonaPitchEvent]
    tempos: list[SongTempo]
    tick_prefix: int

    @property
    def length(self) -> int:
        last_event_with_index = next(
            (event for event in reversed(self.events) if event.index is not None), None
        )
        length = last_event_with_index.index
        for event in self.events[self.events.index(last_event_with_index) :]:
            length += event.repeat or 1
        return length + MIN_DATA_LENGTH


def pitch_from_voisona_track(data: VoiSonaTrackPitchData) -> Optional[ParamCurve]:
    converted_points = [Point.start_point()]
    current_value = -100

    events_normalized = shape_events(normalize_to_tick(append_ending_points(data)))

    next_pos = None
    for event in events_normalized:
        pos = event.index - data.tick_prefix
        length = event.repeat
        value = (
            round(hz2midi(math.e**event.value) * 100)
            if event.value is not None
            else -100
        )
        if value != current_value or next_pos != pos:
            converted_points.append(Point(x=round(pos), y=value))
            if value == -100:
                converted_points.append(Point(x=round(pos), y=value))
            current_value = value
        next_pos = pos + length
    converted_points.append(Point.end_point())

    return (
        ParamCurve(points=Points(root=converted_points))
        if len(converted_points) > 2
        else None
    )


def append_ending_points(data: VoiSonaTrackPitchData) -> VoiSonaTrackPitchData:
    result = []
    next_pos = None
    for event in data.events:
        pos = event.index if event.index is not None else next_pos
        length = event.repeat if event.repeat is not None else 1
        if next_pos is not None and next_pos < pos:
            result.append(VoiSonaPitchEvent(next_pos, None, TEMP_VALUE_AS_NULL))
        result.append(VoiSonaPitchEvent(pos, length, event.value))
        next_pos = pos + length
    if next_pos is not None:
        result.append(VoiSonaPitchEvent(next_pos, None, TEMP_VALUE_AS_NULL))
    return VoiSonaTrackPitchData(result, data.tempos, data.tick_prefix)


def normalize_to_tick(data: VoiSonaTrackPitchData) -> list[VoiSonaPitchEventFloat]:
    tempos = expand(data.tempos, data.tick_prefix)
    events = [VoiSonaPitchEventFloat.from_event(event) for event in data.events]
    events_normalized: list[VoiSonaPitchEventFloat] = []
    current_tempo_index = 0
    next_pos = 0.0
    next_tick_pos = 0.0
    for event in events:
        pos = event.index if event.index is not None else next_pos
        tick_pos = next_tick_pos if event.index is None else None
        if event.index is not None:
            while (
                current_tempo_index + 1 < len(tempos)
                and tempos[current_tempo_index + 1][0] <= event.index
            ):
                current_tempo_index += 1
            ticks_in_time_unit = (
                TIME_UNIT_AS_TICKS_PER_BPM * tempos[current_tempo_index][2]
            )
            tick_pos = (
                tempos[current_tempo_index][1]
                + (event.index - tempos[current_tempo_index][0]) * ticks_in_time_unit
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
            remaining_repeat
            * TIME_UNIT_AS_TICKS_PER_BPM
            * tempos[current_tempo_index][2]
        )
        next_pos = pos + repeat
        next_tick_pos = tick_pos + repeat_in_ticks
        events_normalized.append(
            VoiSonaPitchEventFloat(tick_pos, repeat_in_ticks, event.value)
        )
    return [
        VoiSonaPitchEventFloat(
            tick.index + data.tick_prefix,
            tick.repeat,
            tick.value if tick.value != TEMP_VALUE_AS_NULL else None,
        )
        for tick in events_normalized
    ]


def shape_events(
    events_with_full_params: list[VoiSonaPitchEventFloat],
) -> list[VoiSonaPitchEventFloat]:
    result: list[VoiSonaPitchEventFloat] = []
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


def generate_for_voisona(
    pitch: ParamCurve, tempos: list[SongTempo], tick_prefix: int
) -> Optional[VoiSonaTrackPitchData]:
    events_with_full_params = []
    for i, this_point in enumerate(pitch.points):
        next_point = pitch.points[i + 1] if i + 1 < len(pitch.points) else None
        end_tick = next_point.x if next_point else None
        index = this_point.x
        repeat = end_tick - index if end_tick else 1
        repeat = max(repeat, 1)
        value = math.log(midi2hz(this_point.y / 100)) if this_point.y != -100 else None
        if value is not None:
            events_with_full_params.append(
                VoiSonaPitchEventFloat(float(index), float(repeat), float(value))
            )
    are_events_connected_to_next = [
        this_event.index + this_event.repeat >= next_event.index
        if next_event
        else False
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
        (event for event in reversed(events) if event.index is not None), None
    )
    if last_event_with_index is not None:
        length = last_event_with_index.index
        for event in events[events.index(last_event_with_index) :]:
            length += event.repeat or 1
    return VoiSonaTrackPitchData(events, [], tick_prefix)


def denormalize_from_tick(
    events_with_full_params: list[VoiSonaPitchEventFloat],
    tempos_in_ticks: list[SongTempo],
    tick_prefix: int,
) -> list[VoiSonaPitchEvent]:
    tempos = expand(
        [
            tempo.model_copy(update={"position": tempo.position + tick_prefix})
            for tempo in tempos_in_ticks
        ],
        tick_prefix,
    )
    events_with_full_params = [
        event
        if event.index is None
        else event._replace(index=event.index + tick_prefix)
        for event in events_with_full_params
    ]
    events = []
    current_tempo_index = 0
    for event_double in events_with_full_params:
        if event_double.index is not None:
            tick_pos = event_double.index
        while (
            current_tempo_index + 1 < len(tempos)
            and tempos[current_tempo_index + 1][1] < tick_pos
        ):
            current_tempo_index += 1
        ticks_per_time_unit = (
            tempos[current_tempo_index][2] * TIME_UNIT_AS_TICKS_PER_BPM
        )
        pos = (
            tempos[current_tempo_index][0]
            + (event_double.index - tempos[current_tempo_index][1])
            / ticks_per_time_unit
        )
        repeat_in_ticks = event_double.repeat
        remaining_repeat_in_ticks = repeat_in_ticks
        repeat = 0.0
        while (current_tempo_index + 1 < len(tempos)) and (
            tempos[current_tempo_index + 1][1] < tick_pos + repeat_in_ticks
        ):
            repeat += tempos[current_tempo_index + 1][0] - max(
                tempos[current_tempo_index][0], pos
            )
            remaining_repeat_in_ticks -= tempos[current_tempo_index + 1][1] - max(
                tempos[current_tempo_index][1], tick_pos
            )
            current_tempo_index += 1
        repeat += remaining_repeat_in_ticks / (
            TIME_UNIT_AS_TICKS_PER_BPM * tempos[current_tempo_index][2]
        )
        events.append(
            VoiSonaPitchEvent(round(pos), int(round(repeat)), event_double.value)
        )
    return events


def restore_connection(
    events: list[VoiSonaPitchEvent], are_events_connected_to_next: list[bool]
) -> list[VoiSonaPitchEvent]:
    new_events = []
    for event, is_connected_to_next in zip(events, are_events_connected_to_next):
        new_events.append(event)
        if not is_connected_to_next:
            new_events.append(
                VoiSonaPitchEvent(event.index + event.repeat, 0, event.value)
            )
    return new_events


def merge_events_if_possible(
    events: list[VoiSonaPitchEvent],
) -> list[VoiSonaPitchEvent]:
    new_events = []
    for event, next_event in zip(events, events[1:] + [None]):
        if (
            next_event
            and event.value == next_event.value
            and event.index + event.repeat == next_event.index
        ):
            new_events.append(
                VoiSonaPitchEvent(
                    event.index, event.repeat + next_event.repeat, event.value
                )
            )
        else:
            new_events.append(event)
    return new_events


def remove_redundant_index(events: list[VoiSonaPitchEvent]) -> list[VoiSonaPitchEvent]:
    new_events = []
    for prev_event, event in zip([None] + events[:-1], events):
        if (
            prev_event is not None
            and prev_event.index is not None
            and prev_event.repeat is not None
            and prev_event.index + prev_event.repeat == event.index
        ):
            new_events.append(VoiSonaPitchEvent(None, event.repeat, event.value))
        else:
            new_events.append(event)
    return new_events


def remove_redundant_repeat(events: list[VoiSonaPitchEvent]) -> list[VoiSonaPitchEvent]:
    return [
        event if event.repeat != 1 else event._replace(repeat=None) for event in events
    ]
