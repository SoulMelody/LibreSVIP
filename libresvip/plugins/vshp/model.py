from construct import (
    Bytes,
    BytesInteger,
    Const,
    FixedSized,
    Float64l,
    GreedyBytes,
    If,
    Int8ul,
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
    "flag" / Int8ul,
    "padding" / Bytes(23),
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
    "pitch" / Int16ul,
    "flag" / Int8ul,
    "padding" / Bytes(21),
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
    "pit_analyze" / Int16ul[4],
    "wave" / Int16ul[4],
    "fix_org" / Int16ul,
    "fix_edit" / Int16ul,
    "ori_pit" / Int16ul,
    "pit" / Int16ul,
    "frm" / Int16sl,
    "bre" / Int16sl,
    "brightness" / Int16sl,
    "clearness" / Int16sl,
    "ori_dyn" / Float64l,
    "dyn" / Float64l,
    "vol" / Float64l,
    "pan" / Float64l,
    "sdyn" / Float64l,
    "dsdyn" / Float64l,
    "unknown" / Int16sl,
    "heq" / Int16sl,
    "padding" / Bytes(12),
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
    "time_count" / Int32ul,
    "analyze_params" / Int32ul,
    "analyze_prm1" / Int16ul,
    "analyze_prm2" / Int16ul,
    "analyze_prm3" / Int16ul,
    "padding1" / Bytes(10),
    "synth_mode" / Int16ul,
    "attack_threshold" / Int16sl,
    "padding2" / Bytes(2),
    "fix_threshold" / Int16sl,
    "padding3" / Bytes(2),
    "fix_threshold_dyn" / Int16ul,
    "synth_option" / Int32ul,
    "fade_in_sample" / Int32ul,
    "fade_out_sample" / Int32ul,
    "padding4" / Bytes(56),
    "spectrum_key_min" / Int16ul,
    "spectrum_key_scale" / Int16ul,
    "spectrum_points_density" / Int16ul,
    "spectrum_points_per_group" / Int16ul,
    "spectrum_points_count" / Int32ul,
    "spectrum_unknown" / Int16ul,
    "padding5" / Bytes(2),
    "notes_count" / Int32ul,
    "label_count" / Int32ul,
    "padding6" / Bytes(8),
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
    "id" / Int32ul,
    "sel_flg" / Int32ul,
    "track_num" / Int32ul,
    "offset_add" / Int32sl,
    "offset" / Float64l,
    "meas_offset" / Float64l,
    "freq_a4" / Float64l,
    "key" / Int32ul,
    "tune" / Int32ul,
    "user_tune" / Bytes(12),
    "base_freq_key" / Int16ul,
    "base_freq_scale" / Int16ul,
    "base_freq" / Float64l,
    "key_type" / Int8ul,
    "padding" / Bytes(3),
    "option" / Int32ul,
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
    "sel_flg" / Int32ul,
    "color" / VocalShifterTrackColor,
    "invert_flg" / Int32ul,
    "morphing_group" / Int32ul,
    "option" / Int32ul,
    "reserved" / Bytes(148),
)


VocalShifterProjectMetadata = Struct(
    "magic" / Const(b"PRJP"),
    "size" / Int32ul,
    "track_count" / Int32ul,
    "pattern_count" / Int32ul,
    "save_option" / Int32ul,
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
