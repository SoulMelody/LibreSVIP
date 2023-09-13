from construct import (
    BytesInteger,
    Const,
    ExprAdapter,
    GreedyBytes,
    Prefixed,
    Struct,
    obj_,
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

VocalinaStudioProjectFileMetadata = Struct(
    "magic" / Const(b"VSPF"),
    "data" / VocalinaSectionData,
)

VocalinaStudioTempos = Struct(
    "magic" / Const(b"TMPO"),
    "data" / VocalinaSectionData,
)

VocalinaStudioTimeSignatures = Struct(
    "magic" / Const(b"BEAT"),
    "data" / VocalinaSectionData,
)

VocalinaStudioTracks = Struct(
    "magic" / Const(b"TRCK"),
    "data" / VocalinaSectionData,
)

VocalinaStudioNotes = Struct(
    "magic" / Const(b"NOTE"),
    "data" / VocalinaSectionData,
)

VocalinaStudioEffects = Struct(
    "magic" / Const(b"EFCT"),
    "data" / VocalinaSectionData,
)

VocalinaStudioVstPlugins = Struct(
    "magic" / Const(b"VST_"),
    "data" / VocalinaSectionData,
)

VocalinaStudioBgm = Struct(
    "magic" / Const(b"BGM_"),
    "data" / VocalinaSectionData,
)

VocalinaStudioConfig = Struct(
    "magic" / Const(b"CONF"),
    "data" / VocalinaSectionData,
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
