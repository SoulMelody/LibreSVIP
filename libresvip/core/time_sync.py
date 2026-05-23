import bisect
from dataclasses import InitVar, dataclass, field

from libresvip.core.tick_counter import skip_tempo_list
from libresvip.model.base import SongTempo


@dataclass
class TimeSynchronizer:
    is_absolute_time_code: bool = field(init=False)
    default_tempo: float = field(init=False)
    tempo_list: list[SongTempo] = field(init=False)
    _positions: list[int] = field(init=False)
    _cum_secs: list[float] = field(init=False)
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

        n = len(self.tempo_list)
        self._positions = [t.position for t in self.tempo_list]
        self._cum_secs = [0.0] * n
        for i in range(1, n):
            dt = self._positions[i] - self._positions[i - 1]
            self._cum_secs[i] = self._cum_secs[i - 1] + dt / self.tempo_list[i - 1].bpm / 8

    def _secs_at_tick(self, ticks: int) -> float:
        idx = bisect.bisect_right(self._positions, ticks) - 1
        if idx < 0:
            idx = 0
        return self._cum_secs[idx] + (ticks - self._positions[idx]) / self.tempo_list[idx].bpm / 8

    def _ticks_at_secs(self, secs: float) -> float:
        idx = bisect.bisect_right(self._cum_secs, secs) - 1
        if idx < 0:
            idx = 0
        return self._positions[idx] + (secs - self._cum_secs[idx]) * self.tempo_list[idx].bpm * 8

    def get_actual_ticks_from_ticks(self, ticks: int) -> float:
        if not self.is_absolute_time_code:
            return ticks
        res = 0.0
        idx = bisect.bisect_right(self._positions, ticks) - 1
        if idx < 0:
            idx = 0
        for i in range(idx):
            res += (self._positions[i + 1] - self._positions[i]) * (
                self.default_tempo / self.tempo_list[i].bpm
            )
        res += (ticks - self._positions[idx]) * self.default_tempo / self.tempo_list[idx].bpm
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
        return self._secs_at_tick(end_ticks) - self._secs_at_tick(start_ticks)

    def get_actual_ticks_from_secs_offset(self, start_ticks: int, offset_secs: float) -> float:
        if self.is_absolute_time_code:
            return (
                self.get_actual_ticks_from_ticks(start_ticks) + offset_secs * self.default_tempo * 8
            )
        target_secs = self._secs_at_tick(start_ticks) + offset_secs
        return self._ticks_at_secs(target_secs)

    def get_actual_ticks_from_secs(self, secs: float) -> float:
        return self.get_actual_ticks_from_secs_offset(0, secs)

    def get_actual_secs_from_ticks(self, ticks: int) -> float:
        return self.get_duration_secs_from_ticks(0, ticks)
