import dataclasses
import itertools
import operator
from typing import Optional

from libresvip.core.constants import TICKS_IN_BEAT
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import Note, ParamCurve, SongTempo
from libresvip.model.pitch_simulator import PitchSimulator
from libresvip.model.point import Point
from libresvip.model.portamento import PortamentoPitch
from libresvip.model.relative_pitch_curve import RelativePitchCurve
from libresvip.utils.search import find_last_index

from .constants import (
    MODE2_PITCH_MAX_POINT_COUNT,
    MODE2_PITCH_SAMPLING_INTERVAL_TICK,
)
from .interpolation import interpolate
from .model import UtauNoteVibrato, UTAUPitchBendMode
from .rdp_simplification import simplify_shape_to
from .vibrato_param import append_utau_note_vibrato


def milli_sec_from_tick(tick: int, bpm: float) -> float:
    return tick / TICKS_IN_BEAT * 60 / bpm * 1000


@dataclasses.dataclass
class UtauMode2NotePitchData:
    bpm: float
    start: Optional[float]  # milliSec, None only if the note is not applied with pitch
    start_shift: Optional[float]  # 10 cents
    widths: list[float] = dataclasses.field(default_factory=list)  # milliSec
    shifts: list[float] = dataclasses.field(default_factory=list)  # 10 cents
    curve_types: list[UTAUPitchBendMode] = dataclasses.field(default_factory=list)
    vibrato_params: Optional[UtauNoteVibrato] = None


@dataclasses.dataclass
class UtauMode2TrackPitchData:
    notes: list[Optional[UtauMode2NotePitchData]] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class NotePitchData:
    points: list[Point]
    offset: int
    bpm: float


def pitch_to_utau_mode2_track(
    pitch: ParamCurve, notes: list[Note], tempos: list[SongTempo]
) -> UtauMode2TrackPitchData:
    absolute_pitch = [
        point._replace(x=point.x - 1920) for point in pitch.points.root if point.y != -100
    ]

    def to_relative(from_: list[Point], key: int) -> list[Point]:
        return [Point(x=p.x, y=(p.y or key * 100) - key * 100) for p in from_]

    dot_pit_data = (
        [
            NotePitchData(
                to_relative(
                    [point for point in absolute_pitch if point.x < notes[0].end_pos],
                    notes[0].key_number,
                ),
                -min(
                    (point.x for point in absolute_pitch if point.x < 0),
                    default=0,
                ),
                bpm_for_note(tempos, notes[0]),
            ),  # first note
        ]
        + [
            NotePitchData(
                to_relative(
                    [point for point in absolute_pitch if note.start_pos <= point.x < note.end_pos],
                    note.key_number,
                ),
                (
                    next(
                        (point.x for point in absolute_pitch if point.x >= note.start_pos),
                        note.start_pos,
                    )
                    - note.start_pos
                ),
                bpm_for_note(tempos, note),
            )
            for note in notes[1:]
        ]
    )

    dot_pit_data_simplified = [
        NotePitchData(
            simplify_shape_to(x.points, MODE2_PITCH_MAX_POINT_COUNT),
            x.offset,
            x.bpm,
        )
        for x in dot_pit_data
    ]

    return UtauMode2TrackPitchData(
        notes=[
            UtauMode2NotePitchData(
                curr_note.bpm,
                milli_sec_from_tick(curr_note.offset, curr_note.bpm),
                curr_note.points[0].y / 10,
                [
                    milli_sec_from_tick(next_point.x - prev_point.x, curr_note.bpm)
                    for prev_point, next_point in zip(curr_note.points, curr_note.points[1:])
                ],
                [point.y / 10 for point in curr_note.points[1:]],
                [""] * (len(curr_note.points) - 1),
                None,
            )
            if curr_note.points
            else None
            for curr_note in dot_pit_data_simplified
        ]
    )


def pitch_from_utau_mode2_track(
    pitch_data: UtauMode2TrackPitchData,
    tick_time_transformer: TimeSynchronizer,
    notes: list[Note],
) -> ParamCurve:
    if pitch_data is None:
        return ParamCurve()
    pitch_points: list[Point] = []
    last_note: Optional[Note] = None
    pending_pitch_points: list[Point] = []
    for note, note_pitch in zip(notes, pitch_data.notes):
        if note_pitch is not None:
            points = []
            note_start_in_millis = (
                tick_time_transformer.get_actual_secs_from_ticks(note.start_pos) * 1000
            )
            if note_pitch.start is not None:
                pos_in_millis = note_start_in_millis + note_pitch.start
                tick_pos = tick_time_transformer.get_actual_ticks_from_secs(pos_in_millis / 1000)
                start_shift = round(
                    (last_note.key_number - note.key_number) * 100
                    if last_note and note.start_pos == last_note.end_pos
                    else note_pitch.start_shift * 10
                    if note_pitch.start_shift is not None
                    else 0
                )
                points.append(Point(x=round(tick_pos), y=start_shift))
                for width, shift, curve_type in itertools.zip_longest(
                    note_pitch.widths,
                    note_pitch.shifts,
                    note_pitch.curve_types,
                ):
                    if width is None:
                        break
                    if shift is None:
                        shift = 0
                    if curve_type is None:
                        curve_type = ""
                    pos_in_millis += width
                    tick_pos = tick_time_transformer.get_actual_ticks_from_secs(
                        pos_in_millis / 1000
                    )
                    this_point = Point(x=round(tick_pos), y=round(shift * 10))
                    last_point = points[-1]
                    if this_point.x != last_point.x and this_point.y != last_point.y:
                        interpolated_point_list = interpolate(
                            last_point,
                            this_point,
                            curve_type,
                            MODE2_PITCH_SAMPLING_INTERVAL_TICK,
                        )
                        points.extend(interpolated_point_list[1:])
                    else:
                        points.append(this_point)
            pitch_points.extend(
                point
                for point in pending_pitch_points
                if point.x < (points[0].x if points else float("inf"))
            )
            pending_pitch_points = shape(
                append_utau_note_vibrato(
                    append_end_point(
                        append_start_point(
                            fix_points_at_last_note(
                                points,
                                note,
                                last_note,
                            ),
                            note,
                        ),
                        note,
                    ),
                    note_pitch.vibrato_params,
                    note,
                    tick_time_transformer,
                    MODE2_PITCH_SAMPLING_INTERVAL_TICK,
                )
            )
        last_note = note
    pitch_points.extend(pending_pitch_points)
    pitch_simulator = PitchSimulator(
        synchronizer=tick_time_transformer,
        portamento=PortamentoPitch.no_portamento(),
        note_list=notes,
    )
    return RelativePitchCurve(
        lower_bound=notes[0].start_pos,
        upper_bound=notes[-1].end_pos,
    ).to_absolute(pitch_points, pitch_simulator)


def fix_points_at_last_note(
    pitch_data: list[Point], this_note: Note, last_note: Optional[Note]
) -> list[Point]:
    if last_note is None or last_note.end_pos != this_note.start_pos:
        return pitch_data
    fixed = [
        Point(
            x=point.x,
            y=point.y + (this_note.key_number - last_note.key_number) * 100,
        )
        if point.x < this_note.start_pos
        else point
        for point in pitch_data
    ]
    last_point = fixed[-1] if fixed else None
    return (
        [*fixed, Point(x=this_note.start_pos, y=0)]
        if last_point is not None and last_point.x < this_note.start_pos
        else fixed
    )


def append_start_point(pitch_data: list[Point], this_note: Note) -> list[Point]:
    first_point = pitch_data[0] if pitch_data else None
    if first_point is None:
        return [Point(x=this_note.start_pos, y=0)]
    elif first_point.x > this_note.start_pos:
        return [Point(x=this_note.start_pos, y=first_point.y), *pitch_data]
    else:
        return pitch_data


def append_end_point(pitch_data: list[Point], this_note: Note) -> list[Point]:
    last_point = pitch_data[-1] if pitch_data else None
    if last_point is None:
        return [Point(x=this_note.end_pos, y=0)]
    elif last_point.x < this_note.end_pos:
        return [*pitch_data, Point(this_note.end_pos, last_point.y)]
    else:
        return pitch_data


def shape(pitch_data: list[Point]) -> list[Point]:
    sorted_data = sorted(pitch_data, key=operator.attrgetter("x"))
    shaped_data: list[Point] = []
    for point in sorted_data:
        if shaped_data and shaped_data[-1].x == point.x:
            shaped_data[-1] = Point(x=shaped_data[-1].x, y=(shaped_data[-1].y + point.y) // 2)
        else:
            shaped_data.append(point)
    return shaped_data


def bpm_for_note(tempos: list[SongTempo], note: Note) -> float:
    tempo_index = find_last_index(tempos, lambda x: x.position <= note.start_pos)
    return tempos[tempo_index].bpm
