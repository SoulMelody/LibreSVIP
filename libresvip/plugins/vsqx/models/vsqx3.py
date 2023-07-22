from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from ..enums import VocaloidLanguage

VSQ3_NS = "http://www.yamaha.co.jp/vocaloid/schema/vsq3/"


class ParameterNames(Enum):
    DYN = "DYN"
    BRE = "BRE"
    BRI = "BRI"
    CLE = "CLE"
    GEN = "GEN"
    POR = "POR"
    PBS = "PBS"
    PIT = "PIT"


@dataclass
class Aux:
    class Meta:
        name = "aux"
        namespace = VSQ3_NS

    aux_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "auxID",
            "type": "Element",
            "required": True,
        },
    )
    content: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class Dyn:
    class Meta:
        name = "dyn"
        namespace = VSQ3_NS

    pos_sec: Optional[int] = field(
        default=None,
        metadata={
            "name": "posSec",
            "type": "Element",
            "required": True,
        },
    )
    dyn_val: Optional[int] = field(
        default=None,
        metadata={
            "name": "dynVal",
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class Pch:
    class Meta:
        name = "pch"
        namespace = VSQ3_NS

    pos_sec: Optional[int] = field(
        default=None,
        metadata={
            "name": "posSec",
            "type": "Element",
            "required": True,
        },
    )
    pch_val: Optional[int] = field(
        default=None,
        metadata={
            "name": "pchVal",
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class Phnm:
    class Meta:
        name = "phnm"
        namespace = VSQ3_NS

    pos_sec: Optional[int] = field(
        default=None,
        metadata={
            "name": "posSec",
            "type": "Element",
            "required": True,
        },
    )
    dur_sec: Optional[int] = field(
        default=None,
        metadata={
            "name": "durSec",
            "type": "Element",
            "required": True,
        },
    )
    phnm_str: Optional[str] = field(
        default=None,
        metadata={
            "name": "phnmStr",
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class SeqAttr:
    class Meta:
        name = "seqAttr"
        namespace = VSQ3_NS

    elem: list["SeqAttr.Elem"] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )
    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )

    @dataclass
    class Elem:
        pos_nrm: Optional[int] = field(
            default=None,
            metadata={
                "name": "posNrm",
                "type": "Element",
                "required": True,
            },
        )
        elv: Optional[int] = field(
            default=None,
            metadata={
                "type": "Element",
                "required": True,
            },
        )


@dataclass
class Singer:
    class Meta:
        name = "singer"
        namespace = VSQ3_NS

    pos_tick: Optional[int] = field(
        default=None,
        metadata={
            "name": "posTick",
            "type": "Element",
            "required": True,
        },
    )
    v_bs: Optional[VocaloidLanguage] = field(
        default=VocaloidLanguage.SIMPLIFIED_CHINESE,
        metadata={
            "name": "vBS",
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 127,
        },
    )
    v_pc: Optional[int] = field(
        default=0,
        metadata={
            "name": "vPC",
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 127,
        },
    )


@dataclass
class StylePlugin:
    class Meta:
        name = "stylePlugin"
        namespace = VSQ3_NS

    style_plugin_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "stylePluginID",
            "type": "Element",
            "required": True,
            "length": 36,
        },
    )
    style_plugin_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "stylePluginName",
            "type": "Element",
            "required": True,
        },
    )
    version: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class Tempo:
    class Meta:
        name = "tempo"
        namespace = VSQ3_NS

    pos_tick: Optional[int] = field(
        default=None,
        metadata={
            "name": "posTick",
            "type": "Element",
            "required": True,
        },
    )
    bpm: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class TimeSig:
    class Meta:
        name = "timeSig"
        namespace = VSQ3_NS

    pos_mes: Optional[int] = field(
        default=None,
        metadata={
            "name": "posMes",
            "type": "Element",
            "required": True,
        },
    )
    nume: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    denomi: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class TypeParamAttr:
    class Meta:
        name = "typeParamAttr"

    value: Optional[int] = field(
        default=None,
        metadata={
            "required": True,
        },
    )
    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass
class TypePhonemes:
    class Meta:
        name = "typePhonemes"

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    lock: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 1,
        },
    )


class TypeResolution(Enum):
    VALUE_16 = 16
    VALUE_24 = 24
    VALUE_32 = 32


class TypeSamplerate(Enum):
    VALUE_44100 = 44100
    VALUE_48000 = 48000
    VALUE_96000 = 96000


class TypeVstSdkversion(Enum):
    VALUE_0 = 0
    VALUE_2 = 2
    VALUE_3 = 3


@dataclass
class VVoiceParam:
    class Meta:
        name = "vVoiceParam"
        namespace = VSQ3_NS

    bre: Optional[int] = field(
        default=0,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": -127,
            "max_inclusive": 127,
        },
    )
    bri: Optional[int] = field(
        default=0,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": -127,
            "max_inclusive": 127,
        },
    )
    cle: Optional[int] = field(
        default=0,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": -127,
            "max_inclusive": 127,
        },
    )
    gen: Optional[int] = field(
        default=0,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": -127,
            "max_inclusive": 127,
        },
    )
    ope: Optional[int] = field(
        default=0,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": -127,
            "max_inclusive": 127,
        },
    )


@dataclass
class Voice:
    class Meta:
        name = "voice"
        namespace = VSQ3_NS

    pos_sec: Optional[int] = field(
        default=None,
        metadata={
            "name": "posSec",
            "type": "Element",
            "required": True,
        },
    )
    v_bs: Optional[VocaloidLanguage] = field(
        default=VocaloidLanguage.SIMPLIFIED_CHINESE,
        metadata={
            "name": "vBS",
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 127,
        },
    )
    v_pc: Optional[int] = field(
        default=0,
        metadata={
            "name": "vPC",
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 127,
        },
    )


@dataclass
class MCtrl:
    class Meta:
        name = "mCtrl"
        namespace = VSQ3_NS

    pos_tick: Optional[int] = field(
        default=None,
        metadata={
            "name": "posTick",
            "type": "Element",
            "required": True,
        },
    )
    attr: Optional[TypeParamAttr] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class MasterTrack:
    class Meta:
        name = "masterTrack"
        namespace = VSQ3_NS

    seq_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "seqName",
            "type": "Element",
            "required": True,
        },
    )
    comment: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    resolution: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    pre_measure: Optional[int] = field(
        default=1,
        metadata={
            "name": "preMeasure",
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 127,
        },
    )
    time_sig: list[TimeSig] = field(
        default_factory=list,
        metadata={
            "name": "timeSig",
            "type": "Element",
            "min_occurs": 1,
        },
    )
    tempo: list[Tempo] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )


@dataclass
class NoteStyle:
    class Meta:
        name = "noteStyle"
        namespace = VSQ3_NS

    attr: list[TypeParamAttr] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    seq_attr: list[SeqAttr] = field(
        default_factory=list,
        metadata={
            "name": "seqAttr",
            "type": "Element",
        },
    )


@dataclass
class PCtrl:
    class Meta:
        name = "pCtrl"
        namespace = VSQ3_NS

    pos_sec: Optional[int] = field(
        default=None,
        metadata={
            "name": "posSec",
            "type": "Element",
            "required": True,
        },
    )
    attr: Optional[TypeParamAttr] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class PartStyle:
    class Meta:
        name = "partStyle"
        namespace = VSQ3_NS

    attr: list[TypeParamAttr] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )


@dataclass
class PhraseStyle:
    class Meta:
        name = "phraseStyle"
        namespace = VSQ3_NS

    pos_tick: Optional[int] = field(
        default=None,
        metadata={
            "name": "posTick",
            "type": "Element",
            "required": True,
        },
    )
    attr: list[TypeParamAttr] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )


@dataclass
class SCtrl:
    class Meta:
        name = "sCtrl"
        namespace = VSQ3_NS

    pos_tick: Optional[int] = field(
        default=None,
        metadata={
            "name": "posTick",
            "type": "Element",
            "required": True,
        },
    )
    attr: Optional[TypeParamAttr] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class VVoice:
    class Meta:
        name = "vVoice"
        namespace = VSQ3_NS

    v_bs: Optional[VocaloidLanguage] = field(
        default=VocaloidLanguage.SIMPLIFIED_CHINESE,
        metadata={
            "name": "vBS",
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 127,
        },
    )
    v_pc: Optional[int] = field(
        default=0,
        metadata={
            "name": "vPC",
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 127,
        },
    )
    comp_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "compID",
            "type": "Element",
            "required": True,
            "length": 16,
        },
    )
    v_voice_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "vVoiceName",
            "type": "Element",
            "required": True,
        },
    )
    v_voice_param: Optional[VVoiceParam] = field(
        default_factory=VVoiceParam,
        metadata={
            "name": "vVoiceParam",
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class VstPlugin:
    class Meta:
        name = "vstPlugin"
        namespace = VSQ3_NS

    vst_plugin_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "vstPluginID",
            "type": "Element",
            "required": True,
        },
    )
    vst_plugin_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "vstPluginName",
            "type": "Element",
            "required": True,
        },
    )
    vst_sdkversion: Optional[TypeVstSdkversion] = field(
        default=None,
        metadata={
            "name": "vstSDKVersion",
            "type": "Element",
            "required": True,
        },
    )
    vst_param_num: Optional[int] = field(
        default=None,
        metadata={
            "name": "vstParamNum",
            "type": "Element",
            "required": True,
        },
    )
    vst_param_val: Optional["VstPlugin.VstParamVal"] = field(
        default=None,
        metadata={
            "name": "vstParamVal",
            "type": "Element",
        },
    )
    vst_preset_no: Optional[int] = field(
        default=None,
        metadata={
            "name": "vstPresetNo",
            "type": "Element",
        },
    )
    enable: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 1,
        },
    )
    bypass: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 1,
        },
    )

    @dataclass
    class VstParamVal:
        val: list[int] = field(
            default_factory=list,
            metadata={
                "type": "Element",
            },
        )


@dataclass
class VstPluginSr:
    class Meta:
        name = "vstPluginSR"
        namespace = VSQ3_NS

    vst_plugin_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "vstPluginID",
            "type": "Element",
            "required": True,
        },
    )
    vst_plugin_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "vstPluginName",
            "type": "Element",
            "required": True,
        },
    )
    vst_sdkversion: Optional[TypeVstSdkversion] = field(
        default=None,
        metadata={
            "name": "vstSDKVersion",
            "type": "Element",
            "required": True,
        },
    )
    vst_param_num: Optional[int] = field(
        default=None,
        metadata={
            "name": "vstParamNum",
            "type": "Element",
            "required": True,
        },
    )
    vst_param_val: Optional["VstPluginSr.VstParamVal"] = field(
        default=None,
        metadata={
            "name": "vstParamVal",
            "type": "Element",
        },
    )
    vst_preset_no: Optional[int] = field(
        default=None,
        metadata={
            "name": "vstPresetNo",
            "type": "Element",
        },
    )
    enable: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 1,
        },
    )
    bypass: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 1,
        },
    )

    @dataclass
    class VstParamVal:
        val: list[int] = field(
            default_factory=list,
            metadata={
                "type": "Element",
            },
        )


@dataclass
class WavPart:
    class Meta:
        name = "wavPart"
        namespace = VSQ3_NS

    pos_tick: Optional[int] = field(
        default=None,
        metadata={
            "name": "posTick",
            "type": "Element",
            "required": True,
        },
    )
    play_time: Optional[int] = field(
        default=None,
        metadata={
            "name": "playTime",
            "type": "Element",
            "required": True,
        },
    )
    part_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "partName",
            "type": "Element",
            "required": True,
        },
    )
    comment: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    sample_rate: Optional[TypeSamplerate] = field(
        default=None,
        metadata={
            "name": "sampleRate",
            "type": "Element",
            "required": True,
        },
    )
    sample_reso: Optional[TypeResolution] = field(
        default=None,
        metadata={
            "name": "sampleReso",
            "type": "Element",
            "required": True,
        },
    )
    channels: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": 1,
            "max_inclusive": 2,
        },
    )
    file_path: Optional[str] = field(
        default=None,
        metadata={
            "name": "filePath",
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class StereoTrack:
    class Meta:
        name = "karaokeTrack"
        namespace = VSQ3_NS

    wav_part: list[WavPart] = field(
        default_factory=list,
        metadata={
            "name": "wavPart",
            "type": "Element",
        },
    )


@dataclass
class StereoUnit:
    class Meta:
        name = "karaokeUnit"
        namespace = VSQ3_NS

    in_gain: Optional[int] = field(
        default=None,
        metadata={
            "name": "inGain",
            "type": "Element",
            "required": True,
        },
    )
    vst_plugin: list[VstPlugin] = field(
        default_factory=list,
        metadata={
            "name": "vstPlugin",
            "type": "Element",
            "max_occurs": 2,
        },
    )
    mute: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 1,
        },
    )
    solo: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 1,
        },
    )
    vol: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class MasterUnit:
    class Meta:
        name = "masterUnit"
        namespace = VSQ3_NS

    out_dev: Optional[int] = field(
        default=None,
        metadata={
            "name": "outDev",
            "type": "Element",
            "required": True,
        },
    )
    vst_plugin: list[VstPlugin] = field(
        default_factory=list,
        metadata={
            "name": "vstPlugin",
            "type": "Element",
            "max_occurs": 2,
        },
    )
    vst_plugin_sr: Optional[VstPluginSr] = field(
        default=None,
        metadata={
            "name": "vstPluginSR",
            "type": "Element",
        },
    )
    ret_level: Optional[int] = field(
        default=None,
        metadata={
            "name": "retLevel",
            "type": "Element",
            "required": True,
        },
    )
    vol: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class Note:
    class Meta:
        name = "note"
        namespace = VSQ3_NS

    pos_tick: Optional[int] = field(
        default=None,
        metadata={
            "name": "posTick",
            "type": "Element",
            "required": True,
        },
    )
    dur_tick: Optional[int] = field(
        default=None,
        metadata={
            "name": "durTick",
            "type": "Element",
            "required": True,
        },
    )
    note_num: Optional[int] = field(
        default=None,
        metadata={
            "name": "noteNum",
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 127,
        },
    )
    velocity: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 127,
        },
    )
    lyric: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    phnms: Optional[TypePhonemes] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    note_style: Optional[NoteStyle] = field(
        default=None,
        metadata={
            "name": "noteStyle",
            "type": "Element",
        },
    )


@dataclass
class ProsodyPart:
    class Meta:
        name = "prosodyPart"
        namespace = VSQ3_NS

    pos_tick: Optional[int] = field(
        default=None,
        metadata={
            "name": "posTick",
            "type": "Element",
            "required": True,
        },
    )
    play_time: Optional[int] = field(
        default=None,
        metadata={
            "name": "playTime",
            "type": "Element",
            "required": True,
        },
    )
    part_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "partName",
            "type": "Element",
            "required": True,
        },
    )
    comment: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    voice: list[Voice] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )
    p_ctrl: list[PCtrl] = field(
        default_factory=list,
        metadata={
            "name": "pCtrl",
            "type": "Element",
        },
    )
    pch: list[Pch] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )
    dyn: list[Dyn] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )
    phnm: list[Phnm] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )


@dataclass
class MonoTrack:
    class Meta:
        name = "seTrack"
        namespace = VSQ3_NS

    wav_part: list[WavPart] = field(
        default_factory=list,
        metadata={
            "name": "wavPart",
            "type": "Element",
        },
    )


@dataclass
class MonoUnit:
    class Meta:
        name = "seUnit"
        namespace = VSQ3_NS

    in_gain: Optional[int] = field(
        default=None,
        metadata={
            "name": "inGain",
            "type": "Element",
            "required": True,
        },
    )
    vst_plugin: list[VstPlugin] = field(
        default_factory=list,
        metadata={
            "name": "vstPlugin",
            "type": "Element",
            "max_occurs": 2,
        },
    )
    send_level: Optional[int] = field(
        default=None,
        metadata={
            "name": "sendLevel",
            "type": "Element",
            "required": True,
        },
    )
    send_enable: Optional[int] = field(
        default=None,
        metadata={
            "name": "sendEnable",
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 1,
        },
    )
    mute: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 1,
        },
    )
    solo: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 1,
        },
    )
    pan: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    vol: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class VVoiceTable:
    class Meta:
        name = "vVoiceTable"
        namespace = VSQ3_NS

    v_voice: list[VVoice] = field(
        default_factory=list,
        metadata={
            "name": "vVoice",
            "type": "Element",
            "min_occurs": 1,
        },
    )


@dataclass
class VsUnit:
    class Meta:
        name = "vsUnit"
        namespace = VSQ3_NS

    vs_track_no: Optional[int] = field(
        default=None,
        metadata={
            "name": "vsTrackNo",
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 127,
        },
    )
    in_gain: Optional[int] = field(
        default=None,
        metadata={
            "name": "inGain",
            "type": "Element",
            "required": True,
        },
    )
    vst_plugin: list[VstPlugin] = field(
        default_factory=list,
        metadata={
            "name": "vstPlugin",
            "type": "Element",
            "max_occurs": 2,
        },
    )
    send_level: Optional[int] = field(
        default=None,
        metadata={
            "name": "sendLevel",
            "type": "Element",
            "required": True,
        },
    )
    send_enable: Optional[int] = field(
        default=None,
        metadata={
            "name": "sendEnable",
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 1,
        },
    )
    mute: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 1,
        },
    )
    solo: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 1,
        },
    )
    pan: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    vol: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class Mixer:
    class Meta:
        name = "mixer"
        namespace = VSQ3_NS

    master_unit: Optional[MasterUnit] = field(
        default=None,
        metadata={
            "name": "masterUnit",
            "type": "Element",
            "required": True,
        },
    )
    vs_unit: list[VsUnit] = field(
        default_factory=list,
        metadata={
            "name": "vsUnit",
            "type": "Element",
            "min_occurs": 1,
            "max_occurs": 16,
        },
    )
    mono_unit: Optional[MonoUnit] = field(
        default=None,
        metadata={
            "name": "seUnit",
            "type": "Element",
            "required": True,
        },
    )
    stereo_unit: Optional[StereoUnit] = field(
        default=None,
        metadata={
            "name": "karaokeUnit",
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class MusicalPart:
    class Meta:
        name = "musicalPart"
        namespace = VSQ3_NS

    pos_tick: Optional[int] = field(
        default=None,
        metadata={
            "name": "posTick",
            "type": "Element",
            "required": True,
        },
    )
    play_time: Optional[int] = field(
        default=None,
        metadata={
            "name": "playTime",
            "type": "Element",
            "required": True,
        },
    )
    part_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "partName",
            "type": "Element",
            "required": True,
        },
    )
    comment: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    style_plugin: Optional[StylePlugin] = field(
        default=None,
        metadata={
            "name": "stylePlugin",
            "type": "Element",
            "required": True,
        },
    )
    part_style: Optional[PartStyle] = field(
        default=None,
        metadata={
            "name": "partStyle",
            "type": "Element",
        },
    )
    phrase_style: list[PhraseStyle] = field(
        default_factory=list,
        metadata={
            "name": "phraseStyle",
            "type": "Element",
        },
    )
    singer: list[Singer] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )
    m_ctrl: list[MCtrl] = field(
        default_factory=list,
        metadata={
            "name": "mCtrl",
            "type": "Element",
        },
    )
    s_ctrl: list[SCtrl] = field(
        default_factory=list,
        metadata={
            "name": "sCtrl",
            "type": "Element",
        },
    )
    note: list[Note] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )


@dataclass
class VsTrack:
    class Meta:
        name = "vsTrack"
        namespace = VSQ3_NS

    vs_track_no: Optional[int] = field(
        default=None,
        metadata={
            "name": "vsTrackNo",
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 127,
        },
    )
    track_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "trackName",
            "type": "Element",
            "required": True,
        },
    )
    comment: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musical_part: list[MusicalPart] = field(
        default_factory=list,
        metadata={
            "name": "musicalPart",
            "type": "Element",
            "sequential": True,
        },
    )
    prosody_part: list[ProsodyPart] = field(
        default_factory=list,
        metadata={
            "name": "prosodyPart",
            "type": "Element",
            "sequential": True,
        },
    )


@dataclass
class Vsq3:
    class Meta:
        name = "vsq3"
        namespace = VSQ3_NS

    vender: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    version: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    v_voice_table: Optional[VVoiceTable] = field(
        default_factory=VVoiceTable,
        metadata={
            "name": "vVoiceTable",
            "type": "Element",
            "required": True,
        },
    )
    mixer: Optional[Mixer] = field(
        default_factory=Mixer,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    master_track: Optional[MasterTrack] = field(
        default_factory=MasterTrack,
        metadata={
            "name": "masterTrack",
            "type": "Element",
            "required": True,
        },
    )
    vs_track: list[VsTrack] = field(
        default_factory=list,
        metadata={
            "name": "vsTrack",
            "type": "Element",
            "min_occurs": 1,
            "max_occurs": 16,
        },
    )
    mono_track: Optional[MonoTrack] = field(
        default=None,
        metadata={
            "name": "seTrack",
            "type": "Element",
            "required": True,
        },
    )
    stereo_track: Optional[StereoTrack] = field(
        default=None,
        metadata={
            "name": "karaokeTrack",
            "type": "Element",
            "required": True,
        },
    )
    aux: list[Aux] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
