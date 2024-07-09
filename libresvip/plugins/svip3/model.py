from __future__ import annotations

from typing import TYPE_CHECKING

import proto
from google.protobuf import any_pb2

if TYPE_CHECKING:
    from collections.abc import MutableSequence

__protobuf__ = proto.module(
    package="xstudio.proto",
    manifest={
        "Svip3TrackType",
        "Svip3PatternType",
        "Svip3NoteLengthValidateTag",
        "Svip3Project",
        "Svip3SongTempo",
        "Svip3SongBeat",
        "Svip3SongTone",
        "Svip3BeatSize",
        "Svip3Master",
        "Svip3SingingTrack",
        "Svip3AudioTrack",
        "Svip3AudioPattern",
        "Svip3SingingPattern",
        "Svip3Vibrato",
        "Svip3Note",
        "Svip3VibratoStyle",
        "Svip3LineParamNode",
    },
)


class Svip3TrackType(proto.Enum):
    Track_None = 0
    Audio_Track = 1
    Singing_Track = 2


class Svip3PatternType(proto.Enum):
    Pattern_None = 0
    Audio_Pattern = 1
    Singing_Pattern = 2


class Svip3NoteLengthValidateTag(proto.Enum):
    NONE = 0
    TOO_LONG = 1
    TOO_SHORT = 2


class Svip3SongMark(proto.Message):
    pos: int = proto.Field(
        proto.INT32,
        number=1,
    )
    mark: str = proto.Field(
        proto.STRING,
        number=2,
    )


class Svip3Project(proto.Message):
    project_file_path: str = proto.Field(
        proto.STRING,
        number=1,
    )
    version: str = proto.Field(
        proto.STRING,
        number=2,
    )
    duration: int = proto.Field(
        proto.INT32,
        number=3,
    )
    tempo_list: MutableSequence[Svip3SongTempo] = proto.RepeatedField(
        proto.MESSAGE,
        number=4,
        message="Svip3SongTempo",
    )
    beat_list: MutableSequence[Svip3SongBeat] = proto.RepeatedField(
        proto.MESSAGE,
        number=5,
        message="Svip3SongBeat",
    )
    track_list: MutableSequence[any_pb2.Any] = proto.RepeatedField(
        proto.MESSAGE,
        number=6,
        message=any_pb2.Any,
    )
    master: Svip3Master = proto.Field(
        proto.MESSAGE,
        number=7,
        message="Svip3Master",
    )
    current_tone: str = proto.Field(
        proto.STRING,
        number=8,
    )
    piano_cells: int = proto.Field(
        proto.INT32,
        number=9,
    )
    loop_start: int = proto.Field(
        proto.INT32,
        number=10,
    )
    loop_end: int = proto.Field(
        proto.INT32,
        number=11,
    )
    is_open_adsorb: bool = proto.Field(
        proto.BOOL,
        number=12,
    )
    params_version: int = proto.Field(
        proto.INT32,
        number=13,
    )
    tone_list: MutableSequence[Svip3SongTone] = proto.RepeatedField(
        proto.MESSAGE,
        number=14,
        message="Svip3SongTone",
    )
    is_triplets: bool = proto.Field(
        proto.BOOL,
        number=15,
    )
    is_loop: bool = proto.Field(
        proto.BOOL,
        number=16,
    )
    is_last_play: bool = proto.Field(
        proto.BOOL,
        number=17,
    )
    mark_list: MutableSequence[Svip3SongMark] = proto.RepeatedField(
        proto.MESSAGE,
        number=18,
        message="Svip3SongMark",
    )


class Svip3SongTempo(proto.Message):
    pos: int = proto.Field(
        proto.INT32,
        number=1,
    )
    tempo: int = proto.Field(
        proto.INT32,
        number=2,
    )


class Svip3SongBeat(proto.Message):
    pos: int = proto.Field(
        proto.INT32,
        number=1,
    )
    beat_size: Svip3BeatSize = proto.Field(
        proto.MESSAGE,
        number=2,
        message="Svip3BeatSize",
    )


class Svip3SongTone(proto.Message):
    pos: int = proto.Field(
        proto.INT32,
        number=1,
    )
    tone: str = proto.Field(
        proto.STRING,
        number=2,
    )


class Svip3BeatSize(proto.Message):
    numerator: int = proto.Field(
        proto.INT32,
        number=1,
    )
    denominator: int = proto.Field(
        proto.INT32,
        number=2,
    )


class Svip3Master(proto.Message):
    volume: float = proto.Field(
        proto.FLOAT,
        number=1,
    )


class Svip3SingingTrack(proto.Message):
    volume: float = proto.Field(
        proto.FLOAT,
        number=1,
    )
    pan: float = proto.Field(
        proto.FLOAT,
        number=2,
    )
    mute: bool = proto.Field(
        proto.BOOL,
        number=3,
    )
    name: str = proto.Field(
        proto.STRING,
        number=4,
    )
    solo: bool = proto.Field(
        proto.BOOL,
        number=5,
    )
    color: str = proto.Field(
        proto.STRING,
        number=6,
    )
    type_: Svip3TrackType = proto.Field(
        proto.ENUM,
        number=7,
        enum="Svip3TrackType",
    )
    pattern_list: MutableSequence[Svip3SingingPattern] = proto.RepeatedField(
        proto.MESSAGE,
        number=8,
        message="Svip3SingingPattern",
    )
    ai_singer_id: str = proto.Field(
        proto.STRING,
        number=9,
    )
    is_reverb_open: bool = proto.Field(
        proto.BOOL,
        number=10,
    )
    reverb_type: int = proto.Field(
        proto.INT32,
        number=11,
    )
    reverb_db: float = proto.Field(
        proto.FLOAT,
        number=12,
    )
    is_rap_track: bool = proto.Field(
        proto.BOOL,
        number=13,
    )


class Svip3AudioTrack(proto.Message):
    volume: float = proto.Field(
        proto.FLOAT,
        number=1,
    )
    pan: float = proto.Field(
        proto.FLOAT,
        number=2,
    )
    mute: bool = proto.Field(
        proto.BOOL,
        number=3,
    )
    name: str = proto.Field(
        proto.STRING,
        number=4,
    )
    solo: bool = proto.Field(
        proto.BOOL,
        number=5,
    )
    color: str = proto.Field(
        proto.STRING,
        number=6,
    )
    type_: Svip3TrackType = proto.Field(
        proto.ENUM,
        number=7,
        enum="Svip3TrackType",
    )
    pattern_list: MutableSequence[Svip3AudioPattern] = proto.RepeatedField(
        proto.MESSAGE,
        number=8,
        message="Svip3AudioPattern",
    )


class Svip3AudioPattern(proto.Message):
    name: str = proto.Field(
        proto.STRING,
        number=1,
    )
    type_: Svip3PatternType = proto.Field(
        proto.ENUM,
        number=2,
        enum="Svip3PatternType",
    )
    real_pos: int = proto.Field(
        proto.INT32,
        number=3,
    )
    real_dur: int = proto.Field(
        proto.INT32,
        number=4,
    )
    play_pos: int = proto.Field(
        proto.INT32,
        number=5,
    )
    play_dur: int = proto.Field(
        proto.INT32,
        number=6,
    )
    is_mute: bool = proto.Field(
        proto.BOOL,
        number=7,
    )
    audio_file_path: str = proto.Field(
        proto.STRING,
        number=8,
    )
    rising_falling_tone: float = proto.Field(
        proto.FLOAT,
        number=9,
    )


class Svip3SingingPattern(proto.Message):
    name: str = proto.Field(
        proto.STRING,
        number=1,
    )
    type_: Svip3PatternType = proto.Field(
        proto.ENUM,
        number=2,
        enum="Svip3PatternType",
    )
    real_pos: int = proto.Field(
        proto.INT32,
        number=3,
    )
    real_dur: int = proto.Field(
        proto.INT32,
        number=4,
    )
    play_pos: int = proto.Field(
        proto.INT32,
        number=5,
    )
    play_dur: int = proto.Field(
        proto.INT32,
        number=6,
    )
    is_mute: bool = proto.Field(
        proto.BOOL,
        number=7,
    )
    note_list: MutableSequence[Svip3Note] = proto.RepeatedField(
        proto.MESSAGE,
        number=8,
        message="Svip3Note",
    )
    edited_pitch_line: MutableSequence[Svip3LineParamNode] = proto.RepeatedField(
        proto.MESSAGE,
        number=9,
        message="Svip3LineParamNode",
    )
    edited_volume_line: MutableSequence[Svip3LineParamNode] = proto.RepeatedField(
        proto.MESSAGE,
        number=10,
        message="Svip3LineParamNode",
    )
    edited_power_line: MutableSequence[Svip3LineParamNode] = proto.RepeatedField(
        proto.MESSAGE,
        number=11,
        message="Svip3LineParamNode",
    )
    merge_pitch_line: MutableSequence[Svip3LineParamNode] = proto.RepeatedField(
        proto.MESSAGE,
        number=12,
        message="Svip3LineParamNode",
    )
    merge_power_line: MutableSequence[Svip3LineParamNode] = proto.RepeatedField(
        proto.MESSAGE,
        number=13,
        message="Svip3LineParamNode",
    )
    edited_spec_trans_coef_line: MutableSequence[Svip3LineParamNode] = proto.RepeatedField(
        proto.MESSAGE,
        number=14,
        message="Svip3LineParamNode",
    )
    edited_ap_coef_line: MutableSequence[Svip3LineParamNode] = proto.RepeatedField(
        proto.MESSAGE,
        number=15,
        message="Svip3LineParamNode",
    )
    edited_energy_value_line: MutableSequence[Svip3LineParamNode] = proto.RepeatedField(
        proto.MESSAGE,
        number=16,
        message="Svip3LineParamNode",
    )
    merge_energy_value_line: MutableSequence[Svip3LineParamNode] = proto.RepeatedField(
        proto.MESSAGE,
        number=17,
        message="Svip3LineParamNode",
    )
    rap_type: int = proto.Field(
        proto.INT32,
        number=18,
    )
    singing_method_id: str = proto.Field(
        proto.STRING,
        number=19,
    )

    @property
    def pos(self) -> int:
        return self.real_pos + self.play_pos


class Svip3Vibrato(proto.Message):
    frequency: float = proto.Field(
        proto.FLOAT,
        number=1,
    )
    amplitude: float = proto.Field(
        proto.FLOAT,
        number=2,
    )
    phase: float = proto.Field(
        proto.FLOAT,
        number=3,
    )
    start: float = proto.Field(
        proto.FLOAT,
        number=4,
    )
    end: float = proto.Field(
        proto.FLOAT,
        number=5,
    )
    attack_x: float = proto.Field(
        proto.FLOAT,
        number=6,
    )
    attack_y: float = proto.Field(
        proto.FLOAT,
        number=7,
    )
    release_x: float = proto.Field(
        proto.FLOAT,
        number=8,
    )
    release_y: float = proto.Field(
        proto.FLOAT,
        number=9,
    )


class Svip3Note(proto.Message):
    start_pos: int = proto.Field(
        proto.INT32,
        number=1,
    )
    width_pos: int = proto.Field(
        proto.INT32,
        number=2,
    )
    key_index: int = proto.Field(
        proto.INT32,
        number=3,
    )
    lyric: str = proto.Field(
        proto.STRING,
        number=4,
    )
    pronouncing: str = proto.Field(
        proto.STRING,
        number=5,
    )
    consonant_len: int = proto.Field(
        proto.INT32,
        number=6,
    )
    has_consonant: bool = proto.Field(
        proto.BOOL,
        number=7,
    )
    user_consonant_len: int = proto.Field(
        proto.INT32,
        number=8,
    )
    sp_len: int = proto.Field(
        proto.INT32,
        number=9,
    )
    sil_len: int = proto.Field(
        proto.INT32,
        number=10,
    )
    length_validate_tag: Svip3NoteLengthValidateTag = proto.Field(
        proto.ENUM,
        number=11,
        enum="Svip3NoteLengthValidateTag",
    )
    vibrato: Svip3Vibrato = proto.Field(
        proto.MESSAGE,
        number=12,
        message="Svip3Vibrato",
    )
    user_sp_len: int = proto.Field(
        proto.INT32,
        number=13,
    )
    tone: int = proto.Field(
        proto.INT32,
        number=14,
    )
    left_pitch: float = proto.Field(
        proto.FLOAT,
        number=15,
    )
    right_pitch: float = proto.Field(
        proto.FLOAT,
        number=16,
    )


class Svip3VibratoStyle(proto.Message):
    is_anti_phase: bool = proto.Field(
        proto.BOOL,
        number=1,
    )
    amp_line: MutableSequence[Svip3LineParamNode] = proto.RepeatedField(
        proto.MESSAGE,
        number=2,
        message="Svip3LineParamNode",
    )
    freq_line: MutableSequence[Svip3LineParamNode] = proto.RepeatedField(
        proto.MESSAGE,
        number=3,
        message="Svip3LineParamNode",
    )


class Svip3LineParamNode(proto.Message):
    pos: int = proto.Field(
        proto.SINT32,
        number=1,
    )
    value: float = proto.Field(
        proto.FLOAT,
        number=2,
    )
