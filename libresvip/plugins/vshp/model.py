from construct import (
    Bytes,
    BytesInteger,
    Const,
    Float64l,
    GreedyRange,
    Int16sl,
    Int16ul,
    PaddedString,
    Padding,
    Struct,
    this,
)
from construct import Enum as CSEnum

Int32ul = BytesInteger(4, swapped=True, signed=False)


VocalShifterNote = Struct(
    "start_time" / Int32ul,
    "length" / Int32ul,
    "pitch" / Int32ul,
    "padding" / Padding(20),
)


VocalShifterNotes = Struct(
    "magic" / Const(b"Note"),
    "size" / Int32ul,
    "notes" / VocalShifterNote[this.size // VocalShifterNote.sizeof()],
)


VocalShifterTime = Struct(
    "magic" / Const(b"Time"),
    "size" / Int32ul,
    "original_time" / Float64l,
    "time" / Float64l,
)

VocalShifterControlPoint = Struct(
    "magic" / Const(b"Ctrp"),
    "size" / Int32ul,
    "pit_array" / Int16ul[4],
    "padding1" / Padding(12),
    "ori_pit" / Int16ul,
    "pit" / Int16ul,
    "frm" / Int16sl,
    "bre" / Int16sl,
    "eq1" / Int16sl,
    "eq2" / Int16sl,
    "ori_dyn" / Float64l,
    "dyn" / Float64l,
    "vol" / Float64l,
    "pan" / Float64l,
    "padding2" / Padding(18),
    "heq" / Int16sl,
    "padding3" / Padding(12),
)

VocalShifterPatternType = CSEnum(
    Int32ul,
    WAVE=0,
    MIDI=1,
)


VocalShifterAnalysisMethod = CSEnum(
    Int16ul,
    Monophonic=0,
    MonophonicVocal=1,
    Polyphonic=2,
    Rhythm=4,
    World=8,
)


VocalShifterTemperament = CSEnum(
    Int32ul,
    EqualTemperament=0,
    JustIntonation=1,
    PythagoreanTuning=2,
    MeantoneTemperament=3,
)


VocalShifterPatternHeader = Struct(
    "magic" / Const(b"Itmp"),
    "size" / Int32ul,
    "length" / Int32ul,
    "sample_rate" / Int32ul,
    "channels" / Int32ul,
    "pattern_type" / VocalShifterPatternType,
    "padding1" / Bytes(4),
    "points_count" / Int32ul,
    "padding2" / Bytes(24),
    "analysis_method" / VocalShifterAnalysisMethod,
    "reserved" / Bytes(110),
    "eq1" / Int16sl[16],
    "eq2" / Int16sl[16],
    "heq" / Int16sl[16],
)

VocalShifterPatternData = Struct(
    "magic" / Const(b"ITMD"),
    "size" / Int32ul,
    "header" / VocalShifterPatternHeader,
    "points" / VocalShifterControlPoint[this.header.points_count],
    "start_time" / VocalShifterTime,
    "end_time" / VocalShifterTime,
    "note" / VocalShifterNotes,
)

VocalShifterPatternMetadata = Struct(
    "magic" / Const(b"ITMP"),
    "size" / Int32ul,
    "path" / Bytes(256),
    "padding1" / Bytes(12),
    "offset_correction" / Int32ul,
    "offset_samples" / Float64l,
    "measure_offset" / Float64l,
    "base_freq" / Float64l,
    "key" / Int32ul,
    "temperament" / VocalShifterTemperament,
    "padding2" / Bytes(16),
    "modified_base_freq" / Float64l,
    "is_sharp" / Int32ul,
    "reserved" / Bytes(180),
)

VocalShifterPattern = Struct(
    "metadata" / VocalShifterPatternMetadata,
    "data" / VocalShifterPatternData,
)

VocalShifterTrackMetadata = Struct(
    "magic" / Const(b"TRKP"),
    "size" / Int32ul,
    "name" / PaddedString(64, "ascii"),
    "volume" / Float64l,
    "pan" / Float64l,
    "mute" / Int32ul,
    "solo" / Int32ul,
    "phase_pre" / Int32ul,
    "color_index" / Int32ul,
    "phase_next" / Int32ul,
    "morph_group" / Int32ul,
    "mute_flag" / Int32ul,
    "reserved" / Bytes(148),
)


VocalShifterTrack = Struct(
    "metadata" / VocalShifterTrackMetadata,
    "patterns" / GreedyRange(VocalShifterPattern),
)


VocalShifterProjectMetadata = Struct(
    "magic" / Const(b"PRJP"),
    "size" / Int32ul,
    "track_count" / Int32ul,
    "padding1" / Bytes(0x4),
    "is_absolute_path" / Int32ul,
    "vslib_version" / Int32ul,
    "sample_rate" / Int32ul,
    "numerator" / Int32ul,
    "denominator" / Int32ul,
    "padding2" / Bytes(0x4),
    "tempo" / Float64l,
    "master_volume" / Float64l,
    "is_float" / Int32ul,
    "bit_depth" / Int32ul,
    "channels" / Int32ul,
    "reserved" / Bytes(196),
)

VocalShifterProjectData = Struct(
    "magic" / Const(b"VSPD"),
    "version" / Bytes(8),
    "size" / Int32ul,
    "project_metadata" / VocalShifterProjectMetadata,
    "tracks" / VocalShifterTrack[this.project_metadata.track_count],
)
