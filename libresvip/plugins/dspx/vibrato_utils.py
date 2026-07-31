from __future__ import annotations

import bisect
import math
from dataclasses import dataclass

from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import ParamCurve, Points, VibratoParam
from libresvip.model.point import Point
from libresvip.utils.music_math import clamp

from .model_v1 import ControlPoint, Note, Vibrato, VibratoPoints

VIBRATO_POSITION_SCALE = 100000
VIBRATO_FREQUENCY_SCALE = 100


class ScaleCurve:
    def __init__(self, points: list[ControlPoint]) -> None:
        unique_points: dict[float, ControlPoint] = {}
        for point in sorted(enumerate(points), key=lambda item: (item[1].x, item[0])):
            unique_points[point[1].x] = point[1]
        self.points = sorted(unique_points.values(), key=lambda point: point.x)
        self.positions = [point.x for point in self.points]

    def value_at(self, position: float) -> float:
        if not self.points:
            return 1.0
        if position <= self.points[0].x:
            return self.points[0].y
        if position >= self.points[-1].x:
            return self.points[-1].y
        right_index = bisect.bisect_right(self.positions, position)
        left = self.points[right_index - 1]
        right = self.points[right_index]
        ratio = (position - left.x) / (right.x - left.x)
        return left.y + (right.y - left.y) * ratio

    def integral_from_zero(self, position: float) -> float:
        if not self.points:
            return position
        if position >= 0:
            return self._integrate_forward(0, position)
        return -self._integrate_forward(position, 0)

    def _integrate_forward(self, start: float, end: float) -> float:
        if start >= end:
            return 0.0
        result = 0.0
        cursor = start
        while cursor < end:
            right_index = bisect.bisect_right(self.positions, cursor)
            next_position = (
                min(end, self.positions[right_index])
                if right_index < len(self.positions)
                else end
            )
            if cursor >= next_position:
                cursor = next_position
                continue
            result += (
                self.value_at(cursor) + self.value_at(next_position)
            ) * 0.5 * (next_position - cursor)
            cursor = next_position
        return result


class VibratoCurve:
    def __init__(self, vibrato: Vibrato, note_length_secs: float) -> None:
        self.vibrato = vibrato
        self.note_length_secs = note_length_secs
        self.amplitude = ScaleCurve(vibrato.points.amp)
        self.frequency = ScaleCurve(vibrato.points.freq)

    def evaluate(self, position: float) -> float:
        if position < self.vibrato.start or position > self.vibrato.end:
            return 0.0
        cycles = (
            self.vibrato.freq
            * self.note_length_secs
            * self.frequency.integral_from_zero(position)
        )
        phase = 2 * 3.141592653589793 * (cycles + self.vibrato.phase)
        return (
            self.vibrato.amp * self.amplitude.value_at(position) * math.sin(phase)
            + self.vibrato.offset
        )


@dataclass
class NoteVibrato:
    start_tick: int
    end_tick: int
    start_secs: float
    duration_secs: float
    curve: VibratoCurve


class VibratoSequence:
    def __init__(
        self,
        notes: list[Note],
        *,
        clip_start: int,
        synchronizer: TimeSynchronizer,
    ) -> None:
        self.synchronizer = synchronizer
        self.vibratos: list[NoteVibrato] = []
        for note in notes:
            if note.length <= 0:
                continue
            start_tick = clip_start + note.pos
            end_tick = start_tick + note.length
            start_secs = synchronizer.get_actual_secs_from_ticks(start_tick)
            duration_secs = synchronizer.get_duration_secs_from_ticks(start_tick, end_tick)
            if duration_secs <= 0:
                continue
            self.vibratos.append(
                NoteVibrato(
                    start_tick=start_tick,
                    end_tick=end_tick,
                    start_secs=start_secs,
                    duration_secs=duration_secs,
                    curve=VibratoCurve(note.vibrato, duration_secs),
                )
            )
        self.vibratos.sort(key=lambda note_vibrato: note_vibrato.start_tick)
        self._start_ticks = [note_vibrato.start_tick for note_vibrato in self.vibratos]
        self._active_vibratos: list[NoteVibrato] = []
        self._next_vibrato_index = 0
        self._last_tick: int | None = None

    def evaluate(self, relative_tick: int, clip_start: int) -> float:
        absolute_tick = relative_tick + clip_start
        if self._last_tick is None or absolute_tick < self._last_tick:
            self._next_vibrato_index = bisect.bisect_right(
                self._start_ticks,
                absolute_tick,
            )
            self._active_vibratos = [
                note_vibrato
                for note_vibrato in self.vibratos[: self._next_vibrato_index]
                if note_vibrato.end_tick > absolute_tick
            ]
        else:
            self._active_vibratos = [
                note_vibrato
                for note_vibrato in self._active_vibratos
                if note_vibrato.end_tick > absolute_tick
            ]
            while (
                self._next_vibrato_index < len(self.vibratos)
                and self.vibratos[self._next_vibrato_index].start_tick <= absolute_tick
            ):
                self._active_vibratos.append(
                    self.vibratos[self._next_vibrato_index],
                )
                self._next_vibrato_index += 1
        self._last_tick = absolute_tick
        if not self._active_vibratos:
            return 0.0
        seconds = self.synchronizer.get_actual_secs_from_ticks(absolute_tick)
        result = 0.0
        for note_vibrato in self._active_vibratos:
            position = (seconds - note_vibrato.start_secs) / note_vibrato.duration_secs
            result += note_vibrato.curve.evaluate(position)
        return result


def _actual_curve(
    points: list[ControlPoint],
    *,
    base_value: float,
    value_scale: int,
) -> ParamCurve:
    scale_curve = ScaleCurve(points)
    positions = sorted({0.0, 1.0, *(point.x for point in points)})
    return ParamCurve(
        points=Points(
            root=[
                Point(
                    x=round(position * VIBRATO_POSITION_SCALE),
                    y=round(base_value * scale_curve.value_at(position) * value_scale),
                )
                for position in positions
            ]
        )
    )


def import_vibrato(vibrato: Vibrato) -> VibratoParam:
    return VibratoParam(
        start_percent=vibrato.start,
        end_percent=vibrato.end,
        is_anti_phase=0.25 <= vibrato.phase < 0.75,
        amplitude=_actual_curve(vibrato.points.amp, base_value=vibrato.amp, value_scale=1),
        frequency=_actual_curve(
            vibrato.points.freq,
            base_value=vibrato.freq,
            value_scale=VIBRATO_FREQUENCY_SCALE,
        ),
    )


def _export_control_points(curve: ParamCurve) -> list[ControlPoint]:
    return [
        ControlPoint(
            x=point.x / VIBRATO_POSITION_SCALE,
            y=point.y,
        )
        for point in curve.points.root
        if point.x not in (Point.start_point().x, Point.end_point().x)
        and point.y != -100
    ]


def export_vibrato(vibrato: VibratoParam | None, *, preserve: bool) -> Vibrato:
    if not preserve or vibrato is None:
        return Vibrato(
            start=0,
            end=1,
            amp=0,
            freq=0,
            phase=0,
            offset=0,
            points=VibratoPoints(amp=[], freq=[]),
        )
    amplitude = _export_control_points(vibrato.amplitude)
    frequency = _export_control_points(vibrato.frequency)
    return Vibrato(
        start=clamp(vibrato.start_percent, 0, 1),
        end=clamp(vibrato.end_percent, 0, 1),
        amp=1 if amplitude else 0,
        freq=1 / VIBRATO_FREQUENCY_SCALE if frequency else 0,
        phase=0.5 if vibrato.is_anti_phase else 0,
        offset=0,
        points=VibratoPoints(amp=amplitude, freq=frequency),
    )
