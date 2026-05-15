from construct import (
    Array,
    Byte,
    BytesInteger,
    Const,
    ExprAdapter,
    Float32l,
    GreedyBytes,
    Int16sl,
    Int16ul,
    PascalString,
    Prefixed,
    PrefixedArray,
    Struct,
    obj_,
)

Int32ul = BytesInteger(4, swapped=True)

VocalinaSectionSize = ExprAdapter(
    Int32ul,
    encoder=obj_ + 8,
    decoder=obj_ - 8,
)

SubSize = ExprAdapter(
    Int16ul,
    encoder=obj_ + 2,
    decoder=obj_ - 2,
)

Utf16LeString = PascalString(Int16ul, "utf-16-le")

PackedValue = ExprAdapter(
    Int32ul,
    encoder=lambda obj, ctx: obj["low"] | (obj["mid"] << 12) | (obj["high"] << 16),
    decoder=lambda obj, ctx: {
        "low": obj & 0xFFF,
        "mid": (obj >> 12) & 0xF,
        "high": (obj >> 16) & 0xFFFF,
    },
)

VocalinaStudioProjectFileMetadata = Struct(
    "magic" / Const(b"VSPF"),
    "data"
    / Prefixed(
        VocalinaSectionSize,
        Struct(
            "version" / Int32ul,
            "is_vocalina2" / Byte,
            "is_vocalina2_pro" / Byte,
            "is_trial" / Byte,
            "project_name" / Utf16LeString,
        ),
    ),
)

TempoEntry = Struct(
    "tick" / Int16ul,
    "tempo_value" / Int16ul,
)

VocalinaStudioTempos = Struct(
    "magic" / Const(b"TMPO"),
    "data"
    / Prefixed(
        VocalinaSectionSize,
        PrefixedArray(
            Int16ul,
            TempoEntry,
        ),
    ),
)

TimeSignatureEntry = Struct(
    "tick" / Int16ul,
    "numerator" / Byte,
    "denominator" / Byte,
)

VocalinaStudioTimeSignatures = Struct(
    "magic" / Const(b"BEAT"),
    "data"
    / Prefixed(
        VocalinaSectionSize,
        PrefixedArray(
            Int16ul,
            TimeSignatureEntry,
        ),
    ),
)

TrackParamBlock = Struct(
    "wstring" / Utf16LeString,
    "params_1_7" / Array(7, Int16sl),
    "params_11_14" / Array(4, Int16sl),
    "sub_46E220_1"
    / Struct(
        "magic" / Const(14, Int16ul),
        "f1" / Float32l,
        "f2" / Float32l,
        "f0" / Float32l,
    ),
    "sub_46E220_2"
    / Struct(
        "magic" / Const(14, Int16ul),
        "f1" / Float32l,
        "f2" / Float32l,
        "f0" / Float32l,
    ),
    "sub_46E220_3"
    / Struct(
        "magic" / Const(14, Int16ul),
        "f1" / Float32l,
        "f2" / Float32l,
        "f0" / Float32l,
    ),
    "sub_46E270"
    / Struct(
        "magic" / Const(14, Int16ul),
        "v0" / Int16sl,
        "v4" / Int16sl,
        "v8" / Int16sl,
        "f12" / Float32l,
        "v16" / Int16sl,
    ),
    "param_17" / Int16sl,
)

TrackEntry = Struct(
    "track_name" / Utf16LeString,
    "singer_name" / Utf16LeString,
    "field_16" / Byte,
    "const_1" / Const(1, Byte),
    "param_block" / Prefixed(SubSize, TrackParamBlock),
    "field_18" / Byte,
    "field_20" / Int16ul,
    "field_12" / Byte,
)

VocalinaStudioTracks = Struct(
    "magic" / Const(b"TRCK"),
    "data"
    / Prefixed(
        VocalinaSectionSize,
        Struct(
            "tracks" / PrefixedArray(Int16ul, Prefixed(SubSize, TrackEntry)),
            "is_muted" / Byte,
            "master_track" / Prefixed(SubSize, TrackEntry),
            "effect_track" / Prefixed(SubSize, TrackEntry),
        ),
    ),
)

NoteControlPoint = Struct(
    "position" / Byte,
    "value" / Byte,
    "shape" / Byte,
)

NoteParameters = Prefixed(
    SubSize,
    Struct(
        "param_0" / Int16ul,
        "zero" / Int16ul,
        "vibrato" / Byte,
        "intensity_envelope" / PrefixedArray(Int16ul, NoteControlPoint),
        "vibrato_envelope_1" / PrefixedArray(Int16ul, NoteControlPoint),
        "vibrato_envelope_0" / PrefixedArray(Int16ul, NoteControlPoint),
        "tail_word_0" / Int16ul,
        "tail_byte_0" / Byte,
        "tail_byte_1" / Byte,
        "tail_byte_2" / Byte,
        "intensity" / Byte,
        "param_6" / Int16ul,
        "param_17" / Int16ul,
        "tail_word_1" / Int16ul,
    ),
)

NoteEntry = Prefixed(
    SubSize,
    Struct(
        "track_index" / Int16ul,
        "packed_start" / PackedValue,
        "packed_end" / PackedValue,
        "note_number" / Byte,
        "velocity" / Int16ul,
        "params" / NoteParameters,
        "lyrics" / Utf16LeString,
        "flags" / Byte,
        "flags2" / Byte,
    ),
)

VocalinaStudioNotes = Struct(
    "magic" / Const(b"NOTE"),
    "data"
    / Prefixed(
        VocalinaSectionSize,
        Struct(
            "track_count" / Int16ul,
            "notes" / PrefixedArray(Int16ul, NoteEntry),
        ),
    ),
)

EffectParamEntry = Struct(
    "packed_value" / Int32ul,
    "bypass" / Int32ul,
)

EffectBlock = Prefixed(
    SubSize,
    Struct(
        "track_index" / Int16ul,
        "effect_type" / Int16ul,
        "entries" / PrefixedArray(Int16ul, EffectParamEntry),
        "flag" / Byte,
    ),
)

VocalinaStudioEffects = Struct(
    "magic" / Const(b"EFCT"),
    "data"
    / Prefixed(
        VocalinaSectionSize,
        Struct(
            "blocks" / PrefixedArray(Int16ul, EffectBlock),
        ),
    ),
)

VstPluginEntry = Prefixed(
    SubSize,
    Struct(
        "track_index" / Int16ul,
        "plugin_index" / Int16ul,
        "plugin_name" / Utf16LeString,
        "preset_name" / Utf16LeString,
        "bypass" / Byte,
        "param_display_count" / Int32ul,
        "params"
        / PrefixedArray(
            Int16ul,
            Float32l,
        ),
    ),
)

VocalinaStudioVstPlugins = Struct(
    "magic" / Const(b"VST_"),
    "data"
    / Prefixed(
        VocalinaSectionSize,
        Struct(
            "blocks" / PrefixedArray(Int16ul, VstPluginEntry),
        ),
    ),
)

VocalinaStudioBgm = Struct(
    "magic" / Const(b"BGM_"),
    "data"
    / Prefixed(
        VocalinaSectionSize,
        Struct(
            "block_size" / Int16ul,
            "is_bgm_enabled" / Int32ul,
            "unknown_byte_0" / Byte,
            "unknown_word_2" / Int16ul,
            "unknown_int_0" / Int32ul,
            "unknown_byte_v6" / Byte,
            "unknown_word_2b" / Int16ul,
            "raw_data"
            / Prefixed(
                Int32ul,
                GreedyBytes,
            ),
        ),
    ),
)

VocalinaStudioConfigGrid = Prefixed(
    SubSize,
    Struct(
        "grid_resolution1" / Byte,
        "grid_snap1" / Byte,
        "grid_resolution2" / Byte,
        "grid_snap2" / Byte,
    ),
)

VocalinaStudioConfigPlayback = Prefixed(
    SubSize,
    Struct(
        "playback_enabled" / Int32ul,
        "playback_start" / PackedValue,
        "playback_end" / PackedValue,
        "loop_start_tick" / Int16ul,
        "loop_end_tick" / Int16ul,
        "loop_count" / Int16ul,
    ),
)

VocalinaStudioConfigVolume = Prefixed(
    SubSize,
    Struct(
        "volume_percent" / Byte,
        "master_volume" / Byte,
    ),
)

VocalinaStudioConfig = Struct(
    "magic" / Const(b"CONF"),
    "data"
    / Prefixed(
        VocalinaSectionSize,
        Struct(
            "grid" / VocalinaStudioConfigGrid,
            "playback" / VocalinaStudioConfigPlayback,
            "volume" / VocalinaStudioConfigVolume,
        ),
    ),
)

VocalinaStudioProjectFile = Struct(
    "metadata" / VocalinaStudioProjectFileMetadata,
    "tempos" / VocalinaStudioTempos,
    "time_signatures" / VocalinaStudioTimeSignatures,
    "tracks" / VocalinaStudioTracks,
    "notes" / VocalinaStudioNotes,
    "effects" / VocalinaStudioEffects,
    "vst_plugins" / VocalinaStudioVstPlugins,
    "bgm" / VocalinaStudioBgm,
    "config" / VocalinaStudioConfig,
)
