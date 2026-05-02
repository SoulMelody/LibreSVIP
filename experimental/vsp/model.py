from construct import (
    Array,
    Byte,
    Bytes,
    BytesInteger,
    Const,
    ExprAdapter,
    Float32l,
    GreedyBytes,
    Int16ul,
    PascalString,
    Prefixed,
    PrefixedArray,
    Struct,
    obj_,
    this,
)

Int32ul = BytesInteger(4, swapped=True)

VocalinaSectionData = Prefixed(
    ExprAdapter(
        Int32ul,
        encoder=obj_ + 8,
        decoder=obj_ - 8,
    ),
    GreedyBytes,
)

Utf16LeString = PascalString(Int16ul, "utf-16-le")

PackedValue = ExprAdapter(
    Int32ul,
    encoder=lambda obj, ctx: (
        (obj["value"] << 12) | (obj["note_index"] << 16) | (obj["track_index"] << 20)
    ),
    decoder=lambda obj, ctx: {
        "value": obj & 0xFFF,
        "note_index": (obj >> 12) & 0xF,
        "track_index": (obj >> 16) & 0xF,
    },
)

VocalinaStudioProjectFileMetadata = Struct(
    "magic" / Const(b"VSPF"),
    "data"
    / Struct(
        "version" / Int32ul,
        "is_vocalina2" / Byte,
        "is_vocalina2_pro" / Byte,
        "is_trial" / Byte,
        "project_name" / Utf16LeString,
    ),
)

TempoEntry = Struct(
    "start_tick" / Int32ul,
    "end_tick" / Int32ul,
    "tempo_value" / Int32ul,
    "tempo_display" / Int16ul,
)

VocalinaStudioTempos = Struct(
    "magic" / Const(b"TMPO"),
    "data"
    / PrefixedArray(
        Int16ul,
        TempoEntry,
    ),
)

TimeSignatureEntry = Struct(
    "start_tick" / Int32ul,
    "end_tick" / Int32ul,
    "numerator" / Int32ul,
    "numerator_display" / Byte,
    "denominator_display" / Byte,
)

VocalinaStudioTimeSignatures = Struct(
    "magic" / Const(b"BEAT"),
    "data"
    / PrefixedArray(
        Int16ul,
        TimeSignatureEntry,
    ),
)

TrackEntry = Struct(
    "track_name" / Utf16LeString,
    "singer_name" / Utf16LeString,
    "is_muted" / Byte,
    "is_solo" / Byte,
    "volume" / Int16ul,
    "is_locked" / Byte,
)

VocalinaStudioTracks = Struct(
    "magic" / Const(b"TRCK"),
    "data"
    / Struct(
        "tracks"
        / PrefixedArray(
            Int16ul,
            TrackEntry,
        ),
        "is_muted" / Byte,
        "master_track" / TrackEntry,
        "effect_track" / TrackEntry,
    ),
)

NoteEntry = Struct(
    "note_type" / Int16ul,
    "start_tick" / Int32ul,
    "end_tick" / Int32ul,
    "duration" / Int32ul,
    "pitch" / Int32ul,
    "velocity" / Int32ul,
    "pitch_bend" / Int32ul,
    "is_note_on" / Byte,
    "vibrato" / Int16ul,
    "lyrics" / Utf16LeString,
    "vibrato_depth" / Byte,
    "vibrato_length" / Byte,
)

NoteTrackData = PrefixedArray(
    Int16ul,
    NoteEntry,
)

VocalinaStudioNotes = Struct(
    "magic" / Const(b"NOTE"),
    "data"
    / Struct(
        "track_count" / Int16ul,
        "total_notes" / Int32ul,
        "tracks" / Array(this.track_count, NoteTrackData),
    ),
)

EffectEntry = Struct(
    "effect_type" / Int16ul,
    "param1" / PackedValue,
    "param2" / PackedValue,
    "param3" / PackedValue,
    "bypass" / Byte,
)

EffectTrackData = PrefixedArray(
    Int16ul,
    EffectEntry,
)

VocalinaStudioEffects = Struct(
    "magic" / Const(b"EFCT"),
    "data"
    / Struct(
        "tracks"
        / PrefixedArray(
            Int16ul,
            EffectTrackData,
        ),
        "master_effects" / EffectTrackData,
        "effect_track_effects" / EffectTrackData,
    ),
)

VstPluginEntry = Struct(
    "plugin_name" / Utf16LeString,
    "preset_name" / Utf16LeString,
    "bypass" / Byte,
    "param_display_count" / Int32ul,
    "params"
    / PrefixedArray(
        Int16ul,
        Float32l,
    ),
)

VstTrackData = PrefixedArray(
    Int16ul,
    VstPluginEntry,
)

VocalinaStudioVstPlugins = Struct(
    "magic" / Const(b"VST_"),
    "data"
    / Struct(
        "tracks"
        / PrefixedArray(
            Int16ul,
            VstTrackData,
        ),
        "master_plugins" / VstTrackData,
        "effect_track_plugins" / VstTrackData,
    ),
)

VocalinaStudioBgm = Struct(
    "magic" / Const(b"BGM_"),
    "data"
    / Struct(
        "data_size" / Int32ul,
        "is_bgm_enabled" / Int32ul,
        "volume" / Byte,
        "pan" / Int16ul,
        "playback_mode" / Int32ul,
        "raw_data" / Bytes(this.data_size),
    ),
)

VocalinaStudioConfigGrid = Struct(
    "grid_resolution1" / Byte,
    "grid_snap1" / Byte,
    "grid_resolution2" / Byte,
    "grid_snap2" / Byte,
)

VocalinaStudioConfigPlayback = Struct(
    "playback_enabled" / Int32ul,
    "playback_start" / PackedValue,
    "playback_end" / PackedValue,
    "loop_start_tick" / Int16ul,
    "loop_end_tick" / Int16ul,
    "loop_count" / Int16ul,
)

VocalinaStudioConfigVolume = Struct(
    "volume_percent" / Byte,
    "master_volume" / Byte,
)

VocalinaStudioConfig = Struct(
    "magic" / Const(b"CONF"),
    "data"
    / Struct(
        "grid" / VocalinaStudioConfigGrid,
        "playback" / VocalinaStudioConfigPlayback,
        "volume" / VocalinaStudioConfigVolume,
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
