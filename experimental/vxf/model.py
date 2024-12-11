import mido_fix as mido
from construct import (
    Bytes,
    Const,
    ExprAdapter,
    GreedyRange,
    Int8ub,
    Int16ub,
    Int32ub,
    PaddedString,
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
    "magic" / Const(b"\xd0\x10\x01\x03"),
    "name" / PaddedString(12, "utf-8"),
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
    "tempo"
    / ExprAdapter(
        Int32ub,
        encoder=lambda x, _: mido.bpm2tempo(x / 100),
        decoder=lambda x, _: mido.tempo2bpm(x) * 100,
    ),
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
    "magic" / Const(b"\xd0\x10\x01\x50"),
    "seq_num" / Int16ub,
    "lyric" / PaddedString(10, "utf-8"),
)

VxNote = Struct(
    "offset" / DeltaTicks,
    "start_pitch" / StartPitch,
    "seq_num" / NoteNumber,
    "duration" / DeltaTicks,
    "end_pitch" / EndPitch,
    "padding" / Bytes(4),
)

VxTrack = Struct(
    "title" / UmpClipName,
    "start_of_clip" / UmpStartOfClip,
    "tempos" / GreedyRange(UmpTempo),
    "time_signatures" / GreedyRange(UmpTimeSignature),
    "lyrics" / GreedyRange(UmpLyric),
    "notes" / GreedyRange(VxNote),
    "end_of_clip" / UmpEndOfClip,
)

VxFile = Struct(
    "magic" / Const(b"SMF2CLIP"),
    "ppqn" / PPQN,
    "tracks" / GreedyRange(VxTrack),
)
