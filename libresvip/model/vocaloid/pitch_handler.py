import math
import operator
from dataclasses import dataclass

from libresvip.core.constants import MIN_BREAK_LENGTH_BETWEEN_PITCH_SECTIONS
from libresvip.core.time_interval import PiecewiseIntervalDict
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import Note, ParamCurve, TimeSignature
from libresvip.model.pitch_simulator import PitchSimulator
from libresvip.model.point import Point
from libresvip.model.portamento import PortamentoPitch
from libresvip.model.relative_pitch_curve import RelativePitchCurve
from libresvip.utils.binary.midi import (
    DEFAULT_PITCH_BEND_SENSITIVITY,
    MAX_PITCH_BEND_SENSITIVITY,
    PITCH_MAX_VALUE,
)
from libresvip.utils.music_math import clamp

from .controller_models import ControllerCurve, ControllerEvent


@dataclass
class PitchBendData:
    pit: ControllerCurve
    pbs: ControllerCurve

    def is_empty(self) -> bool:
        return self.pit.is_empty() and self.pbs.is_empty()


class VocaloidPitchHandler:
    def __init__(
        self,
        synchronizer: TimeSynchronizer,
        note_list: list[Note],
        time_signature_list: list[TimeSignature],
        first_bar_length: int,
    ) -> None:
        self.synchronizer = synchronizer
        self.note_list = note_list
        self.time_signature_list = time_signature_list
        self.first_bar_length = first_bar_length

    def combine_pit_pbs(
        self, pit: ControllerCurve, pbs: ControllerCurve
    ) -> list[tuple[int, float]]:
        all_positions = sorted({e.pos for e in pit.events} | {e.pos for e in pbs.events})

        if not all_positions:
            return []

        result = []
        current_pbs = DEFAULT_PITCH_BEND_SENSITIVITY

        for pos in all_positions:
            pbs_value = pbs.get_value_at(pos)
            if pbs_value is not None:
                current_pbs = max(1, min(pbs_value, MAX_PITCH_BEND_SENSITIVITY))

            pit_value = pit.get_value_at(pos)

            denominator = PITCH_MAX_VALUE if pit_value > 0 else (PITCH_MAX_VALUE + 1)
            pitch_cents = (pit_value / denominator) * current_pbs * 100

            result.append((pos, pitch_cents))

        return result

    def to_absolute_pitch(
        self,
        pitch_data_list: list[PitchBendData],
        part_offsets: list[int] | None = None,
        vibrato_rate_interval_dict: PiecewiseIntervalDict | None = None,
        vibrato_depth_interval_dict: PiecewiseIntervalDict | None = None,
        part_start_ticks: list[int] | None = None,
        part_end_ticks: list[int] | None = None,
    ) -> ParamCurve | None:
        if not pitch_data_list:
            return None

        if part_offsets is None:
            part_offsets = [0] * len(pitch_data_list)

        all_pitch_points: list[tuple[int, float]] = []

        for data, offset in zip(pitch_data_list, part_offsets):
            if data.is_empty():
                continue
            points = self.combine_pit_pbs(data.pit, data.pbs)
            for pos, pitch in points:
                all_pitch_points.append((pos + offset, pitch))

        if not all_pitch_points:
            return None

        all_pitch_points.sort(key=operator.itemgetter(0))
        unique_points = dict(all_pitch_points)

        points_data = [Point(x=pos, y=round(pitch)) for pos, pitch in unique_points.items()]

        if not points_data or not self.note_list:
            return None

        pitch_simulator = PitchSimulator(
            synchronizer=self.synchronizer,
            portamento=PortamentoPitch.vocaloid_portamento(),
            note_list=self.note_list,
            time_signature_list=self.time_signature_list,
        )

        result = RelativePitchCurve(self.first_bar_length).to_absolute(points_data, pitch_simulator)

        if result and result.points.root:
            result = self._apply_vibrato(
                result,
                vibrato_rate_interval_dict,
                vibrato_depth_interval_dict,
                part_offsets,
                part_start_ticks,
                part_end_ticks,
            )

        return result

    def _apply_vibrato(
        self,
        pitch: ParamCurve,
        vibrato_rate_interval_dict: PiecewiseIntervalDict | None,
        vibrato_depth_interval_dict: PiecewiseIntervalDict | None,
        part_offsets: list[int],
        part_start_ticks: list[int] | None,
        part_end_ticks: list[int] | None,
    ) -> ParamCurve:
        if vibrato_rate_interval_dict is None or vibrato_depth_interval_dict is None:
            return pitch

        if not pitch.points.root:
            return pitch

        new_points: list[Point] = []

        for point in pitch.points.root:
            tick = point.x

            in_range = False
            if part_start_ticks is not None and part_end_ticks is not None:
                for offset, start, end in zip(part_offsets, part_start_ticks, part_end_ticks):
                    if start <= tick - offset < end:
                        in_range = True
                        break
            else:
                in_range = True

            if not in_range:
                new_points.append(point)
                continue

            secs = self.synchronizer.get_actual_secs_from_ticks(tick)

            try:
                depth = vibrato_depth_interval_dict.get(secs, 0)
                rate = vibrato_rate_interval_dict.get(secs, None)

                if depth and rate:
                    vibrato_offset = depth * rate
                    new_y = point.y + round(vibrato_offset)
                    new_points.append(Point(x=point.x, y=new_y))
                else:
                    new_points.append(point)
            except (KeyError, TypeError):
                new_points.append(point)

        pitch.points.root = new_points
        return pitch

    def from_absolute_pitch(
        self,
        pitch: ParamCurve,
    ) -> PitchBendData:
        if not pitch.points.root:
            return PitchBendData(
                pit=ControllerCurve(name="pitch_bend", events=[]),
                pbs=ControllerCurve(name="pitch_bend_sens", events=[]),
            )

        pitch_simulator = PitchSimulator(
            synchronizer=self.synchronizer,
            portamento=PortamentoPitch.vocaloid_portamento(),
            note_list=self.note_list,
            time_signature_list=self.time_signature_list,
        )
        relative_data = RelativePitchCurve(self.first_bar_length).from_absolute(
            pitch.points.root, pitch_simulator
        )

        if not relative_data:
            return PitchBendData(
                pit=ControllerCurve(name="pitch_bend", events=[]),
                pbs=ControllerCurve(name="pitch_bend_sens", events=[]),
            )

        pit_events: list[ControllerEvent] = []
        pbs_events: list[ControllerEvent] = []

        sections = self._split_into_sections(relative_data)

        for section in sections:
            if not section:
                continue

            max_abs_pitch = max(abs(point.y) for point in section) / 100
            optimal_pbs = min(math.ceil(max_abs_pitch), MAX_PITCH_BEND_SENSITIVITY)
            optimal_pbs = max(optimal_pbs, DEFAULT_PITCH_BEND_SENSITIVITY)

            if optimal_pbs != DEFAULT_PITCH_BEND_SENSITIVITY:
                pbs_events.append(ControllerEvent(pos=section[0].x, value=optimal_pbs))
                pbs_events.append(
                    ControllerEvent(
                        pos=section[-1].x + MIN_BREAK_LENGTH_BETWEEN_PITCH_SECTIONS // 2,
                        value=DEFAULT_PITCH_BEND_SENSITIVITY,
                    )
                )

            for point in section:
                pit_value = int(
                    clamp(
                        point.y / 100 * PITCH_MAX_VALUE / optimal_pbs,
                        -PITCH_MAX_VALUE - 1,
                        PITCH_MAX_VALUE,
                    )
                )
                pit_events.append(ControllerEvent(pos=point.x, value=pit_value))

        return PitchBendData(
            pit=ControllerCurve(
                name="pitch_bend",
                events=pit_events,
                default_value=0,
                min_value=-8192,
                max_value=8191,
            ),
            pbs=ControllerCurve(
                name="pitch_bend_sens",
                events=pbs_events,
                default_value=DEFAULT_PITCH_BEND_SENSITIVITY,
                min_value=1,
                max_value=24,
            ),
        )

    def _split_into_sections(self, points: list[Point]) -> list[list[Point]]:
        if not points:
            return []

        sections: list[list[Point]] = [[]]
        current_pos = 0

        for point in points:
            if not sections[-1] or point.x - current_pos < MIN_BREAK_LENGTH_BETWEEN_PITCH_SECTIONS:
                sections[-1].append(point)
            else:
                sections.append([point])
            current_pos = point.x

        return [s for s in sections if s]


@dataclass
class VocaloidPartPitchData:
    start_pos: int
    pit: list[ControllerEvent]
    pbs: list[ControllerEvent]

    def to_pitch_bend_data(self) -> PitchBendData:
        return PitchBendData(
            pit=ControllerCurve(
                name="pitch_bend",
                events=self.pit,
                default_value=0,
                min_value=-8192,
                max_value=8191,
            ),
            pbs=ControllerCurve(
                name="pitch_bend_sens",
                events=self.pbs,
                default_value=DEFAULT_PITCH_BEND_SENSITIVITY,
                min_value=1,
                max_value=24,
            ),
        )


def pitch_from_vocaloid_parts(
    data_by_parts: list[VocaloidPartPitchData],
    synchronizer: TimeSynchronizer,
    note_list: list[Note],
    time_signature_list: list[TimeSignature],
    first_bar_length: int,
) -> ParamCurve | None:
    handler = VocaloidPitchHandler(
        synchronizer=synchronizer,
        note_list=note_list,
        time_signature_list=time_signature_list,
        first_bar_length=first_bar_length,
    )

    pitch_data_list = [data.to_pitch_bend_data() for data in data_by_parts]
    offsets = [data.start_pos for data in data_by_parts]

    return handler.to_absolute_pitch(pitch_data_list, offsets)


def generate_for_vocaloid(
    pitch: ParamCurve,
    notes: list[Note],
    time_signature_list: list[TimeSignature],
    first_bar_length: int,
    synchronizer: TimeSynchronizer,
) -> VocaloidPartPitchData | None:
    handler = VocaloidPitchHandler(
        synchronizer=synchronizer,
        note_list=notes,
        time_signature_list=time_signature_list,
        first_bar_length=first_bar_length,
    )

    result = handler.from_absolute_pitch(pitch)

    if result.is_empty():
        return None

    return VocaloidPartPitchData(
        start_pos=0,
        pit=result.pit.events,
        pbs=result.pbs.events,
    )
