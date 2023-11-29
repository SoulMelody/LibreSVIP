from construct import (
    Byte,
    Bytes,
    BytesInteger,
    Const,
    ExprAdapter,
    FixedSized,
    FocusedSeq,
    GreedyRange,
    Int16ub,
    Int16ul,
    Mapping,
    PaddedString,
    PascalString,
    Prefixed,
    PrefixedArray,
    Select,
    Struct,
    Subconstruct,
    Switch,
    obj_,
    this,
)

Int32ul = BytesInteger(4, swapped=True)


def ppsf_prefixed_array(subcon: Subconstruct) -> Select:
    return Select(
        PrefixedArray(Byte, subcon),
        PrefixedArray(
            ExprAdapter(
                Int16ub,
                encoder=obj_ ^ 56960,
                decoder=obj_ ^ 56960,
            ),
            subcon,
        ),
        PrefixedArray(
            FocusedSeq(
                "size",
                Const(b"\x81"),
                "size"
                / ExprAdapter(
                    Byte,
                    encoder=obj_ ^ 128,
                    decoder=obj_ ^ 128,
                ),
            ),
            subcon,
        ),
        PrefixedArray(
            FocusedSeq(
                "size",
                Const(b"\x81"),
                "size"
                / ExprAdapter(
                    Int16ub,
                    encoder=obj_ * 2 - (obj_ & 127),
                    decoder=((obj_ & 127) + obj_) // 2,
                ),
            ),
            subcon,
        ),
    )


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
    "data" / ppsf_prefixed_array(PpsfTrack),
)

PpsfEventTags = Mapping(
    Bytes(1),
    {
        "MidiEvent": b"\x00",
        "MidiSysExEvent": b"\x03",
        "MidiMetaEvent": b"\x04",
        "VsqNoteEvent": b"\x05",
        "MidiNoteEvent": b"\x07",
        "Vocaloid3NoteEvent": b"\x08",
        "AutomationEvent": b"\x09",
        "AudioEvent": b"\x0b",
    },
)

PpsfEvent = Struct(
    "magic" / PpsfEventTags,
    "size" / Int16ul,
    "data" / Bytes(this.size),
)

PpsfRect = Struct(
    "magic" / Const(b"RECT"),
    "size" / Int32ul,
    "width" / Int32ul,
    "height" / Int32ul,
    "x" / Int32ul,
    "y" / Int32ul,
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

PpsfEditorData = Struct(
    "magic" / PpsfEditorDataTags,
    "size" / Int32ul,
    "data" / Bytes(this.size),
)

PpsfMarker = Struct(
    "magic" / Const(b"UMKR"),
    "size" / Int32ul,
    "data"
    / FixedSized(
        this.size,
        GreedyRange(
            Struct(
                "index" / Bytes(4),
                "tick" / Int32ul,
            )
        ),
    ),
)

PpsfEditorClipData = Struct(
    "magic" / Const(b"ECLS"),
    "size" / Int32ul,
    "data"
    / FixedSized(
        this.size,
        Struct(
            "unknown1" / Bytes(6),
            "unknown2" / PascalString(Byte, "utf-8"),
            "unknown3" / Bytes(13),
            "note_datas" / ppsf_prefixed_array(PpsfEditorData),
        ),
    ),
)

PpsfEditorTrackData = Struct(
    "magic" / Const(b"ETRS"),
    "size" / Int32ul,
    "data"
    / FixedSized(
        this.size,
        Struct(
            "unknown1" / Bytes(28),
            "unknown2" / PascalString(Byte, "utf-8"),
            "unknown3" / Bytes(22),
            "track_datas" / ppsf_prefixed_array(PpsfEditorData),
            "clip_datas" / ppsf_prefixed_array(PpsfEditorClipData),
            "event_datas" / ppsf_prefixed_array(PpsfEditorData),
        ),
    ),
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
                "clips" / GreedyRange(ppsf_prefixed_array(PpsfClip)),
            ),
            "Events": Struct(
                "events" / GreedyRange(ppsf_prefixed_array(PpsfEvent)),
            ),
            "Plugins": Struct(
                "plugins" / GreedyRange(ppsf_prefixed_array(PpsfPlugin)),
            ),
            "EditorDatas": Struct(
                "prefix" / Bytes(4),
                "rect1" / PpsfRect,
                "unknown1" / Bytes(12),
                "unknown2" / PascalString(Byte, "utf-8"),
                "unknown3" / Bytes(48),
                "markers" / ppsf_prefixed_array(PpsfMarker),
                "unknown4" / ppsf_prefixed_array(PpsfEditorData),
                "editor_datas" / ppsf_prefixed_array(PpsfEditorTrackData),
                "other_track_datas" / GreedyRange(PpsfEditorData),
                "padding" / Bytes(1),
                "rect2" / PpsfRect,
                "rect3" / PpsfRect,
                "suffix" / Bytes(12),
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
