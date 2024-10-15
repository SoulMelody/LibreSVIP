from __future__ import annotations

import abc
import dataclasses
import enum
import operator
from typing import TYPE_CHECKING, Optional, Union

from libresvip.model.point import Point
from libresvip.utils.search import find_last_index

from .interval_utils import position_to_ticks
from .layer_generator import (
    BaseLayerGenerator,
    GaussianLayerGenerator,
    NoteStruct,
    VibratoLayerGenerator,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

    import portion

    from libresvip.core.time_sync import TimeSynchronizer

    from .model import SVNote


class ParamOperators(enum.Enum):
    ADD = operator.add
    SUB = operator.sub
    MUL = operator.mul
    DIV = operator.truediv


class ParamExpression(abc.ABC):
    @abc.abstractmethod
    def value_at_ticks(self, ticks: int) -> float:
        pass

    def __add__(self, other: Union[int, ParamExpression]) -> ParamExpression:
        if isinstance(other, int):
            return TranslationalParam(
                self,
                other,
            )
        else:
            return CompoundParam(
                self,
                ParamOperators.ADD,
                other,
            )

    def __sub__(self, other: Union[int, ParamExpression]) -> ParamExpression:
        if isinstance(other, int):
            return self + (-other)
        else:
            return CompoundParam(
                self,
                ParamOperators.SUB,
                other,
            )

    def __mul__(self, other: Union[float, ParamExpression]) -> ParamExpression:
        if isinstance(other, float):
            return ScaledParam(
                self,
                other,
            )
        else:
            return CompoundParam(
                self,
                ParamOperators.MUL,
                other,
            )

    def __truediv__(self, other: Union[float, ParamExpression]) -> ParamExpression:
        if isinstance(other, float):
            return self * (1 / other)
        else:
            return CompoundParam(
                self,
                ParamOperators.DIV,
                other,
            )


@dataclasses.dataclass
class ScaledParam(ParamExpression):
    expression: ParamExpression
    ratio: float

    def value_at_ticks(self, ticks: int) -> float:
        return self.ratio * self.expression.value_at_ticks(ticks)


@dataclasses.dataclass
class TranslationalParam(ParamExpression):
    expression: ParamExpression
    offset: int

    def value_at_ticks(self, ticks: int) -> float:
        return self.expression.value_at_ticks(ticks) + self.offset


@dataclasses.dataclass
class CurveGenerator(ParamExpression):
    base_value: int = dataclasses.field(init=False)
    interpolation: Callable[[float, tuple[float, float], tuple[float, float]], float] = (
        dataclasses.field(init=False)
    )
    point_list: list[Point] = dataclasses.field(init=False)
    _point_list: dataclasses.InitVar[Iterable[Point]]
    _interpolation: dataclasses.InitVar[
        Callable[[float, tuple[float, float], tuple[float, float]], float]
    ]
    _base_value: dataclasses.InitVar[int] = 0
    interval: Optional[portion.Interval] = None

    def __post_init__(
        self,
        _point_list: Iterable[Point],
        _interpolation: Callable[[float, tuple[float, float], tuple[float, float]], float],
        _base_value: int = 0,
    ) -> None:
        self.point_list = []
        current_pos = -1
        current_sum = 0
        overlap_count = 0
        for pos, value in _point_list:
            if pos == current_pos or current_pos < 0:
                current_sum += value
                overlap_count += 1
            else:
                self.point_list.append(Point(current_pos, round(current_sum / overlap_count)))
                current_sum = value
                overlap_count = 1
            current_pos = pos
        if current_pos != -1:
            self.point_list.append(Point(current_pos, round(current_sum / overlap_count)))
        self.interpolation = _interpolation
        self.base_value = _base_value

    def value_at_ticks(self, ticks: int) -> float:
        if len(self.point_list) == 0 or (self.interval is not None and ticks not in self.interval):
            return self.base_value
        index = find_last_index(self.point_list, lambda point: point.x <= ticks)
        if index == -1:
            return self.point_list[0].y
        if index == len(self.point_list) - 1:
            return self.point_list[-1].y
        return self.interpolation(ticks, self.point_list[index], self.point_list[index + 1])

    def get_converted_curve(self, step: int) -> list[Point]:
        result: list[Point] = []
        if len(self.point_list) == 0:
            result.extend(
                (
                    Point.start_point(self.base_value),
                    Point.end_point(self.base_value),
                )
            )
            return result
        prev_point = self.point_list[0]
        result.extend(
            (
                Point.start_point(prev_point.y),
                Point(prev_point.x, prev_point.y),
            )
        )
        for current_point in self.point_list[1:]:
            if prev_point.y == self.base_value and current_point.y == self.base_value:
                result.extend(
                    (
                        Point(prev_point.x, self.base_value),
                        Point(current_point.x, self.base_value),
                    )
                )
            else:
                for p in range(prev_point.x + step, current_point.x, step):
                    v = round(self.interpolation(p, prev_point, current_point))
                    result.append(Point(p, v))
            prev_point = current_point
        result.extend((Point(prev_point.x, prev_point.y), Point.end_point(prev_point.y)))
        return result


@dataclasses.dataclass
class CompoundParam(ParamExpression):
    expr1: ParamExpression
    op: ParamOperators
    expr2: ParamExpression

    def value_at_ticks(self, ticks: int) -> float:
        ticks1 = self.expr1.value_at_ticks(ticks)
        ticks2 = self.expr2.value_at_ticks(ticks)
        if self.op == ParamOperators.ADD:
            return ticks1 + ticks2
        elif self.op == ParamOperators.SUB:
            return ticks1 - ticks2
        elif self.op == ParamOperators.MUL:
            return ticks1 * ticks2
        elif self.op == ParamOperators.DIV:
            return ticks1 / ticks2
        raise NotImplementedError


@dataclasses.dataclass
class PitchGenerator(ParamExpression):
    synchronizer: TimeSynchronizer = dataclasses.field(init=False)
    pitch_diff: ParamExpression = dataclasses.field(init=False)
    vibrato_env: ParamExpression = dataclasses.field(init=False)
    base_layer: BaseLayerGenerator = dataclasses.field(init=False)
    gaussian_layer: GaussianLayerGenerator = dataclasses.field(init=False)
    vibrato_layer: VibratoLayerGenerator = dataclasses.field(init=False)
    _synchronizer: dataclasses.InitVar[TimeSynchronizer]
    _pitch_diff: dataclasses.InitVar[ParamExpression]
    _vibrato_env: dataclasses.InitVar[ParamExpression]
    _note_list: dataclasses.InitVar[list[SVNote]]

    def __post_init__(
        self,
        _synchronizer: TimeSynchronizer,
        _pitch_diff: ParamExpression,
        _vibrato_env: ParamExpression,
        _note_list: list[SVNote],
    ) -> None:
        self.synchronizer = _synchronizer
        self.pitch_diff = _pitch_diff
        self.vibrato_env = _vibrato_env
        if not len(_note_list):
            return
        note_structs = [
            NoteStruct(
                key=sv_note.pitch,
                start=_synchronizer.get_actual_secs_from_ticks(position_to_ticks(sv_note.onset)),
                end=_synchronizer.get_actual_secs_from_ticks(
                    position_to_ticks(sv_note.onset + sv_note.duration)
                ),
                portamento_offset=sv_note.attributes.transition_offset,
                portamento_left=sv_note.attributes.portamento_left,
                portamento_right=sv_note.attributes.portamento_right,
                depth_left=sv_note.attributes.depth_left,
                depth_right=sv_note.attributes.depth_right,
                vibrato_start=sv_note.attributes.vibrato_start,
                vibrato_left=sv_note.attributes.vibrato_left,
                vibrato_right=sv_note.attributes.vibrato_right,
                vibrato_depth=sv_note.attributes.vibrato_depth,
                vibrato_frequency=sv_note.attributes.vibrato_frequency,
                vibrato_phase=sv_note.attributes.vibrato_phase,
            )
            for sv_note in _note_list
        ]
        self.base_layer = BaseLayerGenerator(note_structs)
        self.vibrato_layer = VibratoLayerGenerator(note_structs)
        self.gaussian_layer = GaussianLayerGenerator(note_structs)

    def value_at_ticks(self, ticks: int) -> float:
        return self.value_at_secs(self.synchronizer.get_actual_secs_from_ticks(ticks))

    def value_at_secs(self, secs: float) -> float:
        ticks = round(self.synchronizer.get_actual_ticks_from_secs(secs))
        return (
            self.base_layer.pitch_at_secs(secs)
            + self.pitch_diff.value_at_ticks(ticks)
            + self.vibrato_layer.pitch_diff_at_secs(secs)
            * self.vibrato_env.value_at_ticks(ticks)
            / 1000
            + self.gaussian_layer.pitch_diff_at_secs(secs)
        )
