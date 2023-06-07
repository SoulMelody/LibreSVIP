import datetime
from dataclasses import dataclass, field

from typing_extensions import Self

from ..model import USTXProject, UTimeSignature


@dataclass
class TimeSigSegment:
    bar_pos: int
    tick_pos: int
    beat_per_bar: int
    beat_unit: int
    ticks_per_bar: int
    ticks_per_beat: int
    bar_end: int = float('inf')
    tick_end: int = float('inf')

@dataclass
class TempoSegment:
    tick_pos: int
    beat_per_bar: int
    beat_unit: int
    bpm: float = 120
    ms_pos: float = 0
    ms_per_tick: float = 0
    ticks_per_ms: float = 0
    tick_end: int = float('inf')
    ms_end: float = float('inf')

    @property
    def ticks(self) -> int:
        return self.tick_end - self.tick_pos

@dataclass
class TimeAxis:
    time_sig_segments: list[TimeSigSegment] = field(default_factory=list)
    tempo_segments: list[TempoSegment] = field(default_factory=list)
    timestamp: int = None

    def build_segments(self, project: USTXProject):
        self.timestamp = datetime.datetime.now().timestamp()
        self.time_sig_segments.clear()
        for i in range(len(project.time_signatures)):
            timesig = project.time_signatures[i]
            pos_tick = 0
            if i > 0:
                last_bar_pos = project.time_signatures[i - 1].bar_position
                pos_tick = self.time_sig_segments[-1].tick_pos + self.time_sig_segments[-1].ticks_per_bar * (timesig.bar_position - last_bar_pos)
            else:
                assert timesig.bar_position == 0
            self.time_sig_segments.append(TimeSigSegment(
                bar_pos=timesig.bar_position,
                tick_pos=pos_tick,
                beat_per_bar=timesig.beat_per_bar,
                beat_unit=timesig.beat_unit,
                ticks_per_bar=project.resolution * 4 * timesig.beat_per_bar // timesig.beat_unit,
                ticks_per_beat=project.resolution * 4 // timesig.beat_unit,
            ))
        for i in range(len(self.time_sig_segments) - 1):
            self.time_sig_segments[i].bar_end = self.time_sig_segments[i + 1].bar_pos
            self.time_sig_segments[i].tick_end = self.time_sig_segments[i + 1].tick_pos

        self.tempo_segments.clear()
        self.tempo_segments.extend([TempoSegment(
            tick_pos=sigseg.tick_pos,
            beat_per_bar=sigseg.beat_per_bar,
            beat_unit=sigseg.beat_unit,
        ) for sigseg in self.time_sig_segments])
        for i in range(len(project.tempos)):
            tempo = project.tempos[i]
            if i == 0:
                assert tempo.position == 0
            index = next((j for j, seg in enumerate(self.tempo_segments) if seg.tick_pos >= tempo.position), -1)
            if index < 0:
                self.tempo_segments.append(TempoSegment(
                    tick_pos=tempo.position,
                    bpm=tempo.bpm,
                    beat_per_bar=self.tempo_segments[-1].beat_per_bar,
                    beat_unit=self.tempo_segments[-1].beat_unit,
                ))
            elif self.tempo_segments[index].tick_pos == tempo.position:
                self.tempo_segments[index].bpm = tempo.bpm
            else:
                self.tempo_segments.insert(index, TempoSegment(
                    tick_pos=tempo.position,
                    bpm=tempo.bpm,
                    beat_per_bar=self.tempo_segments[index - 1].beat_per_bar,
                    beat_unit=self.tempo_segments[index - 1].beat_unit,
                ))
        for i in range(len(self.tempo_segments) - 1):
            if self.tempo_segments[i + 1].bpm == 0:
                self.tempo_segments[i + 1].bpm = self.tempo_segments[i].bpm
            self.tempo_segments[i].tick_end = self.tempo_segments[i + 1].tick_pos
        for i in range(len(self.tempo_segments)):
            self.tempo_segments[i].ms_per_tick = 60.0 * 1000.0 * self.tempo_segments[i].beat_per_bar / (self.tempo_segments[i].bpm * 4 * project.resolution)
            self.tempo_segments[i].ticks_per_ms = self.tempo_segments[i].bpm * 4 * project.resolution / (60.0 * 1000.0 * self.tempo_segments[i].beat_per_bar)
            if i > 0:
                self.tempo_segments[i].ms_pos = self.tempo_segments[i - 1].ms_pos + self.tempo_segments[i - 1].ticks * self.tempo_segments[i - 1].ms_per_tick
                self.tempo_segments[i - 1].ms_end = self.tempo_segments[i].ms_pos

    def get_bpm_at_tick(self, tick: int) -> float:
        segment = next((seg for seg in self.tempo_segments if seg.tick_pos == tick or seg.tick_end > tick), None)
        return segment.bpm if segment else 0

    def tick_pos_to_ms_pos(self, tick: float) -> float:
        segment = next((seg for seg in self.tempo_segments if seg.tick_pos == tick or seg.tick_end > tick), None)
        return segment.ms_pos + segment.ms_per_tick * (tick - segment.tick_pos) if segment else 0

    def ms_pos_to_tick_pos(self, ms: float) -> int:
        segment = next((seg for seg in self.tempo_segments if seg.ms_pos == ms or seg.ms_end > ms), None)
        tick_pos = segment.tick_pos + (ms - segment.ms_pos) * segment.ticks_per_ms if segment else 0
        return round(tick_pos)

    def ticks_between_ms_pos(self, ms_pos: float, ms_end: float) -> int:
        return self.ms_pos_to_tick_pos(ms_end) - self.ms_pos_to_tick_pos(ms_pos)

    def ms_between_tick_pos(self, tick_pos: float, tick_end: float) -> float:
        return self.tick_pos_to_ms_pos(tick_end) - self.tick_pos_to_ms_pos(tick_pos)

    def tick_pos_to_bar_beat(self, tick: int) -> tuple[int, int, int]:
        segment = next((seg for seg in self.time_sig_segments if seg.tick_pos == tick or seg.tick_end > tick), None)
        bar = segment.bar_pos + (tick - segment.tick_pos) // segment.ticks_per_bar if segment else 0
        tick_in_bar = tick - segment.tick_pos - segment.ticks_per_bar * (bar - segment.bar_pos) if segment else 0
        beat = tick_in_bar // segment.ticks_per_beat if segment else 0
        remaining_ticks = tick_in_bar - beat * segment.ticks_per_beat if segment else 0
        return bar, beat, remaining_ticks

    def bar_beat_to_tick_pos(self, bar: int, beat: int) -> int:
        segment = next((seg for seg in self.time_sig_segments if seg.bar_pos == bar or seg.bar_end > bar), None)
        return segment.tick_pos + segment.ticks_per_bar * (bar - segment.bar_pos) + segment.ticks_per_beat * beat if segment else 0

    def next_bar_beat(self, bar: int, beat: int) -> tuple[int, int]:
        next_bar = bar
        next_beat = beat + 1
        segment = next((seg for seg in self.time_sig_segments if seg.bar_pos == bar or seg.bar_end > bar), None)
        if segment and next_beat >= segment.beat_per_bar:
            next_bar += 1
            next_beat = 0
        return next_bar, next_beat

    def time_signature_at_tick(self, tick: int) -> UTimeSignature:
        segment = next((seg for seg in self.time_sig_segments if seg.tick_pos == tick or seg.tick_end > tick), None)
        return UTimeSignature(
            bar_position=segment.bar_pos,
            beat_per_bar=segment.beat_per_bar,
            beat_unit=segment.beat_unit,
        ) if segment else None

    def time_signature_at_bar(self, bar: int) -> UTimeSignature:
        segment = next((seg for seg in self.time_sig_segments if seg.bar_pos == bar or seg.bar_end > bar), None)
        return UTimeSignature(
            bar_position=segment.bar_pos,
            beat_per_bar=segment.beat_per_bar,
            beat_unit=segment.beat_unit,
        ) if segment else None

    def clone(self) -> Self:
        return TimeAxis(
            time_sig_segments=self.time_sig_segments.copy(),
            tempo_segments=self.tempo_segments.copy(),
        )
