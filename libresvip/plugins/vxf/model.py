from construct import (
    Check,
    Const,
    ExprAdapter,
    GreedyRange,
    Int8ub,
    Int16ub,
    Int32ub,
    PaddedString,
    Select,
    Struct,
    obj_,
)

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
    "data" / PaddedString(12, "utf-8"),
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
    "delta_ticks" / DeltaTicks,
    "magic" / Const(b"\xd0\x10\x00\x00"),
    "tempo" / Int32ub,
    "padding" / Const(b"\x00" * 8),
)

UmpTimeSignature = Struct(
    "delta_ticks" / DeltaTicks,
    "magic" / Const(b"\xd0\x10\x00\x01"),
    "numerator" / Int8ub,
    "cc" / Int8ub,
    "dd" / Int8ub,
    "padding" / Const(b"\x00" * 9),
)

UmpLyric = Struct(
    "delta_ticks" / DeltaTicks,
    "header" / Const(b"\xd0"),
    "seq_stat" / Int8ub,
    "magic" / Const(b"\x01\x50"),
    "seq_num" / Int16ub,
    "lyric" / PaddedString(10, "utf-8"),
)

UmpMetadata = Struct(
    "delta_ticks" / DeltaTicks,
    "header" / Const(b"\xd0"),
    "seq_stat" / Int8ub,
    "magic" / Const(b"\x01\x51"),
    "seq_num" / Int16ub,
    "text" / PaddedString(10, "utf-8"),
)

UmpNoteOn = Struct(
    "time" / DeltaTicks,
    "note" / StartPitch,
    Check(lambda ctx: 0 <= ctx.note <= 127),
    "velocity" / Int16ub,
    "attribute" / Int16ub,
)

UmpNoteOff = Struct(
    "time" / DeltaTicks,
    "note" / EndPitch,
    Check(lambda ctx: 0 <= ctx.note <= 127),
    "velocity" / Int16ub,
    "attribute" / Int16ub,
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
    "ppqn" / PPQN,
    "tracks" / GreedyRange(VxTrack),
)
