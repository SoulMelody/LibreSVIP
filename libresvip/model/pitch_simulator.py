import dataclasses
import functools
import itertools
from typing import NamedTuple

import more_itertools
import portion

from libresvip.core.constants import MIN_BREAK_LENGTH_BETWEEN_PITCH_SECTIONS
from libresvip.core.exceptions import NotesOverlappedError
from libresvip.core.tick_counter import find_bar_index
from libresvip.core.time_interval import PiecewiseIntervalDict
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import Note, ParamCurve, TimeSignature
from libresvip.model.portamento import PortamentoPitch
from libresvip.utils.music_math import linear_interpolation
from libresvip.utils.translation import gettext_lazy as _


class PitchIntervalSegment(NamedTuple):
    start: float
    end: float
    start_value: int
    end_value: int


@dataclasses.dataclass
class PitchSimulator:
    synchronizer: TimeSynchronizer
    portamento: PortamentoPitch
    note_list: dataclasses.InitVar[list[Note]]
    time_signature_list: dataclasses.InitVar[list[TimeSignature]]
    interval_dict: PiecewiseIntervalDict = dataclasses.field(default_factory=PiecewiseIntervalDict)
    pitch_interval_dict: PiecewiseIntervalDict | None = dataclasses.field(default=None)
    pitch_interval_segments: list[PitchIntervalSegment] = dataclasses.field(default_factory=list)
    pitch_interval_starts: list[float] = dataclasses.field(default_factory=list)
    pitch_interval_ends: list[float] = dataclasses.field(default_factory=list)

    def __post_init__(
        self, note_list: list[Note], time_signature_list: list[TimeSignature]
    ) -> None:
        if not note_list:
            return
        current_note = note_list[0]
        max_portamento_percent = self.portamento.max_inter_time_percent

        def vocaloid_max_portamento(note: Note) -> tuple[float, float]:
            max_portamento_ticks = max_portamento_percent * note.length
            if max_portamento_ticks >= 60:
                max_portamento_ticks = 60
            elif note.length <= 120:
                max_portamento_ticks = note.length / 2
            max_portamento_time = self.synchronizer.get_duration_secs_from_ticks(
                int(note.end_pos - max_portamento_ticks * 1.4),
                int(note.end_pos - max_portamento_ticks * 0.4),
            )
            return max_portamento_ticks, max_portamento_time

        if self.portamento.vocaloid_mode:
            max_portamento_ticks, max_portamento_time = vocaloid_max_portamento(current_note)
        else:
            max_portamento_ticks = 0
            max_portamento_time = self.portamento.max_inter_time_in_secs

        current_head = self.synchronizer.get_actual_secs_from_ticks(current_note.start_pos)
        current_dur = self.synchronizer.get_duration_secs_from_ticks(
            current_note.start_pos, current_note.end_pos
        )
        current_portamento = min(current_dur * max_portamento_percent, max_portamento_time)

        self.interval_dict[portion.closedopen(0.0, current_head)] = current_note.key_number
        prev_portamento_end = current_head
        for next_note in note_list[1:]:
            if current_note.end_pos > next_note.start_pos:
                msg = _("Notes overlapped near bar {}").format(
                    find_bar_index(time_signature_list, next_note.start_pos)
                )
                raise NotesOverlappedError(msg)
            elif (
                self.portamento.vocaloid_mode
                and next_note.start_pos - current_note.end_pos
                >= MIN_BREAK_LENGTH_BETWEEN_PITCH_SECTIONS
            ):
                max_portamento_time = 0
            next_head = self.synchronizer.get_actual_secs_from_ticks(next_note.start_pos)
            next_dur = self.synchronizer.get_duration_secs_from_ticks(
                next_note.start_pos, next_note.end_pos
            )
            if self.portamento.vocaloid_mode and next_note.start_pos > current_note.end_pos:
                current_tail = self.synchronizer.get_actual_secs_from_ticks(current_note.end_pos)
                if prev_portamento_end < current_tail:
                    self.interval_dict[portion.closedopen(prev_portamento_end, current_tail)] = (
                        current_note.key_number
                    )
                current_note = next_note
                current_head = next_head
                current_dur = next_dur
                max_portamento_ticks, max_portamento_time = vocaloid_max_portamento(current_note)
                current_portamento = min(current_dur * max_portamento_percent, max_portamento_time)
                prev_portamento_end = current_head
                continue
            next_portamento = min(next_dur * max_portamento_percent, max_portamento_time)
            if self.portamento.vocaloid_mode:
                middle_pos = (
                    current_note.end_pos
                    if next_note.lyric == "-"
                    else (next_note.start_pos + current_note.end_pos) / 2
                ) - max_portamento_ticks * 0.4
                interval = self.synchronizer.get_duration_secs_from_ticks(
                    int(middle_pos - max_portamento_ticks),
                    int(middle_pos),
                )
                middle_time = self.synchronizer.get_actual_secs_from_ticks(int(middle_pos))
            else:
                interval = (next_head - current_head - current_dur) / 2
                middle_time = (next_head + current_head + current_dur) / 2
            if interval <= max_portamento_time:
                current_portamento_start = middle_time - current_portamento
                current_portamento_end = middle_time + next_portamento
            else:
                current_portamento_start = middle_time - max_portamento_time
                current_portamento_end = middle_time + max_portamento_time
            self.interval_dict[
                portion.closedopen(prev_portamento_end, current_portamento_start)
            ] = current_note.key_number
            if current_note.key_number == next_note.key_number:
                self.interval_dict[
                    portion.closedopen(current_portamento_start, current_portamento_end)
                ] = current_note.key_number
            elif current_portamento_start < current_portamento_end:
                self.interval_dict[
                    portion.closedopen(current_portamento_start, current_portamento_end)
                ] = functools.partial(  # type: ignore[call-arg]
                    self.portamento.inter_func,
                    start=(current_portamento_start, current_note.key_number),
                    end=(current_portamento_end, next_note.key_number),
                )
            current_note = next_note
            current_head = next_head
            current_dur = next_dur
            current_portamento = next_portamento
            prev_portamento_end = current_portamento_end
            if self.portamento.vocaloid_mode:
                max_portamento_ticks, max_portamento_time = vocaloid_max_portamento(current_note)
        self.interval_dict[portion.closedopen(prev_portamento_end, portion.inf)] = (
            current_note.key_number
        )

    def merge_pitch_curve(self, pitch_curve: ParamCurve, first_bar_length: int) -> None:
        self.pitch_interval_dict = PiecewiseIntervalDict()
        self.pitch_interval_segments = []
        for point_part in more_itertools.split_at(
            pitch_curve.points.root, lambda point: point.y == -100
        ):
            if len(point_part):
                for prev_point, point in itertools.pairwise(point_part):
                    start_time = self.synchronizer.get_actual_secs_from_ticks(
                        prev_point.x - first_bar_length
                    )
                    end_time = self.synchronizer.get_actual_secs_from_ticks(
                        point.x - first_bar_length
                    )
                    if start_time >= end_time:
                        continue
                    interval = portion.closedopen(start_time, end_time)
                    self.pitch_interval_dict[interval] = functools.partial(
                        linear_interpolation,  # type: ignore[call-arg]
                        start=(start_time, prev_point.y),
                        end=(end_time, point.y),
                    )
                    self.pitch_interval_segments.append(
                        PitchIntervalSegment(
                            start=start_time,
                            end=end_time,
                            start_value=prev_point.y,
                            end_value=point.y,
                        )
                    )
        self.pitch_interval_starts = [segment.start for segment in self.pitch_interval_segments]
        self.pitch_interval_ends = [segment.end for segment in self.pitch_interval_segments]

    def pitch_at_ticks(self, ticks: int) -> float | None:
        return self.pitch_at_secs(self.synchronizer.get_actual_secs_from_ticks(ticks))

    def pitch_at_ticks_batch(self, ticks_list: list[int]) -> list[float | None]:
        if not ticks_list:
            return []
        secs_list = self.synchronizer.get_actual_secs_from_ticks_batch(ticks_list)
        return self.pitch_at_secs_batch(secs_list)

    def pitch_at_secs_batch(self, secs_list: list[float]) -> list[float | None]:
        if not secs_list:
            return []
        if len(secs_list) == 1:
            return [self.pitch_at_secs(secs_list[0])]
        if any(current < previous for previous, current in itertools.pairwise(secs_list)):
            return [self.pitch_at_secs(secs) for secs in secs_list]
        return [self._pitch_at_secs_with_ordered_lookup(secs) for secs in secs_list]

    def pitch_at_secs(self, secs: float) -> float | None:
        return self._pitch_at_secs_with_ordered_lookup(secs)

    def _pitch_at_secs_with_ordered_lookup(self, secs: float) -> float | None:
        if (value := self._pitch_override_at_secs(secs)) is not None:
            return value
        if value := self.interval_dict.get(secs):
            return value * 100
        return None

    def _pitch_override_at_secs(self, secs: float) -> float | None:
        if self.pitch_interval_segments:
            index = self._find_pitch_interval_index(secs)
            if index is not None:
                segment = self.pitch_interval_segments[index]
                return linear_interpolation(
                    secs,
                    start=(segment.start, segment.start_value),
                    end=(segment.end, segment.end_value),
                )
        if self.pitch_interval_dict is not None and (value := self.pitch_interval_dict.get(secs)):
            return value
        return None

    def _find_pitch_interval_index(self, secs: float) -> int | None:
        if not self.pitch_interval_segments:
            return None
        left = 0
        right = len(self.pitch_interval_segments) - 1
        while left <= right:
            middle = (left + right) // 2
            if secs < self.pitch_interval_starts[middle]:
                right = middle - 1
            elif secs >= self.pitch_interval_ends[middle]:
                left = middle + 1
            else:
                return middle
        return None
