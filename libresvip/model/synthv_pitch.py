import bisect
import dataclasses
import functools
import itertools
import math
from collections.abc import Callable
from typing import NamedTuple

import portion

from libresvip.core.exceptions import ParamsError
from libresvip.core.time_interval import PiecewiseIntervalDict
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.utils.music_math import linear_interpolation
from libresvip.utils.search import find_index

MAX_BREAK = 0.01
PORTAMENTO_HALFWIDTH_RATIO = 0.3
HALFWIDTH_FLOOR_SECS = 1.0 / 256


class NoteStruct(NamedTuple):
    key: int
    start: float
    end: float
    portamento_offset: float
    portamento_left: float
    portamento_right: float
    depth_left: float
    depth_right: float
    vibrato_start: float
    vibrato_left: float
    vibrato_right: float
    vibrato_depth: float
    vibrato_frequency: float
    vibrato_phase: float


class PitchControlPoint(NamedTuple):
    offset: int
    value: float


@dataclasses.dataclass
class PitchControl:
    pos: int
    pitch: float
    type_: str = "curve"
    points: list[PitchControlPoint] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class SigmoidNode:
    start: float = dataclasses.field(init=False)
    end: float = dataclasses.field(init=False)
    center: float = dataclasses.field(init=False)
    key_left: int = dataclasses.field(init=False)
    key_right: int = dataclasses.field(init=False)
    sigmoid: Callable[[float], float] = dataclasses.field(init=False)
    d_sigmoid: Callable[[float], float] = dataclasses.field(init=False)
    _center: dataclasses.InitVar[float]
    _half_left: dataclasses.InitVar[float]
    _half_right: dataclasses.InitVar[float]
    _key_left: dataclasses.InitVar[int]
    _key_right: dataclasses.InitVar[int]

    def __post_init__(
        self,
        _center: float,
        _half_left: float,
        _half_right: float,
        _key_left: int,
        _key_right: int,
    ) -> None:
        self.center = _center
        self.start = _center - _half_left
        self.end = _center + _half_right
        self.key_left = _key_left
        self.key_right = _key_right
        h = (_key_right - _key_left) * 100
        base = _key_left * 100
        k = 3.0 / (_half_left + _half_right)

        def _logistic(x: float) -> float:
            arg = k * (x - self.center)
            if arg >= 10.0:
                return base + h
            if arg <= -10.0:
                return base
            return base + h / (1.0 + math.exp(-arg))

        def _d_logistic(x: float) -> float:
            arg = k * (x - self.center)
            if arg >= 10.0 or arg <= -10.0:
                return 0.0
            e = math.exp(-arg)
            return h * k * e / (1.0 + e) ** 2

        self.sigmoid = _logistic
        self.d_sigmoid = _d_logistic

    def value_at_secs(self, secs: float) -> float:
        return self.sigmoid(secs)

    def slope_at_secs(self, secs: float) -> float:
        return self.d_sigmoid(secs)


@dataclasses.dataclass
class BaseLayerGenerator:
    _note_list: dataclasses.InitVar[list[NoteStruct]]
    note_list: list[NoteStruct] = dataclasses.field(init=False)
    sigmoid_nodes: list[SigmoidNode] = dataclasses.field(default_factory=list)
    _starts: list[float] = dataclasses.field(init=False, default_factory=list)
    _ends: list[float] = dataclasses.field(init=False, default_factory=list)

    def __post_init__(self, _note_list: list[NoteStruct]) -> None:
        self.note_list = _note_list
        if not _note_list:
            return
        for current_note, next_note in itertools.pairwise(self.note_list):
            if current_note.key == next_note.key:
                continue
            if next_note.start - current_note.end > MAX_BREAK:
                continue
            half_left = max(
                next_note.portamento_left * PORTAMENTO_HALFWIDTH_RATIO,
                HALFWIDTH_FLOOR_SECS,
            )
            half_right = max(
                current_note.portamento_right * PORTAMENTO_HALFWIDTH_RATIO,
                HALFWIDTH_FLOOR_SECS,
            )
            mid = (current_note.end + next_note.start) / 2 + next_note.portamento_offset
            self.sigmoid_nodes.append(
                SigmoidNode(
                    _center=mid,
                    _half_left=half_left,
                    _half_right=half_right,
                    _key_left=current_note.key,
                    _key_right=next_note.key,
                )
            )
        self._starts = [node.start for node in self.sigmoid_nodes]
        self._ends = [node.end for node in self.sigmoid_nodes]

    def pitch_at_secs(self, secs: float) -> float:
        if not self.note_list:
            return 0.0
        left_index = bisect.bisect_right(self._ends, secs)
        right_index = bisect.bisect_right(self._starts, secs)
        query_count = right_index - left_index
        if query_count <= 0:
            if self.sigmoid_nodes:
                next_index = bisect.bisect_right(self._starts, secs)
                if next_index == 0:
                    return self.sigmoid_nodes[0].key_left * 100
                if next_index >= len(self.sigmoid_nodes):
                    return self.sigmoid_nodes[-1].key_right * 100
                return self.sigmoid_nodes[next_index - 1].key_right * 100
            on_note_index = find_index(self.note_list, lambda note: note.start <= secs < note.end)
            if on_note_index >= 0:
                return self.note_list[on_note_index].key * 100
            return (
                min(
                    self.note_list,
                    key=lambda note: min(abs(note.start - secs), abs(secs - note.end)),
                ).key
                * 100
            )
        if query_count == 1:
            return self.sigmoid_nodes[left_index].value_at_secs(secs)
        if query_count <= 3:
            first = self.sigmoid_nodes[left_index]
            last = self.sigmoid_nodes[right_index - 1]
            width = first.end - last.start
            bottom = first.value_at_secs(last.start)
            top = last.value_at_secs(first.end)
            diff1 = first.slope_at_secs(last.start)
            diff2 = last.slope_at_secs(first.end)
            x = secs - last.start
            a = (2 * (bottom - top) + (diff1 + diff2) * width) / width**3
            b = (3 * (top - bottom) - 2 * diff1 * width - diff2 * width) / width**2
            return a * x**3 + b * x**2 + diff1 * x + bottom
        msg = "More than three sigmoid nodes overlapped"
        raise ParamsError(msg)

    @staticmethod
    def cubic_bezier(
        width: float, bottom: float, top: float, diff1: float, diff2: float
    ) -> Callable[[float], float]:
        a = (2 * (bottom - top) + (diff1 + diff2) * width) / width**3
        b = (3 * (top - bottom) - 2 * diff1 * width - diff2 * width) / width**2
        c = diff1
        d = bottom
        return lambda x: a * x**3 + b * x**2 + c * x + d


@dataclasses.dataclass
class GaussianNode:
    origin: float
    sigma: float
    depth: float
    start: float = dataclasses.field(init=False)
    end: float = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        self.start = self.origin - 5.0 * self.sigma
        self.end = self.origin + 5.0 * self.sigma

    def value_at_secs(self, secs: float) -> float:
        return self.depth * math.exp(-0.5 * ((secs - self.origin) / self.sigma) ** 2)


def _portamento_sigma(portamento: float) -> float:
    return max(portamento * PORTAMENTO_HALFWIDTH_RATIO, HALFWIDTH_FLOOR_SECS)


@dataclasses.dataclass
class GaussianLayerGenerator:
    _note_list: dataclasses.InitVar[list[NoteStruct]]
    gaussian_nodes: list[GaussianNode] = dataclasses.field(default_factory=list)
    _starts: list[float] = dataclasses.field(init=False, default_factory=list)
    _ends: list[float] = dataclasses.field(init=False, default_factory=list)

    def __post_init__(self, _note_list: list[NoteStruct]) -> None:
        if not _note_list:
            return
        first_note = _note_list[0]
        sigma_first = _portamento_sigma(first_note.portamento_left)
        self.gaussian_nodes.append(
            GaussianNode(
                origin=first_note.start + 1.5 * sigma_first,
                sigma=sigma_first,
                depth=-first_note.depth_left * 100,
            )
        )
        for current_note, next_note in itertools.pairwise(_note_list):
            sigma_l = _portamento_sigma(current_note.portamento_right)
            sigma_r = _portamento_sigma(next_note.portamento_left)
            if next_note.start - current_note.end >= MAX_BREAK:
                self.gaussian_nodes.append(
                    GaussianNode(
                        origin=current_note.end - 1.5 * sigma_l,
                        sigma=sigma_l,
                        depth=-current_note.depth_right * 100,
                    )
                )
                self.gaussian_nodes.append(
                    GaussianNode(
                        origin=next_note.start + 1.5 * sigma_r,
                        sigma=sigma_r,
                        depth=-next_note.depth_left * 100,
                    )
                )
                continue
            center = (current_note.end + next_note.start) / 2 + next_note.portamento_offset
            depth_left = current_note.depth_right * 100
            depth_right = next_note.depth_left * 100
            if next_note.key <= current_note.key:
                depth_right = -depth_right
            else:
                depth_left = -depth_left
            self.gaussian_nodes.append(
                GaussianNode(
                    origin=center - 1.5 * sigma_l,
                    sigma=sigma_l,
                    depth=depth_left,
                )
            )
            self.gaussian_nodes.append(
                GaussianNode(
                    origin=center + 1.5 * sigma_r,
                    sigma=sigma_r,
                    depth=depth_right,
                )
            )
        last_note = _note_list[-1]
        sigma_last = _portamento_sigma(last_note.portamento_right)
        self.gaussian_nodes.append(
            GaussianNode(
                origin=last_note.end - 1.5 * sigma_last,
                sigma=sigma_last,
                depth=-last_note.depth_right * 100,
            )
        )
        self._starts = [node.start for node in self.gaussian_nodes]
        self._ends = [node.end for node in self.gaussian_nodes]

    def pitch_diff_at_secs(self, secs: float) -> float:
        left_index = bisect.bisect_right(self._ends, secs)
        right_index = bisect.bisect_right(self._starts, secs)
        return sum(
            self.gaussian_nodes[index].value_at_secs(secs)
            for index in range(left_index, right_index)
        )


@dataclasses.dataclass
class VibratoNode:
    start: float
    end: float
    fade_left: float
    fade_right: float
    amplitude: float
    frequency: float
    phase: float

    def value_at_secs(self, secs: float) -> float:
        if self.end - self.start >= self.fade_left + self.fade_left:
            if secs < self.start + self.fade_left:
                zoom = (secs - self.start) / self.fade_left
            elif secs > self.end - self.fade_right:
                zoom = (self.end - secs) / self.fade_right
            else:
                zoom = 1.0
        else:
            mid = (self.start * self.fade_right + self.end * self.fade_left) / (
                self.fade_left + self.fade_right
            )
            if secs < mid:
                zoom = (secs - self.start) / self.fade_left
            else:
                zoom = (self.end - secs) / self.fade_right
        return (
            self.amplitude
            * zoom
            * 100.0
            * math.sin(math.tau * self.frequency * (secs - self.start) + self.phase)
        )


@dataclasses.dataclass
class VibratoLayerGenerator:
    _note_list: dataclasses.InitVar[list[NoteStruct]]
    vibrato_nodes: list[VibratoNode] = dataclasses.field(default_factory=list)
    _starts: list[float] = dataclasses.field(init=False, default_factory=list)
    _ends: list[float] = dataclasses.field(init=False, default_factory=list)

    def __post_init__(self, _note_list: list[NoteStruct]) -> None:
        for i in range(len(_note_list)):
            start, end = _note_list[i].start, _note_list[i].end
            if end - start <= _note_list[i].vibrato_start:
                continue
            if i < len(_note_list) - 1 and _note_list[i + 1].start - end < MAX_BREAK:
                end += min(
                    _note_list[i + 1].portamento_offset,
                    min(
                        _note_list[i + 1].vibrato_start,
                        _note_list[i + 1].end - _note_list[i + 1].start,
                    ),
                )
            if start >= end:
                continue
            self.vibrato_nodes.append(
                VibratoNode(
                    start=start + _note_list[i].vibrato_start,
                    end=end,
                    fade_left=_note_list[i].vibrato_left,
                    fade_right=_note_list[i].vibrato_right,
                    amplitude=_note_list[i].vibrato_depth / 2,
                    frequency=_note_list[i].vibrato_frequency,
                    phase=_note_list[i].vibrato_phase,
                )
            )
        self._starts = [node.start for node in self.vibrato_nodes]
        self._ends = [node.end for node in self.vibrato_nodes]

    def pitch_diff_at_secs(self, secs: float) -> float:
        left_index = bisect.bisect_right(self._ends, secs)
        right_index = bisect.bisect_right(self._starts, secs)
        return sum(
            self.vibrato_nodes[index].value_at_secs(secs)
            for index in range(left_index, right_index)
        )


@dataclasses.dataclass
class PitchControlLayerGenerator:
    _pitch_controls: dataclasses.InitVar[list[PitchControl]]
    interval_dict: PiecewiseIntervalDict = dataclasses.field(default_factory=PiecewiseIntervalDict)

    @staticmethod
    def _overlay_interval(
        segments: list[tuple[portion.Interval, Callable[[int | float], float] | int | float]],
        interval: portion.Interval,
        value: Callable[[int | float], float] | float,
    ) -> None:
        remaining_segments: list[
            tuple[portion.Interval, Callable[[int | float], float] | int | float]
        ] = []
        for existing_interval, existing_value in segments:
            remaining_segments.extend(
                (atomic_interval, existing_value)
                for atomic_interval in existing_interval - interval
                if not atomic_interval.empty
            )
        remaining_segments.append((interval, value))
        segments[:] = remaining_segments

    def __post_init__(self, _pitch_controls: list[PitchControl]) -> None:
        segments: list[tuple[portion.Interval, Callable[[int | float], float] | int | float]] = []
        for pitch_control in _pitch_controls:
            if pitch_control.type_ == "curve" and len(pitch_control.points):
                prev_point = pitch_control.points[0]
                prev_ticks = prev_point.offset + pitch_control.pos
                prev_value = (pitch_control.pitch + prev_point.value) * 100
                self._overlay_interval(segments, portion.singleton(prev_ticks), prev_value)
                for point in pitch_control.points[1:]:
                    ticks = point.offset + pitch_control.pos
                    value = (pitch_control.pitch + point.value) * 100
                    self._overlay_interval(
                        segments,
                        portion.openclosed(prev_ticks, ticks),
                        functools.partial(  # type: ignore[call-arg]
                            linear_interpolation,
                            start=(prev_ticks, prev_value),
                            end=(ticks, value),
                        ),
                    )
                    prev_ticks = ticks
                    prev_value = value
        for interval, value in segments:
            self.interval_dict[interval] = value

    def value_at_ticks(self, ticks: int) -> float | None:
        return self.interval_dict.get(ticks)


@dataclasses.dataclass
class SynthVPitchSimulator:
    synchronizer: TimeSynchronizer
    _note_list: dataclasses.InitVar[list[NoteStruct]]
    _pitch_controls: dataclasses.InitVar[list[PitchControl] | None] = None
    base_layer: BaseLayerGenerator = dataclasses.field(init=False)
    gaussian_layer: GaussianLayerGenerator = dataclasses.field(init=False)
    vibrato_layer: VibratoLayerGenerator = dataclasses.field(init=False)
    pitch_control_layer: PitchControlLayerGenerator | None = dataclasses.field(
        init=False, default=None
    )

    def __post_init__(
        self, _note_list: list[NoteStruct], _pitch_controls: list[PitchControl] | None
    ) -> None:
        self.base_layer = BaseLayerGenerator(_note_list)
        self.gaussian_layer = GaussianLayerGenerator(_note_list)
        self.vibrato_layer = VibratoLayerGenerator(_note_list)
        if _pitch_controls:
            self.pitch_control_layer = PitchControlLayerGenerator(_pitch_controls)

    def pitch_at_ticks(self, ticks: int) -> float:
        return self.pitch_at_secs(self.synchronizer.get_actual_secs_from_ticks(ticks), ticks)

    def pitch_at_ticks_batch(self, ticks_list: list[int]) -> list[float]:
        if not ticks_list:
            return []
        secs_list = self.synchronizer.get_actual_secs_from_ticks_batch(ticks_list)
        return self.pitch_at_secs_batch(secs_list, ticks_list)

    def pitch_at_secs_batch(
        self, secs_list: list[float], ticks_list: list[int] | None = None
    ) -> list[float]:
        if not secs_list:
            return []
        if ticks_list is None:
            ticks_list = [
                round(self.synchronizer.get_actual_ticks_from_secs(secs)) for secs in secs_list
            ]
        return [
            self._pitch_from_aligned_secs_and_ticks(secs, ticks)
            for secs, ticks in zip(secs_list, ticks_list)
        ]

    def pitch_at_secs(self, secs: float, ticks: int | None = None) -> float:
        if ticks is None:
            ticks = round(self.synchronizer.get_actual_ticks_from_secs(secs))
        return self._pitch_from_aligned_secs_and_ticks(secs, ticks)

    def _pitch_from_aligned_secs_and_ticks(self, secs: float, ticks: int) -> float:
        if self.pitch_control_layer is not None:
            pitch_control_value = self.pitch_control_layer.value_at_ticks(ticks)
            if pitch_control_value is not None:
                return pitch_control_value
        if not self.base_layer.note_list:
            return 0.0
        return (
            self.base_layer.pitch_at_secs(secs)
            + self.vibrato_layer.pitch_diff_at_secs(secs)
            + self.gaussian_layer.pitch_diff_at_secs(secs)
        )
