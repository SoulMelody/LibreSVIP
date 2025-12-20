from typing import Any

import aristaproto
import aristaproto.lib.pydantic.google.protobuf as aristaproto_lib_pydantic_google_protobuf
from pydantic import GetCoreSchemaHandler
from pydantic.dataclasses import dataclass
from pydantic_core import core_schema


class TrackType(aristaproto.Enum):
    Track_None = 0
    Audio_Track = 1
    Singing_Track = 2

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: GetCoreSchemaHandler
    ) -> core_schema.IntSchema:
        return core_schema.int_schema(ge=0)


class PatternType(aristaproto.Enum):
    Pattern_None = 0
    Audio_Pattern = 1
    Singing_Pattern = 2

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: GetCoreSchemaHandler
    ) -> core_schema.IntSchema:
        return core_schema.int_schema(ge=0)


class Svip3NoteLengthValidateTag(aristaproto.Enum):
    NONE = 0
    TOO_LONG = 1
    TOO_SHORT = 2

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: GetCoreSchemaHandler
    ) -> core_schema.IntSchema:
        return core_schema.int_schema(ge=0)


@dataclass
class Svip3SongTempo(aristaproto.Message):
    pos: int = aristaproto.int32_field(1)
    tempo: int = aristaproto.int32_field(2)


@dataclass
class Svip3SongBeat(aristaproto.Message):
    pos: int = aristaproto.int32_field(1)
    beat_size: "Svip3BeatSize" = aristaproto.message_field(2)


@dataclass
class SongTone(aristaproto.Message):
    pos: int = aristaproto.int32_field(1)
    tone: str = aristaproto.string_field(2)


@dataclass
class Svip3BeatSize(aristaproto.Message):
    numerator: int = aristaproto.int32_field(1)
    denominator: int = aristaproto.int32_field(2)


@dataclass
class Master(aristaproto.Message):
    volume: float = aristaproto.float_field(1)


@dataclass
class Svip3SingingTrack(aristaproto.Message):
    volume: float = aristaproto.float_field(1)
    pan: float = aristaproto.float_field(2)
    mute: bool = aristaproto.bool_field(3)
    name: str = aristaproto.string_field(4)
    solo: bool = aristaproto.bool_field(5)
    color: str = aristaproto.string_field(6)
    type: "TrackType" = aristaproto.enum_field(7)
    pattern_list: list["Svip3SingingPattern"] = aristaproto.message_field(8)
    ai_singer_id: str = aristaproto.string_field(9)
    is_reverb_open: bool = aristaproto.bool_field(10)
    reverb_type: int = aristaproto.int32_field(11)
    reverb_db: float = aristaproto.float_field(12)
    is_rap_track: bool = aristaproto.bool_field(13)


@dataclass
class Svip3AudioTrack(aristaproto.Message):
    volume: float = aristaproto.float_field(1)
    pan: float = aristaproto.float_field(2)
    mute: bool = aristaproto.bool_field(3)
    name: str = aristaproto.string_field(4)
    solo: bool = aristaproto.bool_field(5)
    color: str = aristaproto.string_field(6)
    type: "TrackType" = aristaproto.enum_field(7)
    pattern_list: list["Svip3AudioPattern"] = aristaproto.message_field(8)


@dataclass
class Svip3AudioPattern(aristaproto.Message):
    name: str = aristaproto.string_field(1)
    type: "PatternType" = aristaproto.enum_field(2)
    real_pos: int = aristaproto.int32_field(3)
    real_dur: int = aristaproto.int32_field(4)
    play_pos: int = aristaproto.int32_field(5)
    play_dur: int = aristaproto.int32_field(6)
    is_mute: bool = aristaproto.bool_field(7)
    audio_file_path: str = aristaproto.string_field(8)
    rising_falling_tone: float = aristaproto.float_field(9)


@dataclass
class Svip3SingingPattern(aristaproto.Message):
    name: str = aristaproto.string_field(1)
    type: "PatternType" = aristaproto.enum_field(2)
    real_pos: int = aristaproto.int32_field(3)
    real_dur: int = aristaproto.int32_field(4)
    play_pos: int = aristaproto.int32_field(5)
    play_dur: int = aristaproto.int32_field(6)
    is_mute: bool = aristaproto.bool_field(7)
    note_list: list["Svip3Note"] = aristaproto.message_field(8)
    edited_pitch_line: list["Svip3LineParamNode"] = aristaproto.message_field(9)
    edited_volume_line: list["Svip3LineParamNode"] = aristaproto.message_field(10)
    edited_power_line: list["Svip3LineParamNode"] = aristaproto.message_field(11)
    merge_pitch_line: list["Svip3LineParamNode"] = aristaproto.message_field(12)
    merge_power_line: list["Svip3LineParamNode"] = aristaproto.message_field(13)
    edited_spec_trans_coef_line: list["Svip3LineParamNode"] = aristaproto.message_field(14)
    edited_ap_coef_line: list["Svip3LineParamNode"] = aristaproto.message_field(15)
    edited_energy_value_line: list["Svip3LineParamNode"] = aristaproto.message_field(16)
    merge_energy_value_line: list["Svip3LineParamNode"] = aristaproto.message_field(17)
    rap_type: int = aristaproto.int32_field(18)
    singing_method_id: str = aristaproto.string_field(19)

    @property
    def pos(self) -> int:
        return self.real_pos + self.play_pos


@dataclass
class Svip3Vibrato(aristaproto.Message):
    frequency: float = aristaproto.float_field(1)
    amplitude: float = aristaproto.float_field(2)
    phase: float = aristaproto.float_field(3)
    start: float = aristaproto.float_field(4)
    end: float = aristaproto.float_field(5)
    attack_x: float = aristaproto.float_field(6)
    attack_y: float = aristaproto.float_field(7)
    release_x: float = aristaproto.float_field(8)
    release_y: float = aristaproto.float_field(9)


@dataclass
class Svip3Note(aristaproto.Message):
    start_pos: int = aristaproto.int32_field(1)
    width_pos: int = aristaproto.int32_field(2)
    key_index: int = aristaproto.int32_field(3)
    lyric: str = aristaproto.string_field(4)
    pronouncing: str = aristaproto.string_field(5)
    consonant_len: int = aristaproto.int32_field(6)
    has_consonant: bool = aristaproto.bool_field(7)
    user_consonant_len: int = aristaproto.int32_field(8)
    sp_len: int = aristaproto.int32_field(9)
    sil_len: int = aristaproto.int32_field(10)
    length_validate_tag: "Svip3NoteLengthValidateTag" = aristaproto.enum_field(11)
    vibrato: "Svip3Vibrato" = aristaproto.message_field(12)
    user_sp_len: int = aristaproto.int32_field(13)
    tone: int = aristaproto.int32_field(14)
    left_pitch: float = aristaproto.float_field(15)
    right_pitch: float = aristaproto.float_field(16)


@dataclass
class Svip3VibratoStyle(aristaproto.Message):
    is_anti_phase: bool = aristaproto.bool_field(1)
    amp_line: list["Svip3LineParamNode"] = aristaproto.message_field(2)
    freq_line: list["Svip3LineParamNode"] = aristaproto.message_field(3)


@dataclass
class Svip3VibratoPercentInfo(aristaproto.Message):
    start_percent: float = aristaproto.float_field(1)
    end_percent: float = aristaproto.float_field(2)


@dataclass
class Svip3LineParamNode(aristaproto.Message):
    pos: int = aristaproto.sint32_field(1)
    value: float = aristaproto.float_field(2)


@dataclass
class Svip3SongMark(aristaproto.Message):
    pos: int = aristaproto.int32_field(1)
    mark: str = aristaproto.string_field(2)


@dataclass
class Svip3Project(aristaproto.Message):
    project_file_path: str = aristaproto.string_field(1)
    version: str = aristaproto.string_field(2)
    duration: int = aristaproto.int32_field(3)
    tempo_list: list["Svip3SongTempo"] = aristaproto.message_field(4)
    beat_list: list["Svip3SongBeat"] = aristaproto.message_field(5)
    track_list: list["aristaproto_lib_pydantic_google_protobuf.Any"] = aristaproto.message_field(6)
    master: "Master" = aristaproto.message_field(7)
    current_tone: str = aristaproto.string_field(8)
    piano_cells: int = aristaproto.int32_field(9)
    loop_start: int = aristaproto.int32_field(10)
    loop_end: int = aristaproto.int32_field(11)
    is_open_adsorb: bool = aristaproto.bool_field(12)
    params_version: int = aristaproto.int32_field(13)
    tone_list: list["SongTone"] = aristaproto.message_field(14)
    is_triplets: bool = aristaproto.bool_field(15)
    is_loop: bool = aristaproto.bool_field(16)
    is_last_play: bool = aristaproto.bool_field(17)
    mark_list: list["Svip3SongMark"] = aristaproto.message_field(18)
