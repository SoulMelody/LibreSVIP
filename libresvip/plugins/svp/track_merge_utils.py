from bisect import bisect_left, bisect_right
from operator import attrgetter

from libresvip.core.time_interval import RangeInterval
from libresvip.model.base import Note, ParamCurve, Params, SingingTrack
from libresvip.model.point import Point
from libresvip.utils.music_math import linear_interpolation


def _value_at_cut(points: list[Point], index: int, x: int, interruption: int | None) -> int | None:
    if 0 < index < len(points):
        left, right = points[index - 1], points[index]
        if left.y != interruption and right.y != interruption:
            return round(linear_interpolation(x, left, right))
    return None


def param_curve_override_with(
    main_curve: ParamCurve,
    override_curve: ParamCurve,
    start: int,
    end: int,
    interruption: int | None = None,
) -> None:
    main = main_curve.points.root
    override = override_curve.points.root
    if not override:
        return
    x_key = attrgetter("x")
    main_left = bisect_left(main, start, key=x_key)
    main_right = bisect_right(main, end, key=x_key)
    override_left = bisect_left(override, start, key=x_key)
    override_right = bisect_right(override, end, key=x_key)
    replacement = override[override_left:override_right]
    if (
        main_left == main_right
        and not replacement
        and main[main_left - 1 : main_left + 1] == override[override_left - 1 : override_left + 1]
    ):
        return

    def cut_points(x: int, main_index: int, override_index: int, edge: Point | None) -> list[Point]:
        outside = _value_at_cut(main, main_index, x, interruption)
        exact = edge is not None and edge.x == x
        inside = edge.y if exact else _value_at_cut(override, override_index, x, interruption)
        if outside is None and inside in (None, interruption):
            return []
        fallback = interruption if interruption is not None else 0
        outside = outside if outside is not None else fallback
        inside = inside if inside is not None else fallback
        if exact:
            return [Point(x, outside)] if outside != inside else []
        return [Point(x, outside), Point(x, inside)] if outside != inside else [Point(x, inside)]

    left = cut_points(start, main_left, override_left, replacement[0] if replacement else None)
    right = cut_points(end, main_right, override_right, replacement[-1] if replacement else None)
    main[main_left:main_right] = [*left, *replacement, *reversed(right)]


def params_override_with(
    main_params: Params, override_params: Params, start: int, end: int
) -> None:
    param_curve_override_with(main_params.pitch, override_params.pitch, start, end, -100)
    param_curve_override_with(main_params.volume, override_params.volume, start, end)
    param_curve_override_with(main_params.breath, override_params.breath, start, end)
    param_curve_override_with(main_params.gender, override_params.gender, start, end)
    param_curve_override_with(main_params.strength, override_params.strength, start, end)


def track_override_with(
    track: SingingTrack,
    note_list: list[Note],
    params: Params,
    first_bar_tick: int,
) -> None:
    main_notes = track.note_list
    ranges = []
    for note in note_list:
        index = bisect_right(main_notes, note.start_pos, key=attrgetter("start_pos"))
        start = note.start_pos - 120
        end = note.end_pos + 120
        if index and main_notes[index - 1].end_pos >= start:
            start = (main_notes[index - 1].end_pos + note.start_pos) // 2
        if index < len(main_notes) and main_notes[index].start_pos <= end:
            end = (note.end_pos + main_notes[index].start_pos) // 2
        ranges.append((start, end))
    main_notes.extend(note_list)
    main_notes.sort(key=attrgetter("start_pos"))
    for start, end in RangeInterval(ranges).shift(first_bar_tick).sub_ranges():
        params_override_with(track.edited_params, params, start, end)
