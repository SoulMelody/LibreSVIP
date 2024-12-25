import dataclasses
import hashlib
import io
import pathlib
from typing import Optional

from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import InstrumentalTrack, Project, SongTempo
from libresvip.utils.audio import audio_track_info

from .model import (
    PocketSingerBgmInfo,
    PocketSingerBgmTrack,
    PocketSingerMetadata,
    PocketSingerProject,
    PocketSingerSongInfo,
)
from .options import OutputOptions


@dataclasses.dataclass
class PocketSingerGenerator:
    options: OutputOptions
    buffer: io.BytesIO = dataclasses.field(default_factory=io.BytesIO)
    audio_paths: dict[str, pathlib.Path] = dataclasses.field(default_factory=dict)
    synchronizer: TimeSynchronizer = dataclasses.field(init=False)

    def generate_project(self, project: Project) -> PocketSingerMetadata:
        self.synchronizer = TimeSynchronizer(project.song_tempo_list)
        song_info = self.generate_song_info(project.song_tempo_list[0])
        ps_project = PocketSingerProject(song_info=song_info)
        if (
            first_instrumental_track := next(
                (track for track in project.track_list if isinstance(track, InstrumentalTrack)),
                None,
            )
        ) and (bgm_info := self.generate_bgm_info(first_instrumental_track)):
            ps_project.bgm_info = bgm_info
        self.buffer.write(
            ps_project.model_dump_json(by_alias=True, exclude_none=True).encode("utf-8")
        )
        return PocketSingerMetadata(ace_file_name="export.ace")

    def generate_song_info(self, tempo: SongTempo) -> PocketSingerSongInfo:
        return PocketSingerSongInfo(
            start=0,
            first_beat_offset=0.0,
            scale=[
                80,
                79,
                77,
                76,
                75,
                74,
                73,
                72,
                71,
                70,
                69,
                68,
                67,
                66,
                65,
                64,
                63,
                62,
                61,
                60,
                59,
                58,
                57,
                56,
                55,
                54,
                53,
                52,
                51,
                50,
                49,
                48,
                43,
            ],
            key="C",
            segment_of_beat=2,
            operate_scale=[72, 71, 69, 67, 65, 64, 62, 60, 59, 57, 55],
            bpm=tempo.bpm,
            name="New Project",
            duration=0.0,
            beat_of_bar=4,
        )

    def generate_bgm_info(
        self, instrumental_track: InstrumentalTrack
    ) -> Optional[PocketSingerBgmInfo]:
        audio_path = pathlib.Path(instrumental_track.audio_file_path)
        file_type = audio_path.suffix[1:].lower()
        if file_type not in ("wav", "mp3", "flac", "aac", "m4a"):
            return None
        if not (track_info := audio_track_info(audio_path)):
            return None
        audio_content = audio_path.read_bytes()
        self.audio_paths[audio_path.name] = audio_path
        audio_position = self.synchronizer.get_actual_secs_from_ticks(instrumental_track.offset)
        return PocketSingerBgmInfo(
            mute=instrumental_track.mute,
            solo=instrumental_track.solo,
            tracks=[
                PocketSingerBgmTrack(
                    file_name=audio_path.stem,
                    file_type=file_type,
                    file_md5=hashlib.md5(audio_content).hexdigest(),
                    position=audio_position,
                    start_time=audio_position,
                    end_time=audio_position + track_info.duration / 1000,
                )
            ],
        )
