from typing import BinaryIO

from construct import (
    Array,
    Byte,
    Bytes,
    BytesInteger,
    Computed,
    Const,
    Construct,
    Container,
    FixedSized,
    GreedyBytes,
    GreedyRange,
    If,
    IfThenElse,
    Int16ul,
    Mapping,
    PascalString,
    Prefixed,
    PrefixedArray,
    SizeofError,
    StreamError,
    Struct,
    Subconstruct,
    Switch,
    this,
)
from construct import Path as CSPath
from construct_typed import Context

Int32ul = BytesInteger(4, swapped=True)


def _get_version(ctx: Context) -> tuple[int, ...]:
    while ctx is not None:
        if hasattr(ctx, "version") and isinstance(ctx.get("version"), tuple):
            return ctx.version
        ctx = ctx.get("_") if hasattr(ctx, "get") else None
    return (0, 0, 0, 0, 0, 0)


def _is_new_version(ctx: Context, minor: int = 9, revision: int = 3) -> bool:
    v = _get_version(ctx)
    return v[0] > 0 or v[1] > minor or (v[1] == minor and v[2] > revision)


def _parse_version(s: str) -> tuple[int, ...]:
    parts = s.split(".")
    return (*tuple(int(p) for p in parts), 0, 0, 0)


class PpsfVarInt(Construct):
    """LEB128-style varint matching sub_10119AC0/sub_10119EE0.
    Up to 5 bytes; high bit set means continue; bytes are MSB-first."""

    def _parse(self, stream: BinaryIO, context: Context, path: CSPath) -> int:
        result = 0
        for _ in range(5):
            b = stream.read(1)
            if len(b) != 1:
                msg = "expected 1 byte for varint"
                raise StreamError(msg, path=path)
            byte = b[0]
            result = (result << 7) | (byte & 0x7F)
            if byte & 0x80 == 0:
                return result
        msg = "varint exceeds 5 bytes"
        raise StreamError(msg, path=path)

    def _build(self, obj: Container, stream: BinaryIO, context: Context, path: CSPath) -> None:
        if obj < 0:
            msg = "varint cannot encode negative"
            raise StreamError(msg, path=path)
        if obj <= 0x7F:
            stream.write(bytes([obj]))
        elif obj <= 0x3FFF:
            stream.write(bytes([0x80 | (obj >> 7), obj & 0x7F]))
        elif obj <= 0x1FFFFF:
            stream.write(bytes([0x80 | (obj >> 14), 0x80 | ((obj >> 7) & 0x7F), obj & 0x7F]))
        elif obj <= 0xFFFFFFF:
            stream.write(
                bytes(
                    [
                        0x80 | (obj >> 21),
                        0x80 | ((obj >> 14) & 0x7F),
                        0x80 | ((obj >> 7) & 0x7F),
                        obj & 0x7F,
                    ]
                )
            )
        else:
            stream.write(
                bytes(
                    [
                        0x80 | (obj >> 28),
                        0x80 | ((obj >> 21) & 0x7F),
                        0x80 | ((obj >> 14) & 0x7F),
                        0x80 | ((obj >> 7) & 0x7F),
                        obj & 0x7F,
                    ]
                )
            )
        return obj

    def _sizeof(self, context: Context, path: CSPath) -> int:
        raise SizeofError(path=path)


PpsfVarIntCount = PpsfVarInt()


def ppsf_prefixed_array(subcon: Subconstruct) -> Construct:
    return PrefixedArray(PpsfVarIntCount, subcon)


PpsfVarIntString = PascalString(PpsfVarIntCount, "utf-8")


PpsfMidiNoteEvent = Struct(
    "tick" / Int32ul,
    "note" / Byte,
    "velocity" / Byte,
    "duration" / Int32ul,
    "channel" / Byte,
    "flags" / Byte,
)

PpsfAutomationEvent = Struct(
    "tick" / Int32ul,
    "value" / Int32ul,
    "interpolation_type" / Byte,
)

PpsfMidiSysExEvent = Struct(
    "tick" / Int32ul,
    "manufacturer_id" / Byte,
    "data" / ppsf_prefixed_array(Byte),
)

PpsfMidiMetaEvent = Struct(
    "tick" / Int32ul,
    "meta_type" / Byte,
    "meta_subtype" / Byte,
    "data" / ppsf_prefixed_array(Byte),
)

PpsfLyricHandle = Struct(
    "lyric" / PpsfVarIntString,
    "phoneme" / PpsfVarIntString,
    "protected" / Byte,
)

PpsfBPValue = Struct(
    "value" / Int32ul,
    "position" / Int16ul,
)

PpsfBPValueList = ppsf_prefixed_array(PpsfBPValue)
PpsfExtension = Prefixed(PpsfVarIntCount, GreedyBytes)

PpsfVibratoHandle = Struct(
    "handle_id" / Int16ul,
    "depth_data" / PpsfExtension,
    "flag" / Byte,
    "rate_data" / PpsfExtension,
    "start_position" / Int16ul,
    "amplitude_bp" / PpsfBPValueList,
    "frequency_bp" / PpsfBPValueList,
)

PpsfVsqNoteEvent = Struct(
    "tick" / Int32ul,
    "note" / Byte,
    "duration" / Int32ul,
    "velocity" / Byte,
    "byte_25" / Byte,
    "byte_26" / Byte,
    "byte_27" / Byte,
    "byte_28" / Byte,
    "byte_29" / Byte,
    "lyric_handle" / PpsfLyricHandle,
    "vibrato_data" / GreedyBytes,
)

PpsfVocaloid3NoteEvent = Struct(
    "tick" / Int32ul,
    "note" / Byte,
    "duration" / Int32ul,
    "velocity" / Byte,
    "byte_25" / Byte,
    "byte_26" / Byte,
    "byte_27" / Byte,
    "byte_28" / Byte,
    "byte_29" / Byte,
    "byte_30" / Byte,
    "lyric" / PpsfVarIntString,
    "protected" / Byte,
    "phoneme" / PpsfVarIntString,
    "vibrato" / PpsfVibratoHandle,
    "trailing" / Int16ul,
)

PpsfAudioFormatChunk = Struct(
    "magic" / Const(b"AFMT"),
    "channels" / Int16ul,
    "bits_per_sample" / Int16ul,
    "sample_rate" / Int32ul,
    "block_align" / Int16ul,
)

PpsfAudioAcidChunk = Struct(
    "magic" / Const(b"AACD"),
    "flag" / Byte,
    "field_20" / Int32ul,
    "field_24" / Int16ul,
    "field_26" / Int16ul,
    "string1" / PpsfVarIntString,
    "field_32" / Int32ul,
    "field_36" / Int16ul,
    "field_38" / Int16ul,
    "string2" / PpsfVarIntString,
)

PpsfAudioEvent = Struct(
    "audio_file_name" / PpsfVarIntString,
    "tick" / Int32ul,
    "afmt" / PpsfAudioFormatChunk,
    "aacd" / PpsfAudioAcidChunk,
)

PpsfEventTags = Mapping(
    Bytes(1),
    {
        "AutomationEvent": b"\x00",
        "MidiNoteEvent": b"\x01",
        "MidiSysExEvent": b"\x03",
        "MidiMetaEvent": b"\x04",
        "VsqNoteEvent": b"\x05",
        "Vocaloid3NoteEvent": b"\x08",
        "AudioEvent": b"\x0b",
    },
)

PpsfEvent = Struct(
    "magic" / PpsfEventTags,
    "size" / Int16ul,
    "data"
    / FixedSized(
        this.size,
        Switch(
            this.magic,
            {
                "AutomationEvent": PpsfAutomationEvent,
                "MidiNoteEvent": PpsfMidiNoteEvent,
                "MidiSysExEvent": PpsfMidiSysExEvent,
                "MidiMetaEvent": PpsfMidiMetaEvent,
                "VsqNoteEvent": PpsfVsqNoteEvent,
                "Vocaloid3NoteEvent": PpsfVocaloid3NoteEvent,
                "AudioEvent": PpsfAudioEvent,
            },
            Bytes(this.size),
        ),
    ),
)

PpsfEventIndexArray = ppsf_prefixed_array(Int32ul)

PpsfIClipBase = Struct(
    "field_4" / Int16ul,
    "field_6" / Byte,
    "event_indices" / PpsfEventIndexArray,
    "name" / PpsfVarIntString,
    "flag" / Byte,
    "extension"
    / If(
        lambda ctx: _is_new_version(ctx, 9, 3),
        PpsfExtension,
    ),
)

PpsfNoteClipBase = Struct(
    "iclip" / PpsfIClipBase,
    "offset" / Int32ul,
    "field_108" / Int32ul,
    "song_end_anchor_a" / Int32ul,
    "field_116" / Int32ul,
    "song_end_anchor_b" / Int32ul,
    "field_124" / Byte,
    "field_128" / Int32ul,
    "field_132" / Int32ul,
)

PpsfRenderableClipFields = Struct(
    "field_4" / Int16ul,
    "field_6" / Byte,
)

PpsfAudioClip = Struct(
    "noteclip" / PpsfNoteClipBase,
    "data" / GreedyBytes,
)

PpsfMidiNoteClip = Struct(
    "data" / GreedyBytes,
)

PpsfMidiMetaClip = Struct(
    "data" / GreedyBytes,
)

PpsfMidiSysExClip = Struct(
    "data" / GreedyBytes,
)

PpsfAutomationClip = Struct(
    "field_4" / Int16ul,
    "field_6" / Byte,
    "event_indices" / PpsfEventIndexArray,
    "data" / GreedyBytes,
)

PpsfVsqNoteClip = Struct(
    "noteclip" / PpsfNoteClipBase,
    "v_field_156" / Int16ul,
    "v_field_158" / Byte,
    "data" / GreedyBytes,
)

PpsfVocaloid3NoteClip = Struct(
    "noteclip" / PpsfNoteClipBase,
    "v3_field_156" / Int16ul,
    "v3_field_158" / Byte,
    "data" / GreedyBytes,
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
    "data"
    / FixedSized(
        this.size - 2,
        Switch(
            this.magic,
            {
                "AudioClip": PpsfAudioClip,
                "MidiNoteClip": PpsfMidiNoteClip,
                "MidiMetaClip": PpsfMidiMetaClip,
                "MidiSysExClip": PpsfMidiSysExClip,
                "VsqNoteClip": PpsfVsqNoteClip,
                "Vocaloid3NoteClip": PpsfVocaloid3NoteClip,
                "AutomationClip": PpsfAutomationClip,
            },
            Bytes(this.size - 2),
        ),
    ),
)

PpsfTrackTags = Mapping(
    Bytes(4),
    {
        "AudioEventTrack": b"AETK",
        "AudioInDeviceTrack": b"AIDT",
        "AudioOutDeviceTrack": b"AODT",
        "AudioSendTrack": b"ASTR",
        "MidiEventTrack": b"METK",
        "MidiInDeviceTrack": b"MIDT",
        "MidiOutDeviceTrack": b"MODT",
        "MusicalParamTrack": b"MPTR",
        "Vocaloid2EventTrack": b"VETK",
        "Vocaloid3EventTrack": b"V3TK",
    },
)

PpsfTrackBase = Struct(
    "field_0" / Int16ul,
    "flag_2" / Byte,
    "v3_event_plugin_indices" / ppsf_prefixed_array(Int16ul),
    "audio_event_plugin_indices" / ppsf_prefixed_array(Int16ul),
    "field_180" / Int16ul,
    "synth_plugin_index" / Int16ul,
    "field_184" / Int32ul,
    "byte_188" / Byte,
    "byte_189" / Byte,
    "byte_190" / Byte,
    "source_track_indices" / ppsf_prefixed_array(Int16ul),
    "byte_236" / Byte,
    "byte_237" / Byte,
    "ext_byte" / Byte,
)

PpsfAudioEventTrackData = Struct(
    "base" / PpsfTrackBase,
    "name" / PpsfVarIntString,
    "clip_indices" / ppsf_prefixed_array(Int16ul),
    "data" / GreedyBytes,
)

PpsfMidiEventTrackData = Struct(
    "base" / PpsfTrackBase,
    "name" / PpsfVarIntString,
    "clip_indices" / ppsf_prefixed_array(Int16ul),
    "midi_field_352" / Int16ul,
    "midi_field_354" / Int16ul,
    "data" / GreedyBytes,
)

PpsfVsqEventTrackData = Struct(
    "base" / PpsfTrackBase,
    "name" / PpsfVarIntString,
    "clip_indices" / ppsf_prefixed_array(Int16ul),
    "vsq_byte_352" / Byte,
    "data" / GreedyBytes,
)

PpsfVocaloid3EventTrackData = Struct(
    "base" / PpsfTrackBase,
    "name" / PpsfVarIntString,
    "clip_indices" / ppsf_prefixed_array(Int16ul),
    "data" / GreedyBytes,
)

PpsfAudioDeviceTrackImpl = Struct(
    "byte_12" / Byte,
    "byte_13" / Byte,
    "field_16" / Int32ul,
    "name" / PpsfVarIntString,
    "field_44" / Int16ul,
)

PpsfAudioDeviceTrackData = Struct(
    "base" / PpsfTrackBase,
    "device_impl" / PpsfAudioDeviceTrackImpl,
    "data" / GreedyBytes,
)

PpsfMidiDeviceTrackImpl = Struct(
    "field_12" / Int32ul,
    "name" / PpsfVarIntString,
)

PpsfMidiDeviceTrackData = Struct(
    "base" / PpsfTrackBase,
    "device_impl" / PpsfMidiDeviceTrackImpl,
    "data" / GreedyBytes,
)

PpsfMusicalParamTrackData = Struct(
    "base" / PpsfTrackBase,
    "mp_plugin_index_1" / Int16ul,
    "mp_plugin_index_2" / Int16ul,
    "mp_plugin_index_3" / Int16ul,
    "data" / GreedyBytes,
)

PpsfAudioSendTrackData = Struct(
    "base" / PpsfTrackBase,
    "data" / GreedyBytes,
)

PpsfTrack = Struct(
    "magic" / PpsfTrackTags,
    "size" / Int32ul,
    "index" / Int16ul,
    "data"
    / FixedSized(
        this.size - 2,
        Switch(
            this.magic,
            {
                "AudioEventTrack": PpsfAudioEventTrackData,
                "AudioInDeviceTrack": PpsfAudioDeviceTrackData,
                "AudioOutDeviceTrack": PpsfAudioDeviceTrackData,
                "AudioSendTrack": PpsfAudioSendTrackData,
                "MidiEventTrack": PpsfMidiEventTrackData,
                "MidiInDeviceTrack": PpsfMidiDeviceTrackData,
                "MidiOutDeviceTrack": PpsfMidiDeviceTrackData,
                "MusicalParamTrack": PpsfMusicalParamTrackData,
                "Vocaloid2EventTrack": PpsfVsqEventTrackData,
                "Vocaloid3EventTrack": PpsfVocaloid3EventTrackData,
            },
            GreedyBytes,
        ),
    ),
)

PpsfPluginParameterRecord = Struct(
    "value" / Int32ul,
    "marker" / Int32ul,
)

PpsfEventControlPluginBody = Struct(
    "name" / PpsfVarIntString,
    "reserved" / Bytes(10),
    "flag" / Int16ul,
    "parameters" / PrefixedArray(Byte, PpsfPluginParameterRecord),
    "self_clip_idx" / Int16ul,
    "vfxc_blob" / PpsfExtension,
    "trailing" / GreedyBytes,
)

PpsfV3SynthPluginBody = Struct(
    "name" / PpsfVarIntString,
    "required_tag" / PpsfVarIntString,
    "data" / GreedyBytes,
)

PpsfVstPlugin = Struct(
    "plugin_id" / PascalString(Byte, "utf-8"),
    "plugin_name" / PascalString(Byte, "utf-8"),
    "plugin_path" / PascalString(Byte, "utf-8"),
    "plugin_flags" / Int32ul,
    "parameters" / GreedyRange(PpsfPluginParameterRecord),
)

PpsfEventControlPlugin = Struct(
    "event_type" / Byte,
    "track_index" / Int32ul,
    "parameters" / GreedyRange(PpsfPluginParameterRecord),
)

PpsfSynthPlugin = Struct(
    "synth_type" / Byte,
    "voice_library_id" / PascalString(Byte, "utf-8"),
    "voice_library_name" / PascalString(Byte, "utf-8"),
    "parameters" / GreedyRange(PpsfPluginParameterRecord),
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
    "data"
    / FixedSized(
        this.size - 2,
        Switch(
            this.magic,
            {
                "AudioEventControlPlugin": PpsfEventControlPluginBody,
                "MidiEventControlPlugin": PpsfEventControlPluginBody,
                "VsqEventControlPlugin": PpsfEventControlPluginBody,
                "Vocaloid3EventControlPlugin": PpsfEventControlPluginBody,
                "MusicParamEventControlPlugin": PpsfEventControlPluginBody,
                "Vocaloid3SynthEventControlPlugin": PpsfV3SynthPluginBody,
                "SynthEventControlPlugin": PpsfV3SynthPluginBody,
            },
            Bytes(this.size - 2),
        ),
    ),
)

PpsfPlugins = Struct(
    "audio_event_control_plugins" / ppsf_prefixed_array(PpsfPlugin),
    "midi_event_control_plugins" / ppsf_prefixed_array(PpsfPlugin),
    "vsq_event_control_plugins" / ppsf_prefixed_array(PpsfPlugin),
    "vocaloid3_event_control_plugins" / ppsf_prefixed_array(PpsfPlugin),
    "synth_event_control_plugins" / ppsf_prefixed_array(PpsfPlugin),
    "vocaloid3_synth_event_control_plugins" / ppsf_prefixed_array(PpsfPlugin),
    "music_param_event_control_plugins" / ppsf_prefixed_array(PpsfPlugin),
    "vst_audio_plugins" / ppsf_prefixed_array(PpsfPlugin),
    "vst_midi_plugins" / ppsf_prefixed_array(PpsfPlugin),
    "vst_synth_plugins" / ppsf_prefixed_array(PpsfPlugin),
    "extension_data" / GreedyBytes,
)

PpsfTracksTags = Mapping(
    Bytes(4),
    {
        "AudioEventTracks": b"AETS",
        "MidiEventTracks": b"METS",
        "Vocaloid2EventTracks": b"VETS",
        "Vocaloid3EventTracks": b"V3TS",
        "MidiInDeviceTracks": b"MIDS",
        "MidiOutDeviceTracks": b"MODS",
        "AudioInDeviceTracks": b"AIDS",
        "AudioOutDeviceTracks": b"AODS",
        "AudioSendTracks": b"ASTS",
        "MusicalParamTracks": b"MPTS",
    },
)

PpsfTypedTracks = Struct(
    "magic" / PpsfTracksTags,
    "size" / Int32ul,
    "data" / FixedSized(this.size, ppsf_prefixed_array(PpsfTrack)),
)

PpsfTracks = Struct(
    "audio_event_tracks" / PpsfTypedTracks,
    "midi_event_tracks" / PpsfTypedTracks,
    "vocaloid2_event_tracks" / PpsfTypedTracks,
    "vocaloid3_event_tracks" / PpsfTypedTracks,
    "midi_in_device_tracks" / PpsfTypedTracks,
    "midi_out_device_tracks" / PpsfTypedTracks,
    "audio_in_device_tracks" / PpsfTypedTracks,
    "audio_out_device_tracks" / PpsfTypedTracks,
    "audio_send_tracks" / PpsfTypedTracks,
    "musical_param_tracks" / PpsfTypedTracks,
    "extension_data" / GreedyBytes,
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
        "Marker": b"UMKR",
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

PpsfVoiceParameters = Struct(
    "param1" / Byte,
    "param2" / Byte,
    "param3" / Byte,
    "param4" / Byte,
    "param5" / Byte,
)

PpsfVoiceSetting = Struct(
    "name" / PpsfVarIntString,
    "parameters" / PpsfVoiceParameters,
)

PpsfProjectV2SingerEntry = Struct(
    "singer_id" / PpsfVarIntString,
    "singer_name" / PpsfVarIntString,
    "voice_parameters" / PpsfVoiceParameters,
    "unknown1" / Byte,
    "unknown2" / Byte,
)

PpsfProjectV3SingerEntry = Struct(
    "singer_id" / PpsfVarIntString,
    "singer_name" / PpsfVarIntString,
    "unknown1" / Byte,
    "unknown2" / Byte,
    "voice_setting" / PpsfVoiceSetting,
    "has_extra_voice_setting" / Byte,
    "extra_voice_setting" / If(this.has_extra_voice_setting, PpsfVoiceSetting),
)

PpsfProjectImpl = Struct(
    "project_field_12" / Int32ul,
    "project_field_16" / Int32ul,
    "project_field_20" / Byte,
    "project_field_24" / Int32ul,
    "project_field_28" / Int32ul,
    "project_field_32" / Int32ul,
    "project_field_36" / Int32ul,
    "project_field_40" / Int32ul,
    "vocaloid2_singers" / ppsf_prefixed_array(PpsfProjectV2SingerEntry),
    "vocaloid3_singers" / ppsf_prefixed_array(PpsfProjectV3SingerEntry),
)

PpsfProject = Struct(
    "impl" / PpsfProjectImpl,
    "extension_array_1" / ppsf_prefixed_array(Int16ul),
    "extension_array_2" / ppsf_prefixed_array(Int16ul),
    "extension_array_3" / ppsf_prefixed_array(Int16ul),
    "extension_array_4" / ppsf_prefixed_array(Int16ul),
    "extension_array_5" / ppsf_prefixed_array(Int16ul),
    "extension_array_6" / ppsf_prefixed_array(Int16ul),
    "extension_array_7" / ppsf_prefixed_array(Int16ul),
    "extension_array_8" / ppsf_prefixed_array(Int16ul),
    "extension_array_9" / ppsf_prefixed_array(Int16ul),
    "extension_flags" / Int16ul,
    "extension_data" / GreedyBytes,
)

PpsfTransport = Struct(
    "transport_value" / Int32ul,
    "transport_flags" / Int16ul,
)

PpsfConfig = Struct(
    "config_value_1" / Int32ul,
    "config_value_2" / Int32ul,
    "config_flags" / Int16ul,
)

PpsfDeviceSubcomponent = Struct(
    "magic" / Const(b"MIDV"),
    "field" / Int16ul,
    "name" / PpsfVarIntString,
)

PpsfDeviceSubcomponentArray = Struct(
    "size" / IfThenElse(lambda ctx: _is_new_version(ctx, 9, 3), Byte, Int16ul),
    "subcomponents" / Array(this.size, PpsfDeviceSubcomponent),
)

PpsfDevices = Struct(
    "subcomponent_array_1" / PpsfDeviceSubcomponentArray,
    "subcomponent_array_2" / PpsfDeviceSubcomponentArray,
    "subcomponent_array_3" / PpsfDeviceSubcomponentArray,
    "subcomponent_array_4" / PpsfDeviceSubcomponentArray,
    "subcomponent_array_5" / PpsfDeviceSubcomponentArray,
    "device_field_1" / Int16ul,
    "device_field_2" / Int16ul,
    "device_field_3" / Int32ul,
)

PpsfClips = Struct(
    "audio_clips" / ppsf_prefixed_array(PpsfClip),
    "midi_note_clips" / ppsf_prefixed_array(PpsfClip),
    "midi_sysex_clips" / ppsf_prefixed_array(PpsfClip),
    "midi_meta_clips" / ppsf_prefixed_array(PpsfClip),
    "vsq_note_clips" / ppsf_prefixed_array(PpsfClip),
    "vocaloid3_note_clips" / ppsf_prefixed_array(PpsfClip),
    "automation_clips" / ppsf_prefixed_array(PpsfClip),
    "extension_data" / GreedyBytes,
)

PpsfChunk = Struct(
    "magic" / PpsfChunkTags,
    "size" / Int32ul,
    "data"
    / FixedSized(
        this.size,
        Switch(
            this.magic,
            {
                "Info": PpsfVarIntString,
                "Project": PpsfProject,
                "Transport": PpsfTransport,
                "Config": PpsfConfig,
                "Devices": PpsfDevices,
                "Tracks": PpsfTracks,
                "Clips": PpsfClips,
                "Events": ppsf_prefixed_array(PpsfEvent),
                "Plugins": PpsfPlugins,
            },
            Bytes(this.size),
        ),
    ),
)


PpsfLegacyProject = Struct(
    "magic" / Const(b"PPSF"),
    "size" / Int32ul,
    "version_string" / PascalString(Int16ul, "ascii"),
    "version" / Computed(lambda ctx: _parse_version(ctx.version_string)),
    "chunks" / GreedyRange(PpsfChunk),
)
