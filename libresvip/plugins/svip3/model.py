from dataclasses import dataclass, field
from enum import IntEnum
from typing import Annotated

from pure_protobuf.annotations import Field
from pure_protobuf.message import BaseMessage


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


@dataclass
class Svip3LineParamNode(BaseMessage):
    pos: Annotated[int, Field(1)] = 0
    value: Annotated[float, Field(2)] = 0.0


@dataclass
class Svip3Vibrato(BaseMessage):
    frequency: Annotated[float, Field(1)] = 0.0
    amplitude: Annotated[float, Field(2)] = 0.0
    phase: Annotated[float, Field(3)] = 0.0
    start: Annotated[float, Field(4)] = 0.0
    end: Annotated[float, Field(5)] = 0.0
    attack_x: Annotated[float, Field(6)] = 0.0
    attack_y: Annotated[float, Field(7)] = 0.0
    release_x: Annotated[float, Field(8)] = 0.0
    release_y: Annotated[float, Field(9)] = 0.0


@dataclass
class Svip3Note(BaseMessage):
    start_pos: Annotated[int, Field(1)] = 0
    width_pos: Annotated[int, Field(2)] = 0
    key_index: Annotated[int, Field(3)] = 0
    lyric: Annotated[str, Field(4)] = ""
    pronouncing: Annotated[str, Field(5)] = ""
    consonant_len: Annotated[int, Field(6)] = 0
    has_consonant: Annotated[bool, Field(7)] = False
    user_consonant_len: Annotated[int, Field(8)] = 0
    sp_len: Annotated[int, Field(9)] = 0
    sil_len: Annotated[int, Field(10)] = 0
    length_validate_tag: Annotated[int, Field(11)] = 0
    vibrato: Annotated[Svip3Vibrato, Field(12)] = field(default_factory=Svip3Vibrato)


@dataclass
class Svip3SingingPattern(BaseMessage):
    name: Annotated[str, Field(1)] = ""
    type: Annotated[Svip3PatternType, Field(2)] = Svip3PatternType.Singing_Pattern
    real_pos: Annotated[int, Field(3)] = 0
    real_dur: Annotated[int, Field(4)] = 0
    play_pos: Annotated[int, Field(5)] = 0
    play_dur: Annotated[int, Field(6)] = 0
    is_mute: Annotated[bool, Field(7)] = False
    note_List: Annotated[list[Svip3Note], Field(8)] = field(default_factory=list)
    edited_pitch_line: Annotated[list[Svip3LineParamNode], Field(9)] = field(
        default_factory=list
    )
    edited_volume_line: Annotated[list[Svip3LineParamNode], Field(10)] = field(
        default_factory=list
    )
    edited_power_line: Annotated[list[Svip3LineParamNode], Field(11)] = field(
        default_factory=list
    )
    merge_pitch_line: Annotated[list[Svip3LineParamNode], Field(12)] = field(
        default_factory=list
    )
    merge_power_line: Annotated[list[Svip3LineParamNode], Field(13)] = field(
        default_factory=list
    )


@dataclass
class Svip3SingingTrack(BaseMessage):
    volume: Annotated[float, Field(1)] = 1.0
    pan: Annotated[float, Field(2)] = 0.0
    mute: Annotated[bool, Field(3)] = False
    name: Annotated[str, Field(4)] = ""
    solo: Annotated[bool, Field(5)] = False
    color: Annotated[str, Field(6)] = ""
    type: Annotated[Svip3TrackType, Field(7)] = Svip3TrackType.Singing_Track
    pattern_list: Annotated[list[Svip3SingingPattern], Field(8)] = field(
        default_factory=list
    )
    ai_singer_id: Annotated[str, Field(9)] = ""
    is_reverb_open: Annotated[bool, Field(10)] = False
    reverb_type: Annotated[int, Field(11)] = 0
    reverb_db: Annotated[float, Field(12)] = 0.0


@dataclass
class Svip3BeatSize(BaseMessage):
    numerator: Annotated[int, Field(1)] = 4
    denominator: Annotated[int, Field(2)] = 4


@dataclass
class Svip3Master(BaseMessage):
    volume: Annotated[float, Field(1)] = 1.0


@dataclass
class Svip3SongBeat(BaseMessage):
    pos: Annotated[int, Field(1)] = 0
    beat_size: Annotated[Svip3BeatSize, Field(2)] = field(default_factory=Svip3BeatSize)


@dataclass
class Svip3SongTempo(BaseMessage):
    pos: Annotated[int, Field(1)] = 0
    tempo: Annotated[int, Field(2)] = 0


@dataclass
class Svip3SongTone(BaseMessage):
    pos: Annotated[int, Field(1)] = 0
    tone: Annotated[str, Field(2)] = ""


@dataclass
class Svip3AudioPattern(BaseMessage):
    name: Annotated[str, Field(1)] = ""
    type: Annotated[Svip3PatternType, Field(2)] = Svip3PatternType.Audio_Pattern
    real_pos: Annotated[int, Field(3)] = 0
    real_dur: Annotated[int, Field(4)] = 0
    play_pos: Annotated[int, Field(5)] = 0
    play_dur: Annotated[int, Field(6)] = 0
    is_mute: Annotated[bool, Field(7)] = False
    audio_file_path: Annotated[str, Field(8)] = ""
    rising_falling_tone_: Annotated[float, Field(9)] = 0.0


@dataclass
class Svip3AudioTrack(BaseMessage):
    volume: Annotated[float, Field(1)] = 1.0
    pan: Annotated[float, Field(2)] = 0.0
    mute: Annotated[bool, Field(3)] = False
    name: Annotated[str, Field(4)] = ""
    solo: Annotated[bool, Field(5)] = False
    color: Annotated[str, Field(6)] = ""
    type: Annotated[Svip3TrackType, Field(7)] = Svip3TrackType.Audio_Track
    pattern_list: Annotated[list[Svip3AudioPattern], Field(8)] = field(
        default_factory=list
    )


@dataclass
class Svip3AnyTrack(BaseMessage):
    type_url: Annotated[str, Field(1)] = ""
    value: Annotated[bytes, Field(2)] = b""


@dataclass
class Svip3Project(BaseMessage):
    project_file_path: Annotated[str, Field(1)] = ""
    version: Annotated[str, Field(2)] = "3.0.0"
    duration: Annotated[int, Field(3)] = 0
    tempo_list: Annotated[list[Svip3SongTempo], Field(4)] = field(default_factory=list)
    beat_list: Annotated[list[Svip3SongBeat], Field(5)] = field(default_factory=list)
    track_list: Annotated[list[Svip3AnyTrack], Field(6)] = field(default_factory=list)
    master: Annotated[Svip3Master, Field(7)] = field(default_factory=Svip3Master)
    current_tone: Annotated[str, Field(8)] = ""
    piano_cells: Annotated[int, Field(9)] = 0
    loop_start: Annotated[int, Field(10)] = 0
    loop_end: Annotated[int, Field(11)] = 0
    is_open_adsorb: Annotated[bool, Field(12)] = True
    params_version: Annotated[int, Field(13)] = 0
    tone_list: Annotated[list[Svip3SongTone], Field(14)] = field(default_factory=list)
