import dataclasses
import datetime

from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import Project, SingingTrack
from libresvip.utils.text import SYMBOL_PATTERN

from .model import (
    AlbumInfoTag,
    ArtistInfoTag,
    ByInfoTag,
    LrcFile,
    LyricLine,
    OffsetInfoTag,
    TimeTag,
    TitleInfoTag,
)
from .options import OffsetPolicyOption, OutputOptions, SplitOption


@dataclasses.dataclass
class LrcGenerator:
    options: OutputOptions
    synchronizer: TimeSynchronizer = dataclasses.field(init=False)

    def generate_project(self, project: Project) -> LrcFile:
        self.synchronizer = TimeSynchronizer(project.song_tempo_list)
        singing_track = next(
            track for track in project.track_list if isinstance(track, SingingTrack)
        )
        note_list = singing_track.note_list
        buffer = []
        lyric_lines: list[LyricLine] = []
        for i, note in enumerate(note_list):
            buffer.append((note.start_pos, note.lyric))
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
        info_tags = []
        if self.options.title:
            info_tags.append(TitleInfoTag(value=self.options.title))
        if self.options.artist:
            info_tags.append(ArtistInfoTag(value=self.options.artist))
        if self.options.album:
            info_tags.append(AlbumInfoTag(value=self.options.album))
        if self.options.by:
            info_tags.append(ByInfoTag(value=self.options.by))
        if self.options.offset_policy == OffsetPolicyOption.TIMELINE:
            for line in lyric_lines:
                for time_tag in line.time_tags:
                    ori_time = datetime.datetime(
                        year=1970,
                        month=1,
                        day=1,
                        minute=time_tag.minute,
                        second=time_tag.second,
                        microsecond=time_tag.percent_second * 10,
                        tzinfo=datetime.timezone.utc,
                    )
                    ori_time += datetime.timedelta(microseconds=-self.options.offset)
                    time_tag.minute = ori_time.minute
                    time_tag.second = ori_time.second
                    time_tag.percent_second = round(ori_time.microsecond / 10)
        elif self.options.offset_policy == OffsetPolicyOption.META:
            info_tags.append(OffsetInfoTag(value=str(self.options.offset)))
        lyric_file = LrcFile(
            lyric_lines=lyric_lines,
            info_tags=info_tags,
        )
        return lyric_file

    def commit_current_lyric_line(
        self, lyric_lines: list[LyricLine], buffer: list[tuple[int, str]]
    ) -> None:
        start_time = self.get_time_from_ticks(buffer[0][0])
        lyrics = ""
        for _, lyric in buffer:
            lyrics += SYMBOL_PATTERN.sub("", lyric)
        lyric_lines.append(
            LyricLine(
                time_tags=[
                    TimeTag(
                        minute=start_time.minute,
                        second=start_time.second,
                        percent_second=round(start_time.microsecond / 10),
                    )
                ],
                lyric=lyrics + "\n",
            )
        )

    def get_time_from_ticks(self, ticks: int) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(
            self.synchronizer.get_actual_secs_from_ticks(ticks),
            tz=datetime.timezone.utc,
        )
