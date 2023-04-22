import dataclasses
import datetime

import regex as re
from pysrt import SubRipItem

from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import Note, Project, SingingTrack

from .options import OutputOptions, SplitOption

SYMBOL_PATTERN = re.compile(r"(?!-)\p{punct}+")


@dataclasses.dataclass
class SrtGenerator:
    options: OutputOptions
    synchronizer: TimeSynchronizer = dataclasses.field(init=False)

    def generate_project(self, project: Project) -> list[SubRipItem]:
        self.synchronizer = TimeSynchronizer(project.song_tempo_list)
        singing_track = next(
            track for track in project.track_list if isinstance(track, SingingTrack)
        )
        note_list = singing_track.note_list
        buffer = []
        lyric_lines = []
        for i, note in enumerate(note_list):
            buffer.append(note)
            commit_flag = False
            condition_symbol = SYMBOL_PATTERN.search(note.lyric) is not None
            condition_gap = (
                i + 1 < len(note_list)
                and note_list[i + 1].start_pos - note.end_pos >= 60
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

    def commit_current_lyric_line(
        self, lyric_lines: list[SubRipItem], buffer: list[Note]
    ):
        start_time = self.get_time_from_ticks(buffer[0].start_pos)
        end_time = self.get_time_from_ticks(buffer[-1].end_pos)
        lyrics = ""
        for note in buffer:
            lyrics += SYMBOL_PATTERN.sub("", note.lyric)
        lyric_lines.append(
            SubRipItem(
                index=len(lyric_lines) + 1,
                start=start_time,
                end=end_time,
                text=lyrics,
            )
        )

    def get_time_from_ticks(self, ticks: int) -> datetime.time:
        date_time = datetime.datetime.fromtimestamp(
            self.synchronizer.get_actual_secs_from_ticks(ticks)
        )
        return datetime.time(
            hour=date_time.hour,
            minute=date_time.minute,
            second=date_time.second,
            microsecond=date_time.microsecond,
        )
