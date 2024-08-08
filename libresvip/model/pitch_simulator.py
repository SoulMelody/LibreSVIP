import dataclasses
import functools
from typing import Optional

import portion

from libresvip.core.time_interval import PiecewiseIntervalDict
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import Note
from libresvip.model.portamento import PortamentoPitch


@dataclasses.dataclass
class PitchSimulator:
    synchronizer: TimeSynchronizer
    portamento: PortamentoPitch
    note_list: dataclasses.InitVar[list[Note]]
    interval_dict: PiecewiseIntervalDict = dataclasses.field(default_factory=PiecewiseIntervalDict)

    def __post_init__(self, note_list: list[Note]) -> None:
        if not note_list:
            return
        max_portamento_time = self.portamento.max_inter_time_in_secs
        max_portamento_percent = self.portamento.max_inter_time_percent

        current_note = note_list[0]
        current_head = self.synchronizer.get_actual_secs_from_ticks(current_note.start_pos)
        current_dur = self.synchronizer.get_duration_secs_from_ticks(
            current_note.start_pos, current_note.end_pos
        )
        current_portamento = min(current_dur * max_portamento_percent, max_portamento_time)

        self.interval_dict[portion.closedopen(0.0, current_head)] = current_note.key_number
        prev_portamento_end = current_head
        for next_note in note_list[1:]:
            next_head = self.synchronizer.get_actual_secs_from_ticks(next_note.start_pos)
            next_dur = self.synchronizer.get_duration_secs_from_ticks(
                next_note.start_pos, next_note.end_pos
            )
            next_portamento = min(next_dur * max_portamento_percent, max_portamento_time)
            interval = (
                0.0 if next_note.lyric == "-" else (next_head - current_head - current_dur) / 2
            ) - self.portamento.offset
            if interval <= max_portamento_time:
                current_portamento_start = next_head - interval - current_portamento
                current_portamento_end = next_head - interval + next_portamento
            else:
                current_portamento_start = next_head - interval - max_portamento_time
                current_portamento_end = next_head - interval + max_portamento_time
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
        self.interval_dict[portion.closedopen(prev_portamento_end, portion.inf)] = (
            current_note.key_number
        )

    def pitch_at_ticks(self, ticks: int) -> Optional[float]:
        return self.pitch_at_secs(self.synchronizer.get_actual_secs_from_ticks(ticks))

    def pitch_at_secs(self, secs: float) -> Optional[float]:
        if value := self.interval_dict.get(secs):
            return value * 100
