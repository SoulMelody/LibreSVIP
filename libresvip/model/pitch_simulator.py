import dataclasses
import functools
from typing import Optional

import portion

from libresvip.core.constants import MIN_BREAK_LENGTH_BETWEEN_PITCH_SECTIONS
from libresvip.core.exceptions import NotesOverlappedError
from libresvip.core.time_interval import PiecewiseIntervalDict
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import Note
from libresvip.model.portamento import PortamentoPitch
from libresvip.utils.translation import gettext_lazy as _


@dataclasses.dataclass
class PitchSimulator:
    synchronizer: TimeSynchronizer
    portamento: PortamentoPitch
    note_list: dataclasses.InitVar[list[Note]]
    interval_dict: PiecewiseIntervalDict = dataclasses.field(default_factory=PiecewiseIntervalDict)

    def __post_init__(self, note_list: list[Note]) -> None:
        if not note_list:
            return
        current_note = note_list[0]
        max_portamento_percent = self.portamento.max_inter_time_percent
        if self.portamento.vocaloid_mode:
            max_portamento_ticks = max_portamento_percent * current_note.length
            if max_portamento_ticks >= 60:
                max_portamento_ticks = 60
            elif current_note.length <= 120:
                max_portamento_ticks = current_note.length / 2
            max_portamento_time = self.synchronizer.get_duration_secs_from_ticks(
                int(current_note.end_pos - max_portamento_ticks * 1.4),
                int(current_note.end_pos - max_portamento_ticks * 0.4),
            )
        else:
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
                msg = _("Notes Overlapped")
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
            next_portamento = min(next_dur * max_portamento_percent, max_portamento_time)
            if self.portamento.vocaloid_mode:
                middle_pos = (
                    current_note.end_pos
                    if next_note.lyric == "-"
                    else (next_note.start_pos + current_note.end_pos) / 2
                ) - max_portamento_ticks * 0.4
                interval = self.synchronizer.get_duration_secs_from_ticks(
                    int(middle_pos - max_portamento_ticks), int(middle_pos)
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
                max_portamento_ticks = max_portamento_percent * current_note.length
                if max_portamento_ticks >= 60:
                    max_portamento_ticks = 60
                elif current_note.length <= 120:
                    max_portamento_ticks = current_note.length / 2
                max_portamento_time = self.synchronizer.get_duration_secs_from_ticks(
                    int(middle_pos - max_portamento_ticks * 1.4),
                    int(middle_pos - max_portamento_ticks * 0.4),
                )
        self.interval_dict[portion.closedopen(prev_portamento_end, portion.inf)] = (
            current_note.key_number
        )

    def pitch_at_ticks(self, ticks: int) -> Optional[float]:
        return self.pitch_at_secs(self.synchronizer.get_actual_secs_from_ticks(ticks))

    def pitch_at_secs(self, secs: float) -> Optional[float]:
        if value := self.interval_dict.get(secs):
            return value * 100
