import dataclasses
import io
import pathlib

from libresvip.model.base import Project

from .model import PocketSingerMetadata
from .options import OutputOptions


@dataclasses.dataclass
class PocketSingerGenerator:
    options: OutputOptions
    buffer: io.BytesIO = dataclasses.field(default_factory=io.BytesIO)
    audio_paths: dict[str, pathlib.Path] = dataclasses.field(default_factory=dict)

    def generate_project(self, project: Project) -> PocketSingerMetadata:
        return PocketSingerMetadata()
