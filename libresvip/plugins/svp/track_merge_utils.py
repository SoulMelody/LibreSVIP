from typing import List

from libresvip.core.time_interval import RangeInterval
from libresvip.model.base import Note, ParamCurve, Params, Point, SingingTrack
from libresvip.utils import find_index, find_last_index


def param_curve_override_with(
    main_curve: ParamCurve,
    override_curve: ParamCurve,
    start: int,
    end: int,
    termination: int = 0,
) -> None:
    inserted_points: List[Point] = []
    main_left_index = find_last_index(
        main_curve.points.__root__, lambda point: point.position <= start
    )
    main_right_index = find_index(
        main_curve.points.__root__, lambda point: point.position > end
    )
    override_left_index = find_last_index(
        override_curve.points.__root__, lambda point: point.position <= start
    )
    override_right_index = find_index(
        override_curve.points.__root__, lambda point: point.position > end
    )
    main_left_defined = (
        main_curve.points[main_left_index].position != termination
        and main_curve.points[main_left_index + 1].position != termination
    )
    main_right_defined = (
        main_curve.points[main_right_index - 1].position != termination
        and main_curve.points[main_right_index].position != termination
    )
    override_left_defined = (
        override_curve.points[override_left_index].position != termination
        and override_curve.points[override_left_index + 1].position != termination
    )
    override_right_defined = (
        override_curve.points[override_right_index - 1].position != termination
        and override_curve.points[override_right_index].position != termination
    )
    if main_left_defined:
        r = (start - main_curve.points[main_left_index].position) / (
            main_curve.points[main_left_index + 1].position
            - main_curve.points[main_left_index].position
        )
        inserted_points.append(
            Point(
                start,
                round(
                    r
                    * (
                        main_curve.points[main_left_index + 1].value
                        + main_curve.points[main_left_index].value
                    )
                    * (1 - r)
                ),
            )
        )
    if main_left_defined ^ override_left_defined:
        inserted_points.append(Point(start, termination))
    if override_left_defined:
        r = (start - override_curve.points[override_left_index].position) / (
            override_curve.points[override_left_index + 1].position
            - override_curve.points[override_left_index].position
        )
        inserted_points.append(
            Point(
                start,
                round(
                    r
                    * (
                        override_curve.points[override_left_index + 1].value
                        + override_curve.points[override_left_index].value
                    )
                    * (1 - r)
                ),
            )
        )
    for i in range(override_left_index + 1, override_right_index):
        inserted_points.append(override_curve.points[i])
    if override_right_defined:
        r = (end - override_curve.points[override_right_index - 1].position) / (
            override_curve.points[override_right_index].position
            - override_curve.points[override_right_index - 1].position
        )
        inserted_points.append(
            Point(
                end,
                round(
                    r
                    * (
                        override_curve.points[override_right_index].value
                        + override_curve.points[override_right_index - 1].value
                    )
                    * (1 - r)
                ),
            )
        )
    if main_right_defined ^ override_right_defined:
        inserted_points.append(Point(end, termination))
    if main_right_defined:
        r = (end - main_curve.points[main_right_index - 1].position) / (
            main_curve.points[main_right_index].position
            - main_curve.points[main_right_index - 1].position
        )
        inserted_points.append(
            Point(
                end,
                round(
                    r
                    * (
                        main_curve.points[main_right_index].value
                        + main_curve.points[main_right_index - 1].value
                    )
                    * (1 - r)
                ),
            )
        )
    main_curve.points.__root__ = [
        point
        for i, point in enumerate(main_curve.points.__root__)
        if main_left_index < i < main_right_index
    ]
    main_curve.points.__root__ = (
        main_curve.points.__root__[:main_left_index]
        + inserted_points
        + main_curve.points.__root__[main_left_index:]
    )


def params_override_with(
    main_params: Params, override_params: Params, start: int, end: int
) -> None:
    param_curve_override_with(main_params.pitch, override_params.pitch, start, end)
    param_curve_override_with(main_params.volume, override_params.volume, start, end)
    param_curve_override_with(main_params.breath, override_params.breath, start, end)
    param_curve_override_with(main_params.gender, override_params.gender, start, end)
    param_curve_override_with(
        main_params.strength, override_params.strength, start, end
    )


def track_override_with(
    track: SingingTrack, note_list: List[Note], params: Params, first_bar_tick: int
) -> None:
    main_note_list = track.note_list
    interval = RangeInterval()
    main_left_index = main_right_index = -1
    for i in range(0, len(note_list)):
        main_left_index = (
            find_last_index(
                main_note_list, lambda note: note.start_pos <= note_list[i].start_pos
            )
            if main_left_index < len(main_note_list) - 1
            else -1
        )
        main_left_note = (
            main_note_list[main_left_index] if main_left_index >= 0 else None
        )
        start = (
            note_list[i].start_pos - 120
            if main_left_note is None
            or main_left_note.end_pos < note_list[i].start_pos - 120
            else (main_left_note.end_pos + note_list[i].start_pos) // 2
        )
        while (
            i < len(note_list) - 1
            and note_list[i].end_pos >= note_list[i + 1].start_pos
        ):
            i += 1
        main_right_index = (
            find_index(
                main_note_list[main_left_index:],
                lambda note: note.start_pos > note_list[i].start_pos,
            )
            if main_right_index < len(main_note_list) - 1
            else -1
        )
        main_right_note = (
            main_note_list[main_right_index] if main_right_index >= 0 else None
        )
        end = (
            note_list[i].end_pos + 120
            if main_right_note is None
            or main_right_note.start_pos > note_list[i].end_pos + 120
            else (main_right_note.start_pos + note_list[i].end_pos) // 2
        )
        interval |= RangeInterval([(start, end)])
    track.note_list.extend(note_list)
    track.note_list.sort(key=lambda note: note.start_pos)
    for start, end in (interval >> first_bar_tick).sub_ranges():
        params_override_with(track.edited_params, params, start, end)
