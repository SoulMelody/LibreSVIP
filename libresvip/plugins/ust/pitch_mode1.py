import dataclasses
from typing import Optional

from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import Note, ParamCurve
from libresvip.model.pitch_simulator import PitchSimulator
from libresvip.model.point import Point
from libresvip.model.portamento import PortamentoPitch
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
    notes: list[Optional[UtauMode1NotePitchData]] = dataclasses.field(default_factory=list)


def pitch_from_utau_mode1_track(
    pitch_data: UtauMode1TrackPitchData,
    synchronizer: TimeSynchronizer,
    notes: list[Note],
) -> ParamCurve:
    pitch_points: list[Point] = []
    for note, note_pitch in zip(notes, pitch_data.notes):
        if note_pitch is not None and len(note_pitch.pitch_points):
            pitch_points.extend(
                Point(
                    x=note.start_pos + index * MODE1_PITCH_SAMPLING_INTERVAL_TICK,
                    y=value,
                )
                for index, value in enumerate(note_pitch.pitch_points)
            )
    pitch_simulator = PitchSimulator(
        synchronizer=synchronizer,
        portamento=PortamentoPitch.no_portamento(),
        note_list=notes,
    )
    return RelativePitchCurve(
        lower_bound=notes[0].start_pos,
        upper_bound=notes[-1].end_pos,
    ).to_absolute(pitch_points, pitch_simulator)


def pitch_to_utau_mode1_track(pitch: ParamCurve, notes: list[Note]) -> UtauMode1TrackPitchData:
    note_pitch_data: list[Optional[UtauMode1NotePitchData]] = []
    for note in notes:
        data = [
            point
            for point in pitch.points.root
            if note.start_pos <= point.x - 1920 < note.end_pos and point.y != -100
        ]
        if not len(data):
            note_pitch_data.append(UtauMode1NotePitchData())
            continue
        resampled_data = dot_resampled(data, MODE1_PITCH_SAMPLING_INTERVAL_TICK)
        pitch_points = [round(pitch) - note.key_number * 100 for _, pitch in resampled_data]
        note_pitch_data.append(UtauMode1NotePitchData(pitch_points))
    return UtauMode1TrackPitchData(note_pitch_data)
