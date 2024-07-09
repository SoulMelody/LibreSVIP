import math
from typing import Optional

from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import Note
from libresvip.model.point import Point
from libresvip.utils.music_math import clamp

from .model import UtauNoteVibrato


def append_utau_note_vibrato(
    note_values: list[Point],
    vibrato_params: Optional[UtauNoteVibrato],
    note_start: Note,
    tick_time_transformer: TimeSynchronizer,
    sample_interval_tick: int,
) -> list[Point]:
    if vibrato_params is None:
        return note_values

    # x-axis: milliSec, y-axis: 100cents
    note_length = (
        tick_time_transformer.get_duration_secs_from_ticks(
            start_ticks=note_start.start_pos,
            end_ticks=note_start.end_pos,
        )
        * 1000
    )
    vibrato_length = note_length * vibrato_params.length / 100
    if vibrato_length <= 0:
        return note_values
    frequency: float = 1.0 / vibrato_params.period
    if not math.isfinite(frequency):
        return note_values
    depth = vibrato_params.depth / 100
    if depth <= 0:
        return note_values
    ease_in_length = note_length * vibrato_params.fade_in / 100
    ease_out_length = note_length * vibrato_params.fade_out / 100
    phase = vibrato_params.phase_shift / 100
    shift = vibrato_params.shift / 100

    start = note_length - vibrato_length

    def vibrato(t: float) -> float:
        if t < start:
            return 0.0
        ease_in_factor = clamp((t - start) / ease_in_length, 0.0, 1.0) if ease_in_length else 1.0
        ease_out_factor = (
            clamp((note_length - t) / ease_out_length, 0.0, 1.0) if ease_out_length else 1.0
        )
        x = math.tau * (frequency * (t - start) - phase)
        return depth * ease_in_factor * ease_out_factor * (math.sin(x) + shift) * 100

    note_start_in_millis = (
        tick_time_transformer.get_actual_secs_from_ticks(note_start.start_pos) * 1000
    )

    # get approximate interval for interpolation
    sample_interval_in_millis = (
        tick_time_transformer.get_duration_secs_from_ticks(
            start_ticks=note_start.start_pos,
            end_ticks=note_start.start_pos + sample_interval_tick,
        )
        * 1000
    )

    interpolated_points = []
    for i in range(len(note_values)):
        x, y = note_values[i]
        x_in_millis = (
            tick_time_transformer.get_actual_secs_from_ticks(x) * 1000
        ) - note_start_in_millis
        interpolated_points.append((x_in_millis, y + vibrato(x_in_millis)))
        if i < len(note_values) - 1:
            next_x, _ = note_values[i + 1]
            pos = x_in_millis + sample_interval_in_millis
            while pos < (
                (tick_time_transformer.get_actual_secs_from_ticks(next_x) * 1000)
                - note_start_in_millis
            ):
                interpolated_points.append((pos, y + vibrato(pos)))
                pos += sample_interval_in_millis

    return [
        Point(
            round(
                tick_time_transformer.get_actual_ticks_from_secs((x + note_start_in_millis) / 1000)
            ),
            round(y),
        )
        for x, y in interpolated_points
    ]
