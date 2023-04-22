import dataclasses

from libresvip.core.constants import DEFAULT_BPM
from libresvip.model.base import (
    InstrumentalTrack,
    Note,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
    Track,
)

from .model import (
    UNote,
    USTXProject,
    UTempo,
    UTimeSignature,
    UTrack,
    UVibrato,
    UVoicePart,
    UWavePart,
)
from .options import OutputOptions


@dataclasses.dataclass
class UstxGenerator:
    options: OutputOptions

    def generate_project(self, project: Project) -> USTXProject:
        pass
