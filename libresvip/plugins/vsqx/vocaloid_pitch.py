import math
from dataclasses import dataclass
from typing import Optional

from libresvip.core.constants import (
    DEFAULT_PITCH_BEND_SENSITIVITY,
    MAX_PITCH_BEND_SENSITIVITY,
    MIN_BREAK_LENGTH_BETWEEN_PITCH_SECTIONS,
    PITCH_MAX_VALUE,
)
from libresvip.core.time_interval import PiecewiseIntervalDict
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import Note, ParamCurve
from libresvip.model.pitch_simulator import PitchSimulator
from libresvip.model.point import Point
from libresvip.model.portamento import PortamentoPitch
from libresvip.model.relative_pitch_curve import RelativePitchCurve
from libresvip.utils.music_math import clamp


@dataclass
class ControllerEvent:
    pos: int
    value: int


@dataclass
class VocaloidPartPitchData:
    start_pos: int
    pit: list[ControllerEvent]
    pbs: list[ControllerEvent]


def pitch_from_vocaloid_parts(
    data_by_parts: list[VocaloidPartPitchData],
    synchronizer: TimeSynchronizer,
    note_list: list[Note],
    vibrato_rate_interval_dict: PiecewiseIntervalDict,
    vibrato_depth_interval_dict: PiecewiseIntervalDict,
    first_bar_length: int,
    lower_bound: int,
    upper_bound: int,
) -> Optional[ParamCurve]:
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
                    pit_multiplied_by_pbs[pit_event.pos + part.start_pos] = (
                        pit_event.value * pbs_current_value
                    )
                    if i == len(pit) - 1:
                        pit_index = i
                else:
                    pit_index = i
                    break
            pbs_current_value = pbs_event.value
        if pit_index < len(pit) - 1:
            for i in range(pit_index, len(pit)):
                pit_event = pit[i]
                pit_multiplied_by_pbs[pit_event.pos + part.start_pos] = (
                    pit_event.value * pbs_current_value
                )
        pitch_raw_data_by_part.append(pit_multiplied_by_pbs)
    pitch_raw_data: list[tuple[int, int]] = []
    for element in pitch_raw_data_by_part:
        first_pos = next(iter(element), None)
        if first_pos is None:
            continue
        first_invalid_index_in_previous = next(
            (i for i, x in enumerate(pitch_raw_data) if x[0] >= first_pos),
            None,
        )
        if first_invalid_index_in_previous is None:
            pitch_raw_data += list(element.items())
        else:
            pitch_raw_data = pitch_raw_data[:first_invalid_index_in_previous] + list(
                element.items()
            )
    data = []
    prev_pos = None
    value = None
    for pos, pitch in pitch_raw_data:
        pos_secs = synchronizer.get_actual_secs_from_ticks(pos)
        if prev_pos is not None and value is not None:
            for interp_pos in range(prev_pos + 5, pos, 5):
                interp_pos_secs = synchronizer.get_actual_secs_from_ticks(interp_pos)
                if interp_value_diff := vibrato_rate_interval_dict.get(interp_pos_secs, 0):
                    interp_value_diff *= vibrato_depth_interval_dict.get(interp_pos_secs, 64)
                data.append(
                    Point(
                        x=interp_pos,
                        y=value + round(interp_value_diff),
                    )
                )
        value = round((pitch / (PITCH_MAX_VALUE if pitch > 0 else (PITCH_MAX_VALUE + 1))) * 100)
        if value_diff := vibrato_rate_interval_dict.get(pos_secs, 0):
            value_diff *= vibrato_depth_interval_dict.get(pos_secs, 64)
        data.append(
            Point(
                x=pos,
                y=value + round(value_diff),
            )
        )
        prev_pos = pos
    pitch_simulator = PitchSimulator(
        synchronizer=synchronizer,
        portamento=PortamentoPitch.vocaloid_portamento(),
        note_list=note_list,
    )
    return (
        RelativePitchCurve(first_bar_length, lower_bound, upper_bound).to_absolute(
            data, pitch_simulator
        )
        if data and note_list
        else None
    )


def generate_for_vocaloid(
    pitch: ParamCurve,
    notes: list[Note],
    first_bar_length: int,
    synchronizer: TimeSynchronizer,
) -> Optional[VocaloidPartPitchData]:
    pitch_simulator = PitchSimulator(
        synchronizer=synchronizer,
        portamento=PortamentoPitch.vocaloid_portamento(),
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
    pit: list[ControllerEvent] = []
    pbs: list[ControllerEvent] = []
    for section in pitch_sectioned:
        if len(section):
            max_abs_value = max(abs(point.y / 100) for point in section)
            pbs_for_this_section = min(math.ceil(max_abs_value), MAX_PITCH_BEND_SENSITIVITY)
            if pbs_for_this_section > DEFAULT_PITCH_BEND_SENSITIVITY:
                pbs.extend(
                    (
                        ControllerEvent(section[0][0], pbs_for_this_section),
                        ControllerEvent(
                            section[-1][0] + MIN_BREAK_LENGTH_BETWEEN_PITCH_SECTIONS // 2,
                            DEFAULT_PITCH_BEND_SENSITIVITY,
                        ),
                    )
                )
            else:
                pbs_for_this_section = DEFAULT_PITCH_BEND_SENSITIVITY
            pit.extend(
                ControllerEvent(
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
    return VocaloidPartPitchData(start_pos=0, pit=pit, pbs=pbs)
