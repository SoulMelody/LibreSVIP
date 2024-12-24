import dataclasses
import io
import pathlib

from libresvip.model.base import Project

from .model import PocketSingerMetadata, PocketSingerProject, PocketSingerSongInfo
from .options import OutputOptions


@dataclasses.dataclass
class PocketSingerGenerator:
    options: OutputOptions
    buffer: io.BytesIO = dataclasses.field(default_factory=io.BytesIO)
    audio_paths: dict[str, pathlib.Path] = dataclasses.field(default_factory=dict)

    def generate_project(self, project: Project) -> PocketSingerMetadata:
        song_info = self.generate_song_info(project)
        ps_project = PocketSingerProject(song_info=song_info)
        self.buffer.write(
            ps_project.model_dump_json(by_alias=True, exclude_none=True).encode("utf-8")
        )
        return PocketSingerMetadata(ace_file_name="export.ace")

    def generate_song_info(self, project: Project) -> PocketSingerSongInfo:
        return PocketSingerSongInfo()
