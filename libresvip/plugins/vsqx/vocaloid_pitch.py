import math
from dataclasses import dataclass
from typing import Optional

from libresvip.model.base import Note, ParamCurve, Point, Points
from libresvip.model.relative_pitch_curve import RelativePitchCurve

from .constants import (
    BORDER_APPEND_RADIUS,
    DEFAULT_PITCH_BEND_SENSITIVITY,
    MIN_BREAK_LENGTH_BETWEEN_PITCH_SECTIONS,
    PITCH_MAX_VALUE,
)


@dataclass
class ControllerEvent:
    pos: int
    value: int


@dataclass
class VocaloidPartPitchData:
    start_pos: int
    pit: list[ControllerEvent]
    pbs: list[ControllerEvent]


def pitch_from_vocaloid_parts(data_by_parts: list[VocaloidPartPitchData], note_list: list[Note]) -> Optional[ParamCurve]:
    pitch_raw_data_by_part = []
    for part in data_by_parts:
        pit = part.pit
        pbs = part.pbs
        pit_multiplied_by_pbs = {}
        pit_index = 0
        pbs_current_value = DEFAULT_PITCH_BEND_SENSITIVITY
        for pbs_event in pbs:
            for i in range(pit_index, len(pit)):
                pit_event = pit[i]
                if pit_event.pos < pbs_event.pos:
                    pit_multiplied_by_pbs[pit_event.pos] = pit_event.value * pbs_current_value
                    if i == len(pit) - 1:
                        pit_index = i
                else:
                    pit_index = i
                    break
            pbs_current_value = pbs_event.value
        if pit_index < len(pit) - 1:
            for i in range(pit_index, len(pit)):
                pit_event = pit[i]
                pit_multiplied_by_pbs[pit_event.pos] = pit_event.value * pbs_current_value
        pitch_raw_data_by_part.append({k + part.start_pos: v for k, v in pit_multiplied_by_pbs.items()})
    pitch_raw_data = []
    for element in pitch_raw_data_by_part:
        first_pos = next(iter(element), None)
        if first_pos is None:
            continue
        first_invalid_index_in_previous = next((i for i, x in enumerate(pitch_raw_data) if x[0] >= first_pos), None)
        if first_invalid_index_in_previous is None:
            pitch_raw_data += element.items()
        else:
            pitch_raw_data = pitch_raw_data[:first_invalid_index_in_previous] + element.items()
    data = [Point(x=pos, y=round((value / PITCH_MAX_VALUE) * 100)) for pos, value in pitch_raw_data]
    return RelativePitchCurve(points=Points(
        root=data
    )).to_absolute(note_list) if data and note_list else None

def generate_for_vocaloid(pitch: ParamCurve, notes: list[Note]) -> Optional[VocaloidPartPitchData]:
    data = RelativePitchCurve.from_absolute(pitch, notes, border_append_radius=BORDER_APPEND_RADIUS)
    if data is None:
        return None
    pitch_sectioned = [[]]
    current_pos = 0
    for pitch_event in data.points:
        if (
            not pitch_sectioned[-1]
            or pitch_event.x - current_pos
            < MIN_BREAK_LENGTH_BETWEEN_PITCH_SECTIONS
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
            pbs_for_this_section = math.ceil(max_abs_value)
            if pbs_for_this_section > DEFAULT_PITCH_BEND_SENSITIVITY:
                pbs.extend(
                    (
                        ControllerEvent(section[0][0], pbs_for_this_section),
                        ControllerEvent(
                            section[-1][0]
                            + MIN_BREAK_LENGTH_BETWEEN_PITCH_SECTIONS // 2,
                            DEFAULT_PITCH_BEND_SENSITIVITY,
                        ),
                    )
                )
            else:
                pbs_for_this_section = DEFAULT_PITCH_BEND_SENSITIVITY
            pit.extend(
                ControllerEvent(
                    pitch_pos,
                    min(
                        max(
                            round(
                                pitch_value
                                * PITCH_MAX_VALUE
                                / 100
                                / pbs_for_this_section
                            ),
                            -PITCH_MAX_VALUE,
                        ),
                        PITCH_MAX_VALUE,
                    ),
                )
                for pitch_pos, pitch_value in section
            )
    return VocaloidPartPitchData(start_pos=0, pit=pit, pbs=pbs)
