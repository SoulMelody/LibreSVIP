import dataclasses

from libresvip.model.base import Note, ParamCurve, Point, Points
from libresvip.model.relative_pitch_curve import RelativePitchCurve

from .constants import (
    MODE1_PITCH_SAMPLING_INTERVAL_TICK,
)
from .resampling import dot_resampled


@dataclasses.dataclass
class UtauMode1NotePitchData:
    pitch_points: list[int] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class UtauMode1TrackPitchData:
    notes: list[UtauMode1NotePitchData] = dataclasses.field(default_factory=list)


def pitch_from_utau_mode1_track(pitch_data: UtauMode1TrackPitchData, notes: list[Note]) -> ParamCurve:
    pitch_points = []
    for note, note_pitch in zip(notes, pitch_data.notes):
        if note_pitch is not None and len(note_pitch.pitch_points):
            pitch_points += [
                Point(x=note.start_pos + index * MODE1_PITCH_SAMPLING_INTERVAL_TICK, y=value)
                for index, value in enumerate(note_pitch.pitch_points)
            ]
    return RelativePitchCurve(points=Points(
        root=pitch_points
    )).to_absolute(notes)

def pitch_to_utau_mode1_track(pitch: ParamCurve, notes: list[Note]) -> UtauMode1TrackPitchData:
    note_pitch_data = []
    for note in notes:
        data = [
            point
            for point in pitch.points
            if note.start_pos <= point.x - 1920 < note.end_pos
        ]
        if not len(data):
            note_pitch_data.append(UtauMode1NotePitchData())
            continue
        resampled_data = dot_resampled(data, MODE1_PITCH_SAMPLING_INTERVAL_TICK)
        pitch_points = [
            round(pitch) - note.key_number * 100
            for _, pitch in resampled_data
        ]
        note_pitch_data.append(UtauMode1NotePitchData(pitch_points))
    return UtauMode1TrackPitchData(note_pitch_data)
