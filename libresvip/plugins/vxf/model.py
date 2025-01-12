from construct import (
    Check,
    Computed,
    Const,
    ExprAdapter,
    GreedyRange,
    If,
    IfThenElse,
    Int8ub,
    Int16ub,
    Int32ub,
    PaddedString,
    Select,
    Struct,
    obj_,
)
from pydantic import Field

from libresvip.model.base import BaseModel

# Reference: https://github.com/jazz-soft/JZZ/blob/master/javascript/JZZ.js
BASE_DCTPQ = 0x30
BASE_DELTA_TICKS = 0x40
BASE_NOTE = 0x7F
BASE_START_PITCH = 0x4090
BASE_END_PITCH = 0x4080

PPQN = ExprAdapter(
    Int32ub,
    encoder=obj_ + (BASE_DCTPQ << 16),
    decoder=obj_ - (BASE_DCTPQ << 16),
)

DeltaTicks = ExprAdapter(
    Int32ub,
    encoder=obj_ + (BASE_DELTA_TICKS << 16),
    decoder=obj_ - (BASE_DELTA_TICKS << 16),
)

NoteNumber = ExprAdapter(
    Int32ub,
    encoder=obj_ + (BASE_NOTE << 16),
    decoder=obj_ - (BASE_NOTE << 16),
)

StartPitch = ExprAdapter(
    Int32ub,
    encoder=(1 + (obj_ << 8) + (BASE_START_PITCH << 16)),
    decoder=(obj_ - (BASE_START_PITCH << 16)) >> 8,
)

EndPitch = ExprAdapter(
    Int32ub,
    encoder=(1 + (obj_ << 8) + (BASE_END_PITCH << 16)),
    decoder=(obj_ - (BASE_END_PITCH << 16)) >> 8,
)

UmpClipName = Struct(
    "header" / Const(b"\xd0"),
    "seq_stat" / Int8ub,
    "magic" / Const(b"\x01\x03"),
    "name" / PaddedString(12, "utf-8"),
    "type" / Computed("track_name"),
)

UmpStartOfClip = Struct(
    "magic" / Const(b"\xf0\x20\x00\x00"),
    "padding" / Const(b"\x00" * 12),
)

UmpEndOfClip = Struct(
    "magic" / Const(b"\xf0\x21\x00\x00"),
    "padding" / Const(b"\x00" * 12),
)

UmpTempo = Struct(
    "time" / DeltaTicks,
    "magic" / Const(b"\xd0\x10\x00\x00"),
    "tempo"
    / ExprAdapter(
        Int32ub,
        encoder=lambda obj, context: int(1705032600 / obj),
        decoder=lambda obj, context: 1705032600 / obj,
    ),
    "padding" / Const(b"\x00" * 8),
    "type" / Computed("set_tempo"),
)

UmpTimeSignature = Struct(
    "time" / DeltaTicks,
    "magic" / Const(b"\xd0\x10\x00\x01"),
    "numerator" / Int8ub,
    "denominator"
    / ExprAdapter(
        Int8ub,
        encoder=lambda obj, context: obj.bit_length() - 1,
        decoder=lambda obj, context: 1 << obj,
    ),
    "padding" / Const(b"\x08" + b"\x00" * 9),
    "type" / Computed("time_signature"),
)

UmpLyric = Struct(
    "time" / DeltaTicks,
    "header" / Const(b"\xd0"),
    "seq_stat" / Int8ub,
    "magic" / Const(b"\x01\x50"),
    "seq_num" / If(lambda this: (this.seq_stat - 16) // 64 <= 1, Int16ub),
    "text"
    / IfThenElse(
        lambda this: (this.seq_stat - 16) // 64 <= 1,
        PaddedString(10, "ascii"),
        PaddedString(12, "ascii"),
    ),
    "type" / Computed("lyrics"),
)

UmpMetadata = Struct(
    "time" / DeltaTicks,
    "header" / Const(b"\xd0"),
    "seq_stat" / Int8ub,
    "magic" / Const(b"\x01\x51"),
    "text" / PaddedString(12, "utf-8"),
    "type" / Computed("metadata"),
)

UmpNoteOn = Struct(
    "time" / DeltaTicks,
    "note" / StartPitch,
    Check(lambda ctx: 0 <= ctx.note <= 127),
    "velocity" / Int16ub,
    "on_data" / Int16ub,
    "type" / Computed("note_on"),
)

UmpNoteOff = Struct(
    "time" / DeltaTicks,
    "note" / EndPitch,
    Check(lambda ctx: 0 <= ctx.note <= 127),
    "velocity" / Int16ub,
    "off_data" / Int16ub,
    "type" / Computed("note_off"),
)

VxTrack = Struct(
    "title_parts" / GreedyRange(UmpClipName),
    "start_of_clip" / UmpStartOfClip,
    "events"
    / GreedyRange(Select(UmpTempo, UmpTimeSignature, UmpLyric, UmpMetadata, UmpNoteOn, UmpNoteOff)),
    "end_of_clip" / UmpEndOfClip,
)

VxFile = Struct(
    "magic" / Const(b"SMF2CLIP"),
    "ticks_per_beat" / PPQN,
    "tracks" / GreedyRange(VxTrack),
)


class VxPitchPoint(BaseModel):
    pitch: float
    position: int
    applicable: bool = True


class VxTimeBasedPitchSequence(BaseModel):
    time_frame_period_seconds: float = Field(alias="timeFramePeriodSeconds")
    num_frames_overall_sequence: int = Field(0, alias="numFramesOverallSequence")
    pitch_sequence: list[VxPitchPoint] = Field(default_factory=list, alias="pitchSequence")


class VxPitchData(BaseModel):
    time_based_pitch_sequence: VxTimeBasedPitchSequence = Field(alias="TimeBasedPitchSequence")
