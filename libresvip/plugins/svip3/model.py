from dataclasses import dataclass
from enum import IntEnum
from typing import List, Optional

from pure_protobuf.dataclasses_ import field, message, optional_field
from pure_protobuf.types import int32, sint32
from pure_protobuf.types.google import Any_


class Svip3TrackType(IntEnum):
    Track_None = 0
    Audio_Track = 1
    Singing_Track = 2


class Svip3PatternType(IntEnum):
    Pattern_None = 0
    Audio_Pattern = 1
    Singing_Pattern = 2


class Svip3NoteLengthValidateTag(IntEnum):
    NONE = 0
    TOO_LONG = 1
    TOO_SHORT = 2


@message
@dataclass
class Svip3LineParamNode:
    pos: Optional[sint32] = field(1)
    value: Optional[float] = field(2)


@message
@dataclass
class Svip3Vibrato:
    frequency: Optional[float] = field(1)
    amplitude: Optional[float] = field(2)
    phase: Optional[float] = field(3)
    start: Optional[float] = field(4)
    end: Optional[float] = field(5)
    attack_x: Optional[float] = field(6)
    attack_y: Optional[float] = field(7)
    release_x: Optional[float] = field(8)
    release_y: Optional[float] = field(9)


@message
@dataclass
class Svip3Note:
    start_pos: Optional[int32] = field(1)
    width_pos: Optional[int32] = field(2)
    key_index: Optional[int32] = field(3)
    lyric: Optional[str] = field(4)
    pronouncing: Optional[str] = field(5)
    vibrato: Optional[Svip3Vibrato] = optional_field(12)
    consonant_len: Optional[int32] = field(6, default=0)
    has_consonant: Optional[bool] = field(7, default=False)
    user_consonant_len: Optional[int32] = field(8, default=0)
    sp_len: Optional[int32] = field(9, default=0)
    sil_len: Optional[int32] = field(10, default=0)
    length_validate_tag: Optional[int32] = field(11, default=0)


@message
@dataclass
class Svip3SingingPattern:
    name: Optional[str] = field(1)
    real_dur: Optional[int32] = field(4)
    play_dur: Optional[int32] = field(6)
    note_List: Optional[List[Svip3Note]] = field(8)
    type: Optional[Svip3PatternType] = field(
        2, default=Svip3PatternType.Singing_Pattern
    )
    real_pos: Optional[int32] = field(3, default=0)
    play_pos: Optional[int32] = field(5, default=0)
    is_mute: Optional[bool] = field(7, default=False)
    edited_pitch_line: Optional[List[Svip3LineParamNode]] = field(
        9, default_factory=list
    )
    edited_volume_line: Optional[List[Svip3LineParamNode]] = field(
        10, default_factory=list
    )
    edited_power_line: Optional[List[Svip3LineParamNode]] = field(
        11, default_factory=list
    )
    merge_pitch_line: Optional[List[Svip3LineParamNode]] = field(
        12, default_factory=list
    )
    merge_power_line: Optional[List[Svip3LineParamNode]] = field(
        13, default_factory=list
    )


@message
@dataclass
class Svip3SingingTrack:
    volume: Optional[float] = field(1)
    name: Optional[str] = field(4)
    color: Optional[str] = field(6)
    pattern_list: Optional[List[Svip3SingingPattern]] = field(8)
    ai_singer_id: Optional[str] = field(9)
    pan: Optional[float] = field(2, default=0.0)
    mute: Optional[bool] = field(3, default=False)
    solo: Optional[bool] = field(5, default=False)
    type: Optional[Svip3TrackType] = field(7, default=Svip3TrackType.Singing_Track)
    is_reverb_open: Optional[bool] = field(10, default=False)
    reverb_type: Optional[int32] = field(11, default=0)
    reverb_db: Optional[float] = field(12, default=0.0)


@message
@dataclass
class Svip3BeatSize:
    numerator: Optional[int32] = field(1)
    denominator: Optional[int32] = field(2)


@message
@dataclass
class Svip3Master:
    volume: Optional[float] = field(1, default=1.0)


@message
@dataclass
class Svip3SongBeat:
    beat_size: Optional[Svip3BeatSize] = field(2)
    pos: Optional[int32] = field(1, default=0)


@message
@dataclass
class Svip3SongTempo:
    tempo: Optional[int32] = field(2)
    pos: Optional[int32] = field(1, default=0)


@message
@dataclass
class Svip3SongTone:
    tone: Optional[str] = field(2)
    pos: Optional[int32] = field(1, default=0)


@message
@dataclass
class Svip3AudioPattern:
    name: Optional[str] = field(1)
    real_pos: Optional[int32] = field(3)
    real_dur: Optional[int32] = field(4)
    play_dur: Optional[int32] = field(6)
    audio_file_path: Optional[str] = field(8)
    type: Optional[Svip3PatternType] = field(2, default=Svip3PatternType.Audio_Pattern)
    play_pos: Optional[int32] = optional_field(5)
    is_mute: Optional[bool] = optional_field(7)
    rising_falling_tone_: Optional[float] = optional_field(9)


@message
@dataclass
class Svip3AudioTrack:
    volume: Optional[float] = field(1)
    name: Optional[str] = field(4)
    color: Optional[str] = field(6)
    pattern_list: Optional[List[Svip3AudioPattern]] = field(8)
    pan: Optional[float] = optional_field(2)
    mute: Optional[bool] = optional_field(3)
    solo: Optional[bool] = optional_field(5)
    type: Optional[Svip3TrackType] = field(7, default=Svip3TrackType.Audio_Track)


@message
@dataclass
class Svip3Project:
    duration: Optional[int32] = field(3)
    tempo_list: Optional[List[Svip3SongTempo]] = field(4)
    beat_list: Optional[List[Svip3SongBeat]] = field(5)
    track_list: Optional[List[Any_]] = field(6)
    project_file_path: Optional[str] = field(1, default="")
    version: Optional[str] = field(2, default="3.0.0")
    master: Optional[Svip3Master] = field(7, default_factory=Svip3Master)
    current_tone: Optional[str] = field(8, default="")
    piano_cells: Optional[int32] = optional_field(9)
    loop_start: Optional[int32] = optional_field(10)
    loop_end: Optional[int32] = optional_field(11)
    is_open_adsorb: Optional[bool] = optional_field(12)
    params_version: Optional[int32] = optional_field(13)
    tone_list: Optional[List[Svip3SongTone]] = field(14, default_factory=list)
