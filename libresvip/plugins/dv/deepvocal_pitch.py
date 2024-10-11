from __future__ import annotations

import dataclasses
import operator
from functools import singledispatch
from itertools import groupby
from typing import Optional, SupportsFloat

from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import Note, ParamCurve, SongTempo
from libresvip.model.point import Point
from libresvip.utils.music_math import (
    interpolate_cosine_ease_in_out,
    interpolate_linear,
)

from .constants import (
    BEND_DOWN_LENGTH_FIXED_SEC,
    BEND_LENGTH_MAX_SEC,
    BEND_LENGTH_MIN_SEC,
    BEND_VALUE_MAX,
    NOTE_KEY_SUM,
    PORTAMENTO_LENGTH_MAX_SEC,
    SAMPLING_INTERVAL_TICK,
)
from .model import DvPoint


@dataclasses.dataclass
class DvSegmentPitchRawData:
    tick_offset: int  # only for import
    data: list[DvPoint]  # (tick, DV style cent)


@dataclasses.dataclass
class DvNoteWithPitch:
    note: Note
    por_head: int  # 0~100
    por_tail: int  # 0~100
    ben_len: int  # 0~100
    ben_dep: int  # 0~100
    vibrato: list[DvPoint]  # (ms, minus cent)


def merge_points_from_segments(
    segments: list[DvSegmentPitchRawData],
) -> Optional[list[Point]]:
    points = []
    for segment in segments:
        for dv_point in segment.data:
            if (raw_tick := dv_point.x) >= 0:
                tick = raw_tick + segment.tick_offset
                if dv_point.y >= 0:
                    value = round(convert_note_key(dv_point.y / 100) * 100)
                    points.append(Point(x=tick, y=value))
                else:
                    points.append(Point(x=tick, y=-100))
    return points or None


def merge_same_tick_points(points: list[Point]) -> Optional[list[Point]]:
    merged_points = []
    for tick, group in groupby(iter(points), key=operator.attrgetter("x")):
        group_list = list(group)
        if len(group_list) > 1:
            if any(point.y == -100 for point in group_list):
                merged_points.append(Point(x=tick, y=-100))
            else:
                merged_points.append(
                    Point(
                        x=tick,
                        y=round(sum(point.y for point in group_list) / len(group_list)),
                    )
                )
        else:
            merged_points.append(group_list[0])
    return merged_points or None


def merge_same_value_points(points: list[Point]) -> Optional[list[Point]]:
    merged_points = [next(group) for key, group in groupby(points, key=operator.attrgetter("y"))]
    return merged_points or None


def apply_default_pitch(
    first_bar_length: int,
    points: list[Point],
    notes: list[DvNoteWithPitch],
    tempos: list[SongTempo],
) -> list[Point]:
    if not points or not notes:
        return points

    time_synchronizer = TimeSynchronizer(tempos)

    base = get_base_pitch(notes, time_synchronizer)
    bend_diff = get_bend_pitch(notes, time_synchronizer)
    vibrato_diff = get_vibrato_pitch(notes, time_synchronizer)

    result = []
    last_point = None
    for point in points:
        if last_point is not None and last_point.y == -100:
            result.extend(
                Point(
                    x=tick + first_bar_length,
                    y=base.get(tick, 0) + bend_diff.get(tick, 0) + vibrato_diff.get(tick, 0),
                )
                for tick in range(last_point.x + 1, point.x, SAMPLING_INTERVAL_TICK)
            )
            result.append(
                Point(
                    x=(point.x if last_point is None else last_point.x) + first_bar_length,
                    y=-100,
                )
            )
        if point.y != -100:
            result.append(point._replace(x=point.x + first_bar_length))
        else:
            result.append(Point(x=point.x + first_bar_length, y=-100))
        last_point = point
    if not result or result[0].x > notes[-1].note.end_pos:
        result = [
            Point(
                x=tick + first_bar_length,
                y=(base.get(tick, 0) + bend_diff.get(tick, 0) + vibrato_diff.get(tick, 0)),
            )
            for tick in range(0, notes[-1].note.end_pos, SAMPLING_INTERVAL_TICK)
        ] + result
    if result:
        result.insert(0, Point.start_point())
        result.append(Point.end_point())
    return result


def get_base_pitch(notes: list[DvNoteWithPitch], transformer: TimeSynchronizer) -> dict[int, int]:
    result = {}
    for last_note, this_note in zip([None, *notes], [*notes, None]):
        portamento = []
        if last_note is not None and this_note is not None:
            portamento = get_portamento(last_note, transformer, this_note)
            for point in portamento:
                result[point.x] = point.y
        if last_note is not None:
            last_note_tail = [
                (tick, last_note.note.key_number * 100)
                for tick in range(
                    tick_half_start(last_note.note),
                    (portamento[0].x if portamento else last_note.note.end_pos),
                )
            ]
            result |= last_note_tail
        if this_note is not None:
            start = (
                0
                if last_note is None
                else (portamento[-1].x if portamento else this_note.note.start_pos)
            )
            this_note_head = [
                (tick, this_note.note.key_number * 100)
                for tick in range(start, tick_half_start(this_note.note))
            ]
            result.update(this_note_head)
    return result


def get_bend_pitch(notes: list[DvNoteWithPitch], transformer: TimeSynchronizer) -> dict[int, int]:
    result: dict[int, int] = {}
    for note in notes:
        start_tick = note.note.start_pos
        start_sec = transformer.get_actual_secs_from_ticks(start_tick)
        valley_sec = start_sec + BEND_DOWN_LENGTH_FIXED_SEC
        valley_tick = min(
            transformer.get_actual_ticks_from_secs(valley_sec),
            note.note.start_pos + note.note.length // 2 - 1,
        )

        if note.ben_len <= 50:
            length_sec = BEND_LENGTH_MIN_SEC
        else:
            length_sec = (BEND_LENGTH_MAX_SEC - BEND_LENGTH_MIN_SEC) * (
                note.ben_len - 50
            ) // 50 + BEND_LENGTH_MIN_SEC
        end_sec = start_sec + length_sec
        end_tick = min(
            transformer.get_actual_ticks_from_secs(end_sec),
            note.note.start_pos - 1,
        )

        valley_value = -BEND_VALUE_MAX * note.ben_dep
        valley_point = Point(x=round(valley_tick), y=round(valley_value))

        bend_down = interpolate_linear([Point(x=start_tick, y=0), valley_point], 1) or []

        bend_up = (
            interpolate_cosine_ease_in_out([valley_point, Point(x=round(end_tick), y=0)], 1)[1:]
            or []
        )

        result |= dict(bend_down + bend_up)
    return result


def get_portamento(
    last_note: DvNoteWithPitch,
    transformer: TimeSynchronizer,
    this_note: DvNoteWithPitch,
) -> list[Point]:
    tail_length_sec = PORTAMENTO_LENGTH_MAX_SEC * last_note.por_tail // 100
    start_sec = transformer.get_actual_secs_from_ticks(last_note.note.end_pos) - tail_length_sec
    start_tick = max(
        transformer.get_actual_ticks_from_secs(start_sec),
        tick_half_start(last_note.note),
    )

    head_length_sec = PORTAMENTO_LENGTH_MAX_SEC * this_note.por_head // 100
    end_sec = transformer.get_actual_secs_from_ticks(this_note.note.start_pos) + head_length_sec
    end_tick = min(
        transformer.get_actual_ticks_from_secs(end_sec),
        tick_half_start(this_note.note) - 1,
    )

    return (
        interpolate_cosine_ease_in_out(
            [
                Point(round(start_tick), last_note.note.key_number * 100),
                Point(round(end_tick), this_note.note.key_number * 100),
            ],
            1,
        )
        or []
    )


def get_vibrato_pitch(
    notes: list[DvNoteWithPitch], transformer: TimeSynchronizer
) -> dict[int, int]:
    result: dict[int, int] = {}
    for note in notes:
        start_tick = note.note.start_pos
        start_sec = transformer.get_actual_secs_from_ticks(start_tick)
        vibrato_points = [
            Point(
                x=round(transformer.get_actual_ticks_from_secs(start_sec + vib_point.x / 1000)),
                y=-vib_point.y,
            )
            for vib_point in note.vibrato
            if start_tick
            <= transformer.get_actual_ticks_from_secs(start_sec + vib_point.x / 1000)
            < note.note.end_pos
        ]
        result |= dict(interpolate_linear(vibrato_points, 1) or [])
    return result


def tick_half_start(note: Note) -> int:
    return (note.start_pos + note.end_pos) // 2


@singledispatch
def convert_note_key(key: SupportsFloat) -> float:
    raise NotImplementedError


@convert_note_key.register(int)
def _convert_note_key_int(key: int) -> int:
    return int(NOTE_KEY_SUM) - key


@convert_note_key.register(float)
def _convert_note_key_float(key: float) -> float:
    return NOTE_KEY_SUM - key


def pitch_from_dv_track(
    first_bar_length: int,
    segments: list[DvSegmentPitchRawData],
    notes: list[DvNoteWithPitch],
    tempos: list[SongTempo],
) -> Optional[ParamCurve]:
    merged_points = merge_points_from_segments(segments)
    if merged_points is None:
        return None
    merged_points = merge_same_tick_points(merged_points)
    if merged_points is None:
        return None
    merged_points = merge_same_value_points(merged_points)
    if merged_points is None:
        return None
    return ParamCurve(points=apply_default_pitch(first_bar_length, merged_points, notes, tempos))


def generate_for_dv(
    first_bar_length: int, pitch: ParamCurve, notes: list[Note]
) -> Optional[DvSegmentPitchRawData]:
    if not len(pitch.points):
        return None
    data = [DvPoint(x=-1, y=-1)]
    last_value = None
    for point in pitch.points.root:
        if (last_value is None and point.y != -100) or point.y == -100:
            data.append(DvPoint(x=point.x - first_bar_length, y=-1))
        if point.y != -100:
            data.append(
                DvPoint(
                    x=point.x - first_bar_length,
                    y=round(convert_note_key(point.y / 100) * 100),
                )
            )
        last_value = point.y
    data.append(DvPoint(x=data[-1].x + 1 if len(data) > 1 else 307201, y=-1))
    return DvSegmentPitchRawData(0, data)
