from dataclasses import InitVar, dataclass, field

from libresvip.core.tick_counter import skip_tempo_list
from libresvip.model.base import SongTempo
from libresvip.utils.search import find_last_index


@dataclass
class TimeSynchronizer:
    is_absolute_time_code: bool = field(init=False)
    default_tempo: float = field(init=False)
    tempo_list: list[SongTempo] = field(init=False)
    ori_tempo_list: InitVar[list[SongTempo]]
    skip_ticks: InitVar[int] = 0
    _is_absolute_time_code: InitVar[bool] = False
    _default_tempo: InitVar[float] = 60

    def __post_init__(
        self,
        ori_tempo_list: list[SongTempo],
        skip_ticks: int,
        _is_absolute_time_code: bool,
        _default_tempo: float,
    ) -> None:
        if skip_ticks > 0:
            self.tempo_list = skip_tempo_list(ori_tempo_list, skip_ticks)
        else:
            self.tempo_list = ori_tempo_list
        self.is_absolute_time_code = _is_absolute_time_code
        self.default_tempo = _default_tempo

    def get_actual_ticks_from_ticks(self, ticks: int) -> float:
        if not self.is_absolute_time_code:
            return ticks
        res = 0.0
        i = 0
        while i < len(self.tempo_list) - 1 and self.tempo_list[i + 1].position < ticks:
            res += (self.tempo_list[i + 1].position - self.tempo_list[i].position) * (
                self.default_tempo / self.tempo_list[i].bpm
            )
            i += 1
        res += (ticks - self.tempo_list[i].position) * self.default_tempo / self.tempo_list[i].bpm
        return res

    def get_duration_secs_from_ticks(self, start_ticks: int, end_ticks: int) -> float:
        if self.is_absolute_time_code:
            return (
                (
                    self.get_actual_ticks_from_ticks(end_ticks)
                    - self.get_actual_ticks_from_ticks(start_ticks)
                )
                / self.default_tempo
                / 8
            )
        start_tempo_index = find_last_index(
            self.tempo_list, lambda tempo: tempo.position <= start_ticks
        )
        end_tempo_index = find_last_index(
            self.tempo_list, lambda tempo: tempo.position <= end_ticks
        )
        if start_tempo_index == end_tempo_index or end_tempo_index == -1:
            return (end_ticks - start_ticks) / self.tempo_list[start_tempo_index].bpm / 8
        secs = 0.0
        secs += (
            (self.tempo_list[start_tempo_index + 1].position - start_ticks)
            / self.tempo_list[start_tempo_index].bpm
            / 8
        )
        for i in range(start_tempo_index + 1, end_tempo_index):
            secs += (
                (self.tempo_list[i + 1].position - self.tempo_list[i].position)
                / float(self.tempo_list[i].bpm)
                / 8
            )
        secs += (
            (end_ticks - self.tempo_list[end_tempo_index].position)
            / float(self.tempo_list[end_tempo_index].bpm)
            / 8
        )
        return secs

    def get_actual_ticks_from_secs_offset(self, start_ticks: int, offset_secs: float) -> float:
        if self.is_absolute_time_code:
            return (
                self.get_actual_ticks_from_ticks(start_ticks) + offset_secs * self.default_tempo * 8
            )
        start_tempo_index = find_last_index(
            self.tempo_list, lambda tempo: tempo.position <= start_ticks
        )
        ticks: float = start_ticks
        secs = offset_secs
        for i in range(start_tempo_index, len(self.tempo_list) - 1):
            dur = (self.tempo_list[i + 1].position - ticks) / self.tempo_list[i].bpm / 8
            if dur < secs:
                ticks = self.tempo_list[i + 1].position
                secs -= dur
            else:
                ticks += (self.tempo_list[i + 1].position - ticks) * secs / dur
                return ticks
        ticks += self.tempo_list[-1].bpm * secs * 8
        return ticks

    def get_actual_ticks_from_secs(self, secs: float) -> float:
        return self.get_actual_ticks_from_secs_offset(0, secs)

    def get_actual_secs_from_ticks(self, ticks: int) -> float:
        return self.get_duration_secs_from_ticks(0, ticks)
