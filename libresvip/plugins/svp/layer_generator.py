import dataclasses
import functools
import itertools
import math
from collections.abc import Callable
from typing import NamedTuple

import portion

from libresvip.core.exceptions import ParamsError
from libresvip.core.time_interval import PiecewiseIntervalDict
from libresvip.utils.music_math import linear_interpolation
from libresvip.utils.search import find_index

from .constants import HALFWIDTH_FLOOR_SECS, MAX_BREAK, PORTAMENTO_HALFWIDTH_RATIO
from .interval_utils import position_to_ticks
from .model import SVPitchControl


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

    def __post_init__(self, _note_list: list[NoteStruct]) -> None:
        if not _note_list:
            return
        self.note_list = _note_list
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

    def pitch_at_secs(self, secs: float) -> float:
        query = [node for node in self.sigmoid_nodes if node.start <= secs < node.end]
        if not query:
            if self.sigmoid_nodes:
                next_idx = find_index(self.sigmoid_nodes, lambda node: node.start > secs)
                if next_idx == 0:
                    return self.sigmoid_nodes[0].key_left * 100
                if next_idx < 0:
                    return self.sigmoid_nodes[-1].key_right * 100
                return self.sigmoid_nodes[next_idx - 1].key_right * 100
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
        elif len(query) == 1:
            return query[0].value_at_secs(secs)
        elif len(query) <= 3:
            first = query[0]
            last = query[-1]
            width = first.end - last.start
            bottom = first.value_at_secs(last.start)
            top = last.value_at_secs(first.end)
            diff1 = first.slope_at_secs(last.start)
            diff2 = last.slope_at_secs(first.end)
            return self.cubic_bezier(width, bottom, top, diff1, diff2)(secs - last.start)
        else:
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

    def pitch_diff_at_secs(self, secs: float) -> float:
        return sum(
            node.value_at_secs(secs)
            for node in self.gaussian_nodes
            if node.start <= secs < node.end
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

    def pitch_diff_at_secs(self, secs: float) -> float:
        return sum(
            node.value_at_secs(secs) for node in self.vibrato_nodes if node.start <= secs < node.end
        )


@dataclasses.dataclass
class PitchControlLayerGenerator:
    _pitch_controls: dataclasses.InitVar[list[SVPitchControl]]
    interval_dict: PiecewiseIntervalDict = dataclasses.field(default_factory=PiecewiseIntervalDict)

    def __post_init__(self, _pitch_controls: list[SVPitchControl]) -> None:
        for pitch_control in _pitch_controls:
            if pitch_control.type_ == "curve" and len(pitch_control.points):
                prev_point = pitch_control.points.root[0]
                base_position = position_to_ticks(pitch_control.pos)
                prev_ticks = position_to_ticks(prev_point.offset) + base_position
                prev_value = (pitch_control.pitch + prev_point.value) * 100
                self.interval_dict[portion.singleton(prev_ticks)] = prev_value
                for point in pitch_control.points.root[1:]:
                    ticks = position_to_ticks(point.offset) + base_position
                    value = (pitch_control.pitch + point.value) * 100
                    self.interval_dict[
                        portion.openclosed(
                            prev_ticks,
                            ticks,
                        )
                    ] = functools.partial(
                        linear_interpolation,  # type: ignore[call-arg]
                        start=(prev_ticks, prev_value),
                        end=(ticks, value),
                    )
                    prev_ticks = ticks
                    prev_value = value

    def value_at_ticks(self, ticks: int) -> float | None:
        return self.interval_dict.get(ticks)
