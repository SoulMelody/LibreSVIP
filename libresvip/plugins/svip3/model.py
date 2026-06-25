from __future__ import annotations

from typing import TYPE_CHECKING

from .svip3_pb import (
    Svip3AudioPattern,
    Svip3AudioTrack,
    Svip3BeatSize,
    Svip3LineParamNode,
    Svip3Note,
    Svip3NoteLengthValidateTag,
    Svip3Project,
    Svip3SingingPattern,
    Svip3SingingTrack,
    Svip3SongBeat,
    Svip3SongTempo,
)

if TYPE_CHECKING:
    from .svip3_pb import Svip3SingingPattern as _Svip3SingingPattern


def _pattern_pos(self: _Svip3SingingPattern) -> int:
    return self.real_pos + self.play_pos


Svip3SingingPattern.pos = property(_pattern_pos)


__all__ = (
    "Svip3AudioPattern",
    "Svip3AudioTrack",
    "Svip3BeatSize",
    "Svip3LineParamNode",
    "Svip3Note",
    "Svip3NoteLengthValidateTag",
    "Svip3Project",
    "Svip3SingingPattern",
    "Svip3SingingTrack",
    "Svip3SongBeat",
    "Svip3SongTempo",
)
