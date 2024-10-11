import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from libresvip.core.constants import (
    DEFAULT_PITCH_BEND_SENSITIVITY,
    MAX_PITCH_BEND_SENSITIVITY,
    MIN_BREAK_LENGTH_BETWEEN_PITCH_SECTIONS,
    PITCH_MAX_VALUE,
)
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import Note, ParamCurve
from libresvip.model.pitch_simulator import PitchSimulator
from libresvip.model.portamento import PortamentoPitch
from libresvip.model.relative_pitch_curve import RelativePitchCurve
from libresvip.utils.music_math import clamp

if TYPE_CHECKING:
    from libresvip.model.point import Point


@dataclass
class ControlEvent:
    tick: int
    value: int


@dataclass
class MIDIPitchData:
    pit: list[ControlEvent]
    pbs: list[ControlEvent]


def generate_for_midi(
    first_bar_length: int,
    pitch: ParamCurve,
    notes: list[Note],
    synchronizer: TimeSynchronizer,
) -> Optional[MIDIPitchData]:
    pitch_simulator = PitchSimulator(
        synchronizer=synchronizer,
        portamento=PortamentoPitch.no_portamento(),
        note_list=notes,
    )
    data = RelativePitchCurve(first_bar_length).from_absolute(pitch.points.root, pitch_simulator)
    if not len(data):
        return None
    pitch_sectioned: list[list[Point]] = [[]]
    current_pos = 0
    for pitch_event in data:
        if (
            not pitch_sectioned[-1]
            or pitch_event.x - current_pos < MIN_BREAK_LENGTH_BETWEEN_PITCH_SECTIONS
        ):
            pitch_sectioned[-1].append(pitch_event)
        else:
            pitch_sectioned.append([pitch_event])
        current_pos = pitch_event.x
    pit: list[ControlEvent] = []
    pbs: list[ControlEvent] = []
    for section in pitch_sectioned:
        if len(section):
            max_abs_value = max(abs(point.y / 100) for point in section)
            pbs_for_this_section = min(math.ceil(max_abs_value), MAX_PITCH_BEND_SENSITIVITY)
            if pbs_for_this_section > DEFAULT_PITCH_BEND_SENSITIVITY:
                pbs.extend(
                    (
                        ControlEvent(
                            section[-1][0] + MIN_BREAK_LENGTH_BETWEEN_PITCH_SECTIONS // 2,
                            DEFAULT_PITCH_BEND_SENSITIVITY,
                        ),
                    )
                )
            else:
                pbs_for_this_section = DEFAULT_PITCH_BEND_SENSITIVITY
            pit.extend(
                ControlEvent(
                    pitch_pos,
                    int(
                        clamp(
                            pitch_value
                            * (PITCH_MAX_VALUE if pitch_value > 0 else (PITCH_MAX_VALUE + 1))
                            / 100
                            / pbs_for_this_section,
                            -PITCH_MAX_VALUE - 1,
                            PITCH_MAX_VALUE,
                        )
                    ),
                )
                for pitch_pos, pitch_value in section
            )
    return MIDIPitchData(pit=pit, pbs=pbs)
