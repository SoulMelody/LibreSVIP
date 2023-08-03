import math
from dataclasses import dataclass
from typing import Optional

from libresvip.model.base import Note, ParamCurve
from libresvip.model.relative_pitch_curve import RelativePitchCurve
from libresvip.utils import clamp

from .constants import (
    BORDER_APPEND_RADIUS,
    DEFAULT_PITCH_BEND_SENSITIVITY,
    MAX_PITCH_BEND_SENSITIVITY,
    MIN_BREAK_LENGTH_BETWEEN_PITCH_SECTIONS,
    PITCH_MAX_VALUE,
)


@dataclass
class ControlEvent:
    tick: int
    value: int


@dataclass
class MIDIPitchData:
    pit: list[ControlEvent]
    pbs: list[ControlEvent]


def generate_for_midi(pitch: ParamCurve, notes: list[Note]) -> Optional[MIDIPitchData]:
    data = RelativePitchCurve().from_absolute(
        pitch, notes, border_append_radius=BORDER_APPEND_RADIUS
    )
    if data is None:
        return None
    pitch_sectioned = [[]]
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
    pit = []
    pbs = []
    for section in pitch_sectioned:
        if len(section):
            max_abs_value = max(abs(point.y / 100) for point in section)
            pbs_for_this_section = min(
                math.ceil(max_abs_value), MAX_PITCH_BEND_SENSITIVITY
            )
            if pbs_for_this_section > DEFAULT_PITCH_BEND_SENSITIVITY:
                pbs.extend(
                    (
                        ControlEvent(
                            section[-1][0]
                            + MIN_BREAK_LENGTH_BETWEEN_PITCH_SECTIONS // 2,
                            DEFAULT_PITCH_BEND_SENSITIVITY,
                        ),
                    )
                )
            else:
                pbs_for_this_section = DEFAULT_PITCH_BEND_SENSITIVITY
            pit.extend(
                ControlEvent(
                    pitch_pos,
                    clamp(
                        round(
                            pitch_value * PITCH_MAX_VALUE / 100 / pbs_for_this_section
                        ),
                        -PITCH_MAX_VALUE,
                        PITCH_MAX_VALUE,
                    ),
                )
                for pitch_pos, pitch_value in section
            )
    return MIDIPitchData(pit=pit, pbs=pbs)
