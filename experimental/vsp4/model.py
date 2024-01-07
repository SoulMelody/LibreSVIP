from __future__ import annotations

from typing import TYPE_CHECKING

import proto

if TYPE_CHECKING:
    from collections.abc import MutableMapping, MutableSequence

__protobuf__ = proto.module(
    package="org.vocalsharp.vocalshaper.vsp4",
    manifest={
        "MainGraph",
        "MixerTrack",
        "MixerTrackInfo",
        "PluginDock",
        "Plugin",
        "PluginInfo",
        "PluginState",
        "VocalShaperProject",
        "ProjectInfo",
        "Recorder",
        "SourceRecorderInstance",
        "SeqSourceInstance",
        "SeqTrack",
        "SeqTrackInfo",
        "SourceInstanceList",
        "Source",
        "SourceList",
        "AudioInputConnection",
        "AudioOutputConnection",
        "AudioSendConnection",
        "MIDIInputConnection",
        "MIDIOutputConnection",
        "MIDISendConnection",
        "Version",
        "TrackType",
    },
)


class SourceRecorderInstance(proto.Message):
    index: int = proto.Field(
        proto.UINT32,
        number=1,
    )
    offset: float = proto.Field(
        proto.DOUBLE,
        number=2,
    )


class Recorder(proto.Message):
    sources: MutableSequence[SourceRecorderInstance] = proto.RepeatedField(
        proto.MESSAGE,
        number=1,
        message=SourceRecorderInstance,
    )


class TrackType(proto.Enum):
    DISABLED = 0
    MONO = 10
    STEREO = 20
    LCR = 30
    LRS = 31
    LCRS = 40
    SUR_5_0 = 50
    SUR_5_1 = 51
    SUR_5_0_2 = 502
    SUR_5_1_2 = 512
    SUR_5_0_4 = 504
    SUR_5_1_4 = 514
    SUR_6_0 = 60
    SUR_6_1 = 61
    SUR_6_0_M = 600
    SUR_6_1_M = 610
    SUR_7_0 = 70
    SUR_7_0_SDSS = 700
    SUR_7_1 = 71
    SUR_7_1_SDSS = 710
    SUR_7_0_2 = 702
    SUR_7_1_2 = 712
    SUR_7_0_4 = 704
    SUR_7_1_4 = 714
    SUR_7_0_6 = 706
    SUR_7_1_6 = 716
    SUR_9_0_4 = 904
    SUR_9_1_4 = 914
    SUR_9_0_6 = 906
    SUR_9_1_6 = 916
    QUADRAPHONIC = 4000
    PENTAGONAL = 5000
    HEXAGONAL = 6000
    OCTAGONAL = 8000
    AMBISONIC_0 = 100
    AMBISONIC_1 = 101
    AMBISONIC_2 = 102
    AMBISONIC_3 = 103
    AMBISONIC_4 = 104
    AMBISONIC_5 = 105
    AMBISONIC_6 = 106
    AMBISONIC_7 = 107


class Version(proto.Message):
    major: int = proto.Field(
        proto.UINT32,
        number=1,
    )
    minor: int = proto.Field(
        proto.UINT32,
        number=2,
    )
    patch: int = proto.Field(
        proto.UINT32,
        number=3,
    )


class MIDIInputConnection(proto.Message):
    dst: int = proto.Field(
        proto.UINT32,
        number=1,
    )


class MIDIOutputConnection(proto.Message):
    src: int = proto.Field(
        proto.UINT32,
        number=1,
    )


class MIDISendConnection(proto.Message):
    src: int = proto.Field(
        proto.UINT32,
        number=1,
    )
    dst: int = proto.Field(
        proto.UINT32,
        number=2,
    )


class AudioInputConnection(proto.Message):
    src_channel: int = proto.Field(
        proto.UINT32,
        number=1,
    )
    dst: int = proto.Field(
        proto.UINT32,
        number=2,
    )
    dst_channel: int = proto.Field(
        proto.UINT32,
        number=3,
    )


class AudioOutputConnection(proto.Message):
    src: int = proto.Field(
        proto.UINT32,
        number=1,
    )
    src_channel: int = proto.Field(
        proto.UINT32,
        number=2,
    )
    dst_channel: int = proto.Field(
        proto.UINT32,
        number=3,
    )


class AudioSendConnection(proto.Message):
    src: int = proto.Field(
        proto.UINT32,
        number=1,
    )
    src_channel: int = proto.Field(
        proto.UINT32,
        number=2,
    )
    dst: int = proto.Field(
        proto.UINT32,
        number=3,
    )
    dst_channel: int = proto.Field(
        proto.UINT32,
        number=4,
    )


class SeqTrackInfo(proto.Message):
    name: str = proto.Field(
        proto.STRING,
        number=1,
    )
    color: int = proto.Field(
        proto.FIXED32,
        number=2,
    )


class SeqSourceInstance(proto.Message):
    index: int = proto.Field(
        proto.UINT32,
        number=1,
    )
    start_pos: float = proto.Field(
        proto.DOUBLE,
        number=2,
    )
    end_pos: float = proto.Field(
        proto.DOUBLE,
        number=3,
    )
    offset: float = proto.Field(
        proto.DOUBLE,
        number=4,
    )


class SourceInstanceList(proto.Message):
    sources: MutableSequence[SeqSourceInstance] = proto.RepeatedField(
        proto.MESSAGE,
        number=1,
        message="SeqSourceInstance",
    )


class SeqTrack(proto.Message):
    type_: TrackType = proto.Field(
        proto.ENUM,
        number=1,
        enum=TrackType,
    )
    info: SeqTrackInfo = proto.Field(
        proto.MESSAGE,
        number=2,
        message="SeqTrackInfo",
    )
    bypassed: bool = proto.Field(
        proto.BOOL,
        number=3,
    )
    sources: SourceInstanceList = proto.Field(
        proto.MESSAGE,
        number=4,
        message="SourceInstanceList",
    )


class PluginInfo(proto.Message):
    info_id: str = proto.Field(
        proto.STRING,
        number=1,
    )
    decorator_type: TrackType = proto.Field(
        proto.ENUM,
        number=2,
        enum=TrackType,
    )


class PluginState(proto.Message):
    data: bytes = proto.Field(
        proto.BYTES,
        number=1,
    )
    midi_channel: int = proto.Field(
        proto.UINT32,
        number=2,
    )
    param_cc_links: MutableMapping[int, int] = proto.MapField(
        proto.UINT32,
        proto.UINT32,
        number=3,
    )
    midi_output: bool = proto.Field(
        proto.BOOL,
        number=4,
    )
    midi_intercept: bool = proto.Field(
        proto.BOOL,
        number=5,
    )


class Plugin(proto.Message):
    info: PluginInfo = proto.Field(
        proto.MESSAGE,
        number=1,
        message="PluginInfo",
    )
    state: PluginState = proto.Field(
        proto.MESSAGE,
        number=2,
        message="PluginState",
    )
    bypassed: bool = proto.Field(
        proto.BOOL,
        number=3,
    )


class MixerTrackInfo(proto.Message):
    name: str = proto.Field(
        proto.STRING,
        number=1,
    )
    color: int = proto.Field(
        proto.FIXED32,
        number=2,
    )


class PluginDock(proto.Message):
    plugins: MutableSequence[Plugin] = proto.RepeatedField(
        proto.MESSAGE,
        number=1,
        message=Plugin,
    )
    connections: MutableSequence[AudioInputConnection] = proto.RepeatedField(
        proto.MESSAGE,
        number=2,
        message=AudioInputConnection,
    )


class MixerTrack(proto.Message):
    type_: TrackType = proto.Field(
        proto.ENUM,
        number=1,
        enum=TrackType,
    )
    info: MixerTrackInfo = proto.Field(
        proto.MESSAGE,
        number=2,
        message="MixerTrackInfo",
    )
    bypassed: bool = proto.Field(
        proto.BOOL,
        number=3,
    )
    additional_buses: int = proto.Field(
        proto.UINT32,
        number=4,
    )
    effects: PluginDock = proto.Field(
        proto.MESSAGE,
        number=5,
        message="PluginDock",
    )
    muted: bool = proto.Field(
        proto.BOOL,
        number=6,
    )
    gain: float = proto.Field(
        proto.DOUBLE,
        number=7,
    )
    panner: float = proto.Field(
        proto.DOUBLE,
        number=8,
    )
    slider: float = proto.Field(
        proto.DOUBLE,
        number=9,
    )


class Source(proto.Message):
    class Type(proto.Enum):
        AUDIO = 0
        MIDI = 1
        SYNTH = 2

    type_: Type = proto.Field(
        proto.ENUM,
        number=1,
        enum=Type,
    )
    source_id: int = proto.Field(
        proto.INT32,
        number=5,
    )
    path: str = proto.Field(
        proto.STRING,
        number=2,
    )
    name: str = proto.Field(
        proto.STRING,
        number=3,
    )
    synthesizer: Plugin = proto.Field(
        proto.MESSAGE,
        number=4,
        message=Plugin,
    )


class SourceList(proto.Message):
    sources: MutableSequence[Source] = proto.RepeatedField(
        proto.MESSAGE,
        number=1,
        message=Source,
    )


class MainGraph(proto.Message):
    class Connections(proto.Message):
        midi_i_2_instr: MutableSequence[MIDIInputConnection] = proto.RepeatedField(
            proto.MESSAGE,
            number=1,
            message=MIDIInputConnection,
        )
        midi_src_2_instr: MutableSequence[MIDISendConnection] = proto.RepeatedField(
            proto.MESSAGE,
            number=2,
            message=MIDISendConnection,
        )
        midi_src_2_track: MutableSequence[MIDISendConnection] = proto.RepeatedField(
            proto.MESSAGE,
            number=3,
            message=MIDISendConnection,
        )
        audio_src_2_track: MutableSequence[AudioSendConnection] = proto.RepeatedField(
            proto.MESSAGE,
            number=4,
            message=AudioSendConnection,
        )
        audio_instr_2_track: MutableSequence[AudioSendConnection] = proto.RepeatedField(
            proto.MESSAGE,
            number=5,
            message=AudioSendConnection,
        )
        midi_i_2_track: MutableSequence[MIDIInputConnection] = proto.RepeatedField(
            proto.MESSAGE,
            number=6,
            message=MIDIInputConnection,
        )
        audio_i_2_rack: MutableSequence[AudioInputConnection] = proto.RepeatedField(
            proto.MESSAGE,
            number=7,
            message=AudioInputConnection,
        )
        audio_track_2_o: MutableSequence[AudioOutputConnection] = proto.RepeatedField(
            proto.MESSAGE,
            number=8,
            message=AudioOutputConnection,
        )
        audio_track_2_track: MutableSequence[AudioSendConnection] = proto.RepeatedField(
            proto.MESSAGE,
            number=9,
            message=AudioSendConnection,
        )
        midi_track_2_o: MutableSequence[MIDIOutputConnection] = proto.RepeatedField(
            proto.MESSAGE,
            number=10,
            message=MIDIOutputConnection,
        )

    seq_tracks: MutableSequence[SeqTrack] = proto.RepeatedField(
        proto.MESSAGE,
        number=1,
        message=SeqTrack,
    )
    instrs: MutableSequence[Plugin] = proto.RepeatedField(
        proto.MESSAGE,
        number=2,
        message=Plugin,
    )
    mixer_tracks: MutableSequence[MixerTrack] = proto.RepeatedField(
        proto.MESSAGE,
        number=3,
        message=MixerTrack,
    )
    connections: Connections = proto.Field(
        proto.MESSAGE,
        number=4,
        message=Connections,
    )
    recorder: Recorder = proto.Field(
        proto.MESSAGE,
        number=5,
        message=Recorder,
    )


class ProjectInfo(proto.Message):
    created_time: int = proto.Field(
        proto.FIXED32,
        number=1,
    )
    last_saved_time: int = proto.Field(
        proto.FIXED32,
        number=2,
    )
    spent_time: int = proto.Field(
        proto.FIXED32,
        number=3,
    )
    created_platform: str = proto.Field(
        proto.STRING,
        number=4,
    )
    last_saved_platform: str = proto.Field(
        proto.STRING,
        number=5,
    )
    authors: MutableSequence[str] = proto.RepeatedField(
        proto.STRING,
        number=6,
    )


class VocalShaperProject(proto.Message):
    version: Version = proto.Field(
        proto.MESSAGE,
        number=1,
        message=Version,
    )
    info: ProjectInfo = proto.Field(
        proto.MESSAGE,
        number=2,
        message=ProjectInfo,
    )
    sources: SourceList = proto.Field(
        proto.MESSAGE,
        number=3,
        message=SourceList,
    )
    graph: MainGraph = proto.Field(
        proto.MESSAGE,
        number=4,
        message=MainGraph,
    )
