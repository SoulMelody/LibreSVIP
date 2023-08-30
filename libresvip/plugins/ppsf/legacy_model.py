from construct import (
    Byte,
    Bytes,
    BytesInteger,
    Const,
    GreedyRange,
    Int16ul,
    Mapping,
    PaddedString,
    PascalString,
    Prefixed,
    PrefixedArray,
    Struct,
    Switch,
    this,
)

Int32ul = BytesInteger(4, swapped=True)


PpsfTrackTags = Mapping(
    Bytes(4),
    {
        "AudioEventTrack": b"AETK",
        "AudioInDeviceTrack": b"AIDT",
        "AudioOutDeviceTrack": b"AODT",
        "AudioSendEventTrack": b"ASTR",
        "MidiEventTrack": b"METK",
        "MidiInDeviceTrack": b"MIDT",
        "MidiOutDeviceTrack": b"MODT",
        "MusicalParamTrack": b"MPTR",
        "Vocaloid3EventTrack": b"V3TK",
        "Vocaloid2EventTrack": b"VETK",
    },
)


PpsfTrack = Struct(
    "magic" / PpsfTrackTags,
    "size" / Int32ul,
    "index" / Int16ul,
    "data" / Bytes(this.size - 2),
)


PpsfClipTags = Mapping(
    Bytes(4),
    {
        "Vocaloid3NoteClip": b"V3CL",
        "VsqNoteClip": b"VNCL",
        "MidiNoteClip": b"MNCL",
        "MidiMetaClip": b"MMCL",
        "MidiSysExClip": b"MXCL",
        "AudioClip": b"ADCL",
        "AutomationClip": b"AMCL",
    },
)


PpsfClip = Struct(
    "magic" / PpsfClipTags,
    "size" / Int32ul,
    "index" / Int16ul,
    "data" / Bytes(this.size - 2),
)


PpsfPluginTags = Mapping(
    Bytes(4),
    {
        "Vocaloid3EventControlPlugin": b"E3PG",
        "AudioEventControlPlugin": b"EAPG",
        "MidiEventControlPlugin": b"EMPG",
        "MusicParamEventControlPlugin": b"EMPP",
        "SynthEventControlPlugin": b"ESPG",
        "VsqEventControlPlugin": b"EVPG",
        "OpenVocaloidSynthPlugin": b"OSPG",
        "Vocaloid3SynthEventControlPlugin": b"V3CP",
        "VstAudioPlugin": b"VAPG",
        "VstMidiPlugin": b"VMPG",
        "VstSynthPlugin": b"VSPG",
    },
)


PpsfPlugin = Struct(
    "magic" / PpsfPluginTags,
    "size" / Int32ul,
    "index" / Int16ul,
    "data" / Bytes(this.size - 2),
)

PpsfTracksTags = Mapping(
    Bytes(4),
    {
        "AudioEventTracks": b"AETS",
        "AudioInDeviceTracks": b"AIDS",
        "AudioOutDeviceTracks": b"AODS",
        "AudioSendEventTracks": b"ASTS",
        "MidiEventTracks": b"METS",
        "MidiInDeviceTracks": b"MIDS",
        "MidiOutDeviceTracks": b"MODS",
        "MusicalParamTracks": b"MPTS",
        "Vocaloid3EventTracks": b"V3TS",
        "Vocaloid2EventTracks": b"VETS",
    },
)

PpsfTracks = Struct(
    "magic" / PpsfTracksTags,
    "size" / Int32ul,
    "data" / PrefixedArray(Byte, PpsfTrack),
)

PpsfEditorDataTags = Mapping(
    Bytes(4),
    {
        "EditorTrackData": b"ETRS",
        "EditorClipData": b"ECLS",
        "EditorNoteData": b"ENOT",
        "EditorEventData": b"EEVT",
    },
)

PpsfChunkTags = Mapping(
    Bytes(4),
    {
        "Info": b"INFO",
        "Project": b"PROJ",
        "Transport": b"TRNS",
        "Config": b"CONF",
        "Devices": b"DVCS",
        "Tracks": b"TRKS",
        "Clips": b"CLPS",
        "Events": b"EVTS",
        "Plugins": b"PLGS",
        "EditorDatas": b"EDTS",
    },
)

PpsfChunk = Struct(
    "magic" / PpsfChunkTags,
    "size" / Int32ul,
    "data"
    / Switch(
        this.magic,
        {
            "Tracks": Struct("tracks" / GreedyRange(PpsfTracks), Bytes(1)),
            "Clips": Struct(
                "clips" / GreedyRange(PrefixedArray(Byte, PpsfClip)),
            ),
            "Plugins": Struct(
                "plugins" / GreedyRange(PrefixedArray(Byte, PpsfPlugin)),
            ),
        },
        Bytes(this.size),
    ),
)

PpsfLegacyProject = Struct(
    "magic" / Const("PPSF", PaddedString(4, "utf8")),
    "body"
    / Prefixed(
        Int32ul,
        Struct(
            "version" / PascalString(Int16ul, "utf8"),
            "chunks" / GreedyRange(PpsfChunk),
        ),
    ),
)
