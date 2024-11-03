from types import SimpleNamespace
from typing import Final

TYPE_URL_BASE: Final[str] = "type.googleapis.com/"
DEFAULT_SINGER_ID: Final[str] = "7d0c0cfc-00b3-4dca-b7b0-d20b634b531a"
MIN_NOTE_DURATION: Final[float] = 0.06
MAX_NOTE_DURATION: Final[float] = 6.0


Svip3TrackType = SimpleNamespace(
    SINGING_TRACK="xstudio.proto.SingingTrack",
    AUDIO_TRACK="xstudio.proto.AudioTrack",
)
