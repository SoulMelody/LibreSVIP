from enum import Enum
from typing import Optional

from xsdata_pydantic.fields import field

from libresvip.model.base import BaseModel

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


class Aux(BaseModel):
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


class Dyn(BaseModel):
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


class Pch(BaseModel):
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


class Phnm(BaseModel):
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


class SeqAttr(BaseModel):
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
    seq_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "id",
            "type": "Attribute",
            "required": True,
        },
    )

    class Elem(BaseModel):
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


class Singer(BaseModel):
    class Meta:
        name = "singer"
        namespace = VSQ3_NS

    pos_tick: Optional[int] = field(
        default=0,
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


class StylePlugin(BaseModel):
    class Meta:
        name = "stylePlugin"
        namespace = VSQ3_NS

    style_plugin_id: Optional[str] = field(
        default="ACA9C502-A04B-42b5-B2EB-5CEA36D16FCE",
        metadata={
            "name": "stylePluginID",
            "type": "Element",
            "required": True,
            "length": 36,
        },
    )
    style_plugin_name: Optional[str] = field(
        default="VOCALOID2 Compatible Style",
        metadata={
            "name": "stylePluginName",
            "type": "Element",
            "required": True,
        },
    )
    version: Optional[str] = field(
        default="3.0.0.1",
        metadata={
            "type": "Element",
            "required": True,
        },
    )


class Tempo(BaseModel):
    class Meta:
        name = "tempo"
        namespace = VSQ3_NS

    pos_tick: int = field(
        metadata={
            "name": "posTick",
            "type": "Element",
            "required": True,
        },
    )
    bpm: int = field(
        metadata={
            "type": "Element",
            "required": True,
        },
    )


class TimeSig(BaseModel):
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


class TypeParamAttr(BaseModel):
    class Meta:
        name = "typeParamAttr"

    value: Optional[int] = field(
        default=None,
        metadata={
            "required": True,
        },
    )
    type_param_attr_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "id",
            "type": "Attribute",
            "required": True,
        },
    )


class TypePhonemes(BaseModel):
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


class VVoiceParam(BaseModel):
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


class Voice(BaseModel):
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


class MCtrl(BaseModel):
    class Meta:
        name = "mCtrl"
        namespace = VSQ3_NS

    pos_tick: int = field(
        metadata={
            "name": "posTick",
            "type": "Element",
            "required": True,
        },
    )
    attr: TypeParamAttr = field(
        default_factory=TypeParamAttr,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


class MasterTrack(BaseModel):
    class Meta:
        name = "masterTrack"
        namespace = VSQ3_NS

    seq_name: Optional[str] = field(
        default="Untitled0",
        metadata={
            "name": "seqName",
            "type": "Element",
            "required": True,
        },
    )
    comment: Optional[str] = field(
        default="New VSQ File",
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    resolution: Optional[int] = field(
        default=480,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    pre_measure: int = field(
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


class NoteStyle(BaseModel):
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


class PCtrl(BaseModel):
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


class PartStyle(BaseModel):
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


class PhraseStyle(BaseModel):
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


class SCtrl(BaseModel):
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


class VVoice(BaseModel):
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


class VstPlugin(BaseModel):
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

    class VstParamVal(BaseModel):
        val: list[int] = field(
            default_factory=list,
            metadata={
                "type": "Element",
            },
        )


class VstPluginSr(BaseModel):
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

    class VstParamVal(BaseModel):
        val: list[int] = field(
            default_factory=list,
            metadata={
                "type": "Element",
            },
        )


class WavPart(BaseModel):
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


class StereoTrack(BaseModel):
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


class StereoUnit(BaseModel):
    class Meta:
        name = "karaokeUnit"
        namespace = VSQ3_NS

    in_gain: Optional[int] = field(
        default=0,
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
        default=0,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 1,
        },
    )
    solo: Optional[int] = field(
        default=0,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 1,
        },
    )
    vol: Optional[int] = field(
        default=0,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


class MasterUnit(BaseModel):
    class Meta:
        name = "masterUnit"
        namespace = VSQ3_NS

    out_dev: Optional[int] = field(
        default=0,
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
        default=0,
        metadata={
            "name": "retLevel",
            "type": "Element",
            "required": True,
        },
    )
    vol: Optional[int] = field(
        default=0,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


class Note(BaseModel):
    class Meta:
        name = "note"
        namespace = VSQ3_NS

    pos_tick: int = field(
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
        default=64,
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
    note_style: NoteStyle = field(
        default_factory=NoteStyle,
        metadata={
            "name": "noteStyle",
            "type": "Element",
        },
    )


class ProsodyPart(BaseModel):
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


class MonoTrack(BaseModel):
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


class MonoUnit(BaseModel):
    class Meta:
        name = "seUnit"
        namespace = VSQ3_NS

    in_gain: Optional[int] = field(
        default=0,
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
        default=-898,
        metadata={
            "name": "sendLevel",
            "type": "Element",
            "required": True,
        },
    )
    send_enable: Optional[int] = field(
        default=0,
        metadata={
            "name": "sendEnable",
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 1,
        },
    )
    mute: Optional[int] = field(
        default=0,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 1,
        },
    )
    solo: Optional[int] = field(
        default=0,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 1,
        },
    )
    pan: Optional[int] = field(
        default=64,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    vol: Optional[int] = field(
        default=0,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


class VVoiceTable(BaseModel):
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


class VsUnit(BaseModel):
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
        default=0,
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
        default=-898,
        metadata={
            "name": "sendLevel",
            "type": "Element",
            "required": True,
        },
    )
    send_enable: Optional[int] = field(
        default=0,
        metadata={
            "name": "sendEnable",
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 1,
        },
    )
    mute: Optional[int] = field(
        default=0,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 1,
        },
    )
    solo: Optional[int] = field(
        default=0,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 1,
        },
    )
    pan: Optional[int] = field(
        default=64,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    vol: Optional[int] = field(
        default=0,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


class Mixer(BaseModel):
    class Meta:
        name = "mixer"
        namespace = VSQ3_NS

    master_unit: Optional[MasterUnit] = field(
        default_factory=MasterUnit,
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
    mono_unit: MonoUnit = field(
        default_factory=MonoUnit,
        metadata={
            "name": "seUnit",
            "type": "Element",
            "required": True,
        },
    )
    stereo_unit: StereoUnit = field(
        default_factory=StereoUnit,
        metadata={
            "name": "karaokeUnit",
            "type": "Element",
            "required": True,
        },
    )


class MusicalPart(BaseModel):
    class Meta:
        name = "musicalPart"
        namespace = VSQ3_NS

    pos_tick: int = field(
        metadata={
            "name": "posTick",
            "type": "Element",
            "required": True,
        },
    )
    play_time: int = field(
        metadata={
            "name": "playTime",
            "type": "Element",
            "required": True,
        },
    )
    part_name: Optional[str] = field(
        default="New Part",
        metadata={
            "name": "partName",
            "type": "Element",
            "required": True,
        },
    )
    comment: Optional[str] = field(
        default="New Musical Part",
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    style_plugin: Optional[StylePlugin] = field(
        default_factory=StylePlugin,
        metadata={
            "name": "stylePlugin",
            "type": "Element",
            "required": True,
        },
    )
    part_style: PartStyle = field(
        default_factory=PartStyle,
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


class VsTrack(BaseModel):
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
        default="Track",
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


class Vsq3(BaseModel):
    class Meta:
        name = "vsq3"
        namespace = VSQ3_NS

    vender: Optional[str] = field(
        default="Yamaha Corporation",
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    version: Optional[str] = field(
        default="3.0.0.0",
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    v_voice_table: VVoiceTable = field(
        default_factory=VVoiceTable,
        metadata={
            "name": "vVoiceTable",
            "type": "Element",
            "required": True,
        },
    )
    mixer: Mixer = field(
        default_factory=Mixer,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    master_track: MasterTrack = field(
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
        default_factory=MonoTrack,
        metadata={
            "name": "seTrack",
            "type": "Element",
            "required": True,
        },
    )
    stereo_track: Optional[StereoTrack] = field(
        default_factory=StereoTrack,
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
