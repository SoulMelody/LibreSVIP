from construct import (
    Bytes,
    BytesInteger,
    Const,
    FixedSized,
    Float64l,
    GreedyBytes,
    If,
    Int16sl,
    Int16ul,
    Struct,
    this,
)
from construct import Enum as CSEnum

Int32sl = BytesInteger(4, swapped=True, signed=True)
Int32ul = BytesInteger(4, swapped=True, signed=False)

VocalShifterLabel = Struct(
    "start_tick" / Int32ul,
    "end_tick" / Int32ul,
    "index" / Int32ul,
    "padding" / Bytes(20),
    "name" / FixedSized(64, GreedyBytes),
)


VocalShifterLabels = Struct(
    "magic" / Const(b"Labl"),
    "size" / Int32ul,
    "labels" / VocalShifterLabel[this._.header.label_count],
)


VocalShifterNote = Struct(
    "start_tick" / Int32ul,
    "length" / Int32ul,
    "pitch" / Int32ul,
    "padding" / Bytes(20),
)


VocalShifterNotes = Struct(
    "magic" / Const(b"Note"),
    "size" / Int32ul,
    "notes" / VocalShifterNote[this._.header.notes_count],
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
    "padding1" / Bytes(12),
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
    "padding2" / Bytes(18),
    "heq" / Int16sl,
    "padding3" / Bytes(12),
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
    "sample_count" / Int32ul,
    "sample_rate" / Int32ul,
    "channels" / Int32ul,
    "pattern_type" / VocalShifterPatternType,
    "points_per_second" / Int32ul,
    "points_count" / Int32ul,
    "padding1" / Bytes(8),
    "key_min" / Int16ul,
    "key_scale" / Int16ul,  # key_max = key_min + key_scale
    "padding2" / Bytes(12),
    "analysis_method" / VocalShifterAnalysisMethod,
    "padding3" / Bytes(78),
    "spectrum_key_min" / Int16ul,
    "spectrum_key_scale" / Int16ul,
    "spectrum_points_density" / Int16ul,
    "spectrum_unknown1" / Int16ul,
    "spectrum_points_count" / Int32ul,
    "spectrum_unknown2" / Int32ul,
    "notes_count" / Int32ul,
    "label_count" / Int32ul,
    "padding4" / Bytes(8),
    "eq1" / Int16sl[16],
    "eq2" / Int16sl[16],
    "heq" / Int16sl[16],
)


VocalShifterSpectrumData = Struct(
    "magic" / Const(b"Spct"),
    "size" / Int32ul,
    "data"
    / Int16ul[
        this._.header.spectrum_points_count
        * this._.header.spectrum_points_density
        * this._.header.spectrum_key_scale
    ],
)


VocalShifterPatternData = Struct(
    "magic" / Const(b"ITMD"),
    "size" / Int32ul,
    "header" / VocalShifterPatternHeader,
    "points" / VocalShifterControlPoint[this.header.points_count],
    "start_time" / VocalShifterTime,
    "end_time" / VocalShifterTime,
    "spectrum"
    / If(
        this.header.spectrum_points_count > 0,
        VocalShifterSpectrumData,
    ),
    "notes" / VocalShifterNotes,
    "labels" / If(this.header.label_count > 0, VocalShifterLabels),
)

VocalShifterPatternMetadata = Struct(
    "magic" / Const(b"ITMP"),
    "size" / Int32ul,
    "path_and_ext" / Bytes(256),
    "pattern_index" / Int32ul,
    "track_index" / Int32ul,
    "padding1" / Bytes(4),
    "offset_correction" / Int32sl,
    "offset_samples" / Float64l,
    "measure_offset" / Float64l,
    "base_freq" / Float64l,
    "key" / Int32ul,
    "temperament" / VocalShifterTemperament,
    "padding2" / Bytes(16),
    "modified_base_freq" / Float64l,
    "is_sharp" / Int32ul,
    "mrp_auto_set" / Int32ul,
    "reserved" / Bytes(176),
)

VocalShifterTrackColor = CSEnum(
    Int32ul,
    Red=0,
    Orange=1,
    Yellow=2,
    Green=3,
    LightBlue=4,
    Blue=5,
    Purple=6,
    Pink=7,
)

VocalShifterTrackMetadata = Struct(
    "magic" / Const(b"TRKP"),
    "size" / Int32ul,
    "name" / FixedSized(64, GreedyBytes),
    "volume" / Float64l,
    "pan" / Float64l,
    "mute" / Int32ul,
    "solo" / Int32ul,
    "phase_pre" / Int32ul,
    "color" / VocalShifterTrackColor,
    "phase_next" / Int32ul,
    "morph_group" / Int32ul,
    "mute_flag" / Int32ul,
    "reserved" / Bytes(148),
)


VocalShifterProjectMetadata = Struct(
    "magic" / Const(b"PRJP"),
    "size" / Int32ul,
    "track_count" / Int32ul,
    "pattern_count" / Int32ul,
    "is_absolute_path" / Int32ul,
    "vslib_version" / Int32ul,
    "sample_rate" / Int32ul,
    "numerator" / Int32ul,
    "denominator" / Int32ul,
    "padding1" / Bytes(0x4),
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
    "track_metadatas" / VocalShifterTrackMetadata[this.project_metadata.track_count],
    "pattern_metadatas" / VocalShifterPatternMetadata[this.project_metadata.pattern_count],
    "pattern_datas" / VocalShifterPatternData[this.project_metadata.pattern_count],
)
