from types import SimpleNamespace
from typing import Final

TYPE_URL_BASE: Final[str] = "type.googleapis.com/"


Svip3TrackType = SimpleNamespace(
    SINGING_TRACK="xstudio.proto.SingingTrack", AUDIO_TRACK="xstudio.proto.AudioTrack"
)
