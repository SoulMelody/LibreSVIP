from __future__ import annotations

import bisect
import math
from dataclasses import dataclass
from itertools import pairwise
from typing import TYPE_CHECKING, Callable

from libresvip.model.base import ParamCurve as LibreParamCurve
from libresvip.model.base import Points
from libresvip.model.point import Point
from libresvip.utils.music_math import clamp

from .model_v1 import (
    AnchorNode,
    Param,
    ParamCurve,
    ParamCurveAnchor,
    ParamCurveFree,
)
from .options import PitchImportMode

if TYPE_CHECKING:
    from collections.abc import Iterable

SAMPLE_INTERVAL = 5
PITCH_BREAK_VALUE = -100
PITCH_MIN = 0
PITCH_MAX = 12800


def _ceil_to_interval(value: int) -> int:
    return math.ceil(value / SAMPLE_INTERVAL) * SAMPLE_INTERVAL


def _floor_to_interval(value: int) -> int:
    return math.floor(value / SAMPLE_INTERVAL) * SAMPLE_INTERVAL


def _round_to_interval(value: int) -> int:
    return round(value / SAMPLE_INTERVAL) * SAMPLE_INTERVAL


def _curve_bounds(curve: ParamCurve) -> tuple[int, int] | None:
    if isinstance(curve, ParamCurveFree):
        if not curve.values:
            return None
        return curve.start, curve.start + curve.step * (len(curve.values) - 1)
    if not curve.nodes:
        return None
    positions = [curve.start + node.x for node in curve.nodes]
    return min(positions), max(positions)


def _combined_bounds(curves: Iterable[ParamCurve]) -> tuple[int, int] | None:
    bounds = [bound for curve in curves if (bound := _curve_bounds(curve)) is not None]
    if not bounds:
        return None
    return min(bound[0] for bound in bounds), max(bound[1] for bound in bounds)


def _free_curve_value(curve: ParamCurveFree, position: int) -> float | None:
    if not curve.values:
        return None
    relative = position - curve.start
    last_offset = curve.step * (len(curve.values) - 1)
    if relative < 0 or relative > last_offset:
        return None
    left_index, remainder = divmod(relative, curve.step)
    if remainder == 0:
        return float(curve.values[left_index])
    right_index = left_index + 1
    if right_index >= len(curve.values):
        return None
    ratio = remainder / curve.step
    return curve.values[left_index] + (curve.values[right_index] - curve.values[left_index]) * ratio


class FreeCurveEvaluator:
    def __init__(self, curves: list[ParamCurve]) -> None:
        self.curves = [curve for curve in curves if isinstance(curve, ParamCurveFree)]
        self.bounds = _combined_bounds(self.curves)

    def evaluate(self, position: int) -> float | None:
        result = None
        for curve in self.curves:
            value = _free_curve_value(curve, position)
            if value is not None:
                result = value
        return result


@dataclass(frozen=True)
class AbsoluteAnchorNode:
    x: int
    y: int
    interp: str


def _absolute_nodes(curve: ParamCurveAnchor, *, force_last_none: bool) -> list[AbsoluteAnchorNode]:
    result = [
        AbsoluteAnchorNode(
            x=curve.start + node.x,
            y=node.y,
            interp=node.interp,
        )
        for node in curve.nodes
    ]
    if force_last_none and result:
        result[-1] = AbsoluteAnchorNode(x=result[-1].x, y=result[-1].y, interp="none")
    return result


def _deduplicate_anchor_nodes(nodes: Iterable[AbsoluteAnchorNode]) -> list[AbsoluteAnchorNode]:
    first_nodes: dict[int, AbsoluteAnchorNode] = {}
    for node in nodes:
        first_nodes.setdefault(node.x, node)
    return sorted(first_nodes.values(), key=lambda node: node.x)


def _secant(left: AbsoluteAnchorNode, right: AbsoluteAnchorNode) -> float:
    return (right.y - left.y) / (right.x - left.x)


def _fritsch_butland(
    left: AbsoluteAnchorNode,
    center: AbsoluteAnchorNode,
    right: AbsoluteAnchorNode,
) -> float:
    left_width = center.x - left.x
    right_width = right.x - center.x
    left_delta = (center.y - left.y) / left_width
    right_delta = (right.y - center.y) / right_width
    if left_delta * right_delta <= 0:
        return 0.0
    weight_1 = 2 * right_width + left_width
    weight_2 = right_width + 2 * left_width
    return (weight_1 + weight_2) / (
        weight_1 / left_delta + weight_2 / right_delta
    )


def _hermite_value(nodes: list[AbsoluteAnchorNode], left_index: int, position: int) -> float:
    left = nodes[left_index]
    right = nodes[left_index + 1]
    left_slope = (
        _fritsch_butland(nodes[left_index - 1], left, right)
        if left_index > 0
        else _secant(left, right)
    )
    right_slope = (
        _fritsch_butland(left, right, nodes[left_index + 2])
        if left_index + 2 < len(nodes)
        else _secant(left, right)
    )
    width = right.x - left.x
    ratio = (position - left.x) / width
    ratio_2 = ratio * ratio
    ratio_3 = ratio_2 * ratio
    return (
        (2 * ratio_3 - 3 * ratio_2 + 1) * left.y
        + (ratio_3 - 2 * ratio_2 + ratio) * width * left_slope
        + (-2 * ratio_3 + 3 * ratio_2) * right.y
        + (ratio_3 - ratio_2) * width * right_slope
    )


def _anchor_nodes_value(nodes: list[AbsoluteAnchorNode], position: int) -> float | None:
    if not nodes:
        return None
    positions = [node.x for node in nodes]
    right_index = bisect.bisect_left(positions, position)
    if right_index < len(nodes) and nodes[right_index].x == position:
        return float(nodes[right_index].y)
    if right_index == 0 or right_index == len(nodes):
        return None
    left_index = right_index - 1
    left = nodes[left_index]
    right = nodes[right_index]
    if left.interp == "none":
        return None
    if left.interp == "linear":
        ratio = (position - left.x) / (right.x - left.x)
        return left.y + (right.y - left.y) * ratio
    return _hermite_value(nodes, left_index, position)


class AnchorCurveEvaluator:
    def __init__(self, curves: list[ParamCurve]) -> None:
        anchor_curves = [curve for curve in curves if isinstance(curve, ParamCurveAnchor)]
        self.nodes = _deduplicate_anchor_nodes(
            node
            for curve in anchor_curves
            for node in _absolute_nodes(curve, force_last_none=True)
        )
        self.bounds = (
            (self.nodes[0].x, self.nodes[-1].x)
            if self.nodes
            else None
        )

    def evaluate(self, position: int) -> float | None:
        return _anchor_nodes_value(self.nodes, position)


class OriginalCurveEvaluator:
    def __init__(self, curves: list[ParamCurve]) -> None:
        self.free = FreeCurveEvaluator(curves)
        self.anchors = [
            _deduplicate_anchor_nodes(_absolute_nodes(curve, force_last_none=True))
            for curve in curves
            if isinstance(curve, ParamCurveAnchor)
        ]
        self.bounds = _combined_bounds(curves)

    def evaluate(self, position: int) -> float | None:
        result = self.free.evaluate(position)
        for nodes in self.anchors:
            value = _anchor_nodes_value(nodes, position)
            if value is not None:
                result = value
        return result


class ResolvedParam:
    def __init__(self, parameter: Param, mode: PitchImportMode) -> None:
        self.mode = mode
        self.edited_anchor = AnchorCurveEvaluator(parameter.edited)
        self.edited_free = FreeCurveEvaluator(parameter.edited)
        self.original = OriginalCurveEvaluator(parameter.original)
        self.transform_anchor = AnchorCurveEvaluator(parameter.transform)
        self.transform_free = FreeCurveEvaluator(parameter.transform)
        relevant_curves = [*parameter.edited, *parameter.transform]
        if mode == PitchImportMode.EDITED_AND_ORIGINAL:
            relevant_curves.extend(parameter.original)
        self.bounds = _combined_bounds(relevant_curves)

    def evaluate(self, position: int) -> float | None:
        source = self.edited_anchor.evaluate(position)
        if source is None:
            source = self.edited_free.evaluate(position)
        if source is None and self.mode == PitchImportMode.EDITED_AND_ORIGINAL:
            source = self.original.evaluate(position)
        if source is None:
            return None
        transform = self.transform_anchor.evaluate(position)
        if transform is None:
            transform = self.transform_free.evaluate(position)
        return source * (transform / 1000 if transform is not None else 1.0)


def build_pitch_curve(
    pitch: ResolvedParam,
    *,
    coordinate_offset: int,
    tone_shift: ResolvedParam | None = None,
    vibrato_value: Callable[[int], float] | None = None,
) -> LibreParamCurve:
    if pitch.bounds is None:
        return LibreParamCurve()
    start = _ceil_to_interval(pitch.bounds[0])
    end = _floor_to_interval(pitch.bounds[1])
    if start > end:
        return LibreParamCurve()
    sampled: list[tuple[int, int | None]] = []
    for relative_tick in range(start, end + 1, SAMPLE_INTERVAL):
        value = pitch.evaluate(relative_tick)
        if value is not None and tone_shift is not None:
            shift = tone_shift.evaluate(relative_tick)
            if shift is not None:
                value += shift
        if value is not None and vibrato_value is not None:
            value += vibrato_value(relative_tick)
        sampled.append(
            (
                relative_tick + coordinate_offset,
                (
                    round(clamp(value, PITCH_MIN, PITCH_MAX))
                    if value is not None
                    else None
                ),
            )
        )
    points: list[Point] = [Point.start_point()]
    run_last_x: int | None = None
    for x, value in sampled:
        if value is None:
            if run_last_x is not None:
                points.append(Point(run_last_x, PITCH_BREAK_VALUE))
                run_last_x = None
            continue
        if run_last_x is None:
            points.append(Point(x, PITCH_BREAK_VALUE))
        points.append(Point(x, value))
        run_last_x = x
    if run_last_x is not None:
        points.append(Point(run_last_x, PITCH_BREAK_VALUE))
    if len(points) == 1:
        return LibreParamCurve()
    points.append(Point.end_point())
    return LibreParamCurve(points=Points(root=points))


def _split_internal_curve(points: list[Point]) -> list[list[Point]]:
    segments: list[list[Point]] = []
    current: list[Point] = []
    for point in sorted(enumerate(points), key=lambda item: (item[1].x, item[0])):
        value = point[1]
        if value.x in (Point.start_point().x, Point.end_point().x) or value.y == PITCH_BREAK_VALUE:
            if current:
                segments.append(current)
                current = []
        else:
            current.append(value)
    if current:
        segments.append(current)
    return segments


def _deduplicate_points(points: list[Point]) -> list[Point]:
    result: dict[int, Point] = {}
    for point in points:
        result[point.x] = point
    return sorted(result.values(), key=lambda point: point.x)


def _linear_value(points: list[Point], position: int) -> float | None:
    if not points:
        return None
    positions = [point.x for point in points]
    right_index = bisect.bisect_left(positions, position)
    if right_index < len(points) and points[right_index].x == position:
        return float(points[right_index].y)
    if right_index == 0 or right_index == len(points):
        return None
    left = points[right_index - 1]
    right = points[right_index]
    ratio = (position - left.x) / (right.x - left.x)
    return left.y + (right.y - left.y) * ratio


def export_pitch_param(
    curve: LibreParamCurve,
    *,
    coordinate_offset: int,
) -> Param | None:
    free_curves: list[ParamCurve] = []
    for segment in _split_internal_curve(curve.points.root):
        points = _deduplicate_points(
            [
                Point(
                    x=point.x - coordinate_offset,
                    y=round(clamp(point.y, PITCH_MIN, PITCH_MAX)),
                )
                for point in segment
            ]
        )
        if not points:
            continue
        start = _ceil_to_interval(points[0].x)
        end = _floor_to_interval(points[-1].x)
        if start > end:
            sample_position = _round_to_interval(points[0].x)
            sampled_values = [(sample_position, points[0].y)]
        else:
            sampled_values = [
                (position, round(clamp(value, PITCH_MIN, PITCH_MAX)))
                for position in range(start, end + 1, SAMPLE_INTERVAL)
                if (value := _linear_value(points, position)) is not None
            ]
        if sampled_values:
            free_curves.append(
                ParamCurveFree(
                    type="free",
                    start=sampled_values[0][0],
                    step=SAMPLE_INTERVAL,
                    values=[value for _, value in sampled_values],
                )
            )
    if not free_curves:
        return None
    return Param(edited=free_curves, transform=[], original=[])


def param_extent(parameter: Param | None) -> tuple[int, int] | None:
    if parameter is None:
        return None
    return _combined_bounds([*parameter.edited, *parameter.transform, *parameter.original])


def make_anchor_node(*, x: int, y: int, interp: str) -> AnchorNode:
    return AnchorNode(x=x, y=y, interp=interp)
