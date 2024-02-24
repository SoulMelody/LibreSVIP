import dataclasses
import datetime

from srt import Subtitle

from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import Note, Project, SingingTrack
from libresvip.utils.text import SYMBOL_PATTERN

from .options import OutputOptions, SplitOption


@dataclasses.dataclass
class SrtGenerator:
    options: OutputOptions
    synchronizer: TimeSynchronizer = dataclasses.field(init=False)

    def generate_project(self, project: Project) -> list[Subtitle]:
        self.synchronizer = TimeSynchronizer(project.song_tempo_list)
        if self.options.track_index == -1:
            singing_track = next(
                track for track in project.track_list if isinstance(track, SingingTrack)
            )
        else:
            singing_track = project.track_list[self.options.track_index]
        note_list = singing_track.note_list
        buffer = []
        lyric_lines: list[Subtitle] = []
        for i, note in enumerate(note_list):
            buffer.append(note)
            commit_flag = False
            condition_symbol = SYMBOL_PATTERN.search(note.lyric) is not None
            condition_gap = (
                i + 1 < len(note_list) and note_list[i + 1].start_pos - note.end_pos >= 60
            )
            if self.options.split_by == SplitOption.SYMBOL:
                commit_flag = condition_symbol
            elif self.options.split_by == SplitOption.GAP:
                commit_flag = condition_gap
            elif self.options.split_by == SplitOption.BOTH:
                commit_flag = condition_symbol or condition_gap
            if i + 1 == len(note_list):
                commit_flag = True
            if commit_flag:
                self.commit_current_lyric_line(lyric_lines, buffer)
                buffer = []
        return lyric_lines

    def commit_current_lyric_line(self, lyric_lines: list[Subtitle], buffer: list[Note]) -> None:
        start_time = self.get_time_from_ticks(buffer[0].start_pos)
        end_time = self.get_time_from_ticks(buffer[-1].end_pos)
        lyrics = "".join(SYMBOL_PATTERN.sub("", note.lyric) for note in buffer)
        lyric_lines.append(
            Subtitle(
                index=len(lyric_lines) + 1,
                start=start_time,
                end=end_time,
                content=lyrics,
            )
        )

    def get_time_from_ticks(self, ticks: int) -> datetime.timedelta:
        seconds = self.synchronizer.get_actual_secs_from_ticks(ticks)
        seconds_int = int(seconds)
        milliseconds = (seconds % 1) * 1000
        return datetime.timedelta(seconds=seconds_int, milliseconds=milliseconds)
