from construct import (
    Array,
    Byte,
    Bytes,
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
    encoder=lambda obj, ctx: obj["value"] | (obj["note_index"] << 12) | (obj["track_index"] << 16),
    decoder=lambda obj, ctx: {
        "value": obj & 0xFFF,
        "note_index": (obj >> 12) & 0xF,
        "track_index": (obj >> 16) & 0xF,
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

Sub46E4D0Block = Prefixed(
    SubSize,
    Struct(
        "word_50" / Int16ul,
        "zero" / Int16ul,
        "byte_82" / Byte,
        "array_1"
        / PrefixedArray(
            Int16ul,
            Struct(
                "byte_0" / Byte,
                "byte_4" / Byte,
                "byte_6" / Byte,
            ),
        ),
        "array_2"
        / PrefixedArray(
            Int16ul,
            Struct(
                "byte_0" / Byte,
                "byte_4" / Byte,
                "byte_6" / Byte,
            ),
        ),
        "array_3"
        / PrefixedArray(
            Int16ul,
            Struct(
                "byte_0" / Byte,
                "byte_4" / Byte,
                "byte_6" / Byte,
            ),
        ),
        "word_132" / Int16ul,
        "byte_134" / Byte,
        "byte_136" / Byte,
        "byte_138" / Byte,
        "byte_80" / Byte,
        "word_52" / Int16ul,
        "word_54" / Int16ul,
        "word_138" / Int16ul,
    ),
)

NoteEntry = Prefixed(
    SubSize,
    Struct(
        "track_index" / Int16ul,
        "packed_1" / Int32ul,
        "packed_2" / Int32ul,
        "note_on_type" / Byte,
        "raw_data" / Bytes(2),
        "sub_46E4D0" / Sub46E4D0Block,
        "lyrics" / Utf16LeString,
        "vibrato_depth" / Byte,
        "vibrato_length" / Byte,
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
