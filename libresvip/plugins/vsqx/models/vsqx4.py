from enum import Enum
from typing import Optional

from xsdata_pydantic.fields import field

from libresvip.model.base import BaseModel

from .enums import VocaloidLanguage

VSQ4_NS = "http://www.yamaha.co.jp/vocaloid/schema/vsq4/"


class ParameterNames(Enum):
    DYN = "D"
    BRE = "B"
    BRI = "R"
    CLE = "C"
    GEN = "G"
    POR = "T"
    PBS = "S"
    PIT = "P"
    XSY = "X"
    GWL = "W"


class Aux(BaseModel):
    class Meta:
        name = "aux"
        namespace = VSQ4_NS

    aux_id: str | None = field(
        default=None,
        metadata={
            "name": "id",
            "type": "Element",
            "required": True,
        },
    )
    content: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


class StylePlugin(BaseModel):
    class Meta:
        name = "sPlug"
        namespace = VSQ4_NS

    style_plugin_id: str | None = field(
        default="ACA9C502-A04B-42b5-B2EB-5CEA36D16FCE",
        metadata={
            "name": "id",
            "type": "Element",
            "required": True,
            "length": 36,
        },
    )
    style_plugin_name: str | None = field(
        default="VOCALOID2 Compatible Style",
        metadata={
            "name": "name",
            "type": "Element",
            "required": True,
        },
    )
    version: str | None = field(
        default="3.0.0.1",
        metadata={
            "type": "Element",
            "required": True,
        },
    )


class SeqAttr(BaseModel):
    class Meta:
        name = "seq"
        namespace = VSQ4_NS

    elem: list["SeqAttr.Elem"] = field(
        default_factory=list,
        metadata={
            "name": "cc",
            "type": "Element",
            "min_occurs": 1,
        },
    )
    seq_id: str | None = field(
        default=None,
        metadata={
            "name": "id",
            "type": "Attribute",
            "required": True,
        },
    )

    class Elem(BaseModel):
        pos_nrm: int | None = field(
            default=None,
            metadata={
                "name": "p",
                "type": "Element",
                "required": True,
            },
        )
        elv: int | None = field(
            default=None,
            metadata={
                "name": "v",
                "type": "Element",
                "required": True,
            },
        )


class Singer(BaseModel):
    class Meta:
        name = "singer"
        namespace = VSQ4_NS

    pos_tick: int | None = field(
        default=0,
        metadata={
            "name": "t",
            "type": "Element",
            "required": True,
        },
    )
    v_bs: VocaloidLanguage | None = field(
        default=VocaloidLanguage.SIMPLIFIED_CHINESE,
        metadata={
            "name": "bs",
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 127,
        },
    )
    v_pc: int | None = field(
        default=0,
        metadata={
            "name": "pc",
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 127,
        },
    )


class Tempo(BaseModel):
    class Meta:
        name = "tempo"
        namespace = VSQ4_NS

    pos_tick: int = field(
        metadata={
            "name": "t",
            "type": "Element",
            "required": True,
        },
    )
    bpm: int = field(
        metadata={
            "name": "v",
            "type": "Element",
            "required": True,
        },
    )


class TimeSig(BaseModel):
    class Meta:
        name = "timeSig"
        namespace = VSQ4_NS

    pos_mes: int | None = field(
        default=None,
        metadata={
            "name": "m",
            "type": "Element",
            "required": True,
        },
    )
    nume: int | None = field(
        default=None,
        metadata={
            "name": "nu",
            "type": "Element",
            "required": True,
        },
    )
    denomi: int | None = field(
        default=None,
        metadata={
            "name": "de",
            "type": "Element",
            "required": True,
        },
    )


class TypeParamAttr(BaseModel):
    class Meta:
        name = "typeParamAttr"

    value: int | None = field(
        default=None,
        metadata={
            "required": True,
        },
    )
    type_param_attr_id: str | None = field(
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
    lock: int | None = field(
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
        name = "vPrm"
        namespace = VSQ4_NS

    bre: int | None = field(
        default=0,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": -127,
            "max_inclusive": 127,
        },
    )
    bri: int | None = field(
        default=0,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": -127,
            "max_inclusive": 127,
        },
    )
    cle: int | None = field(
        default=0,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": -127,
            "max_inclusive": 127,
        },
    )
    gen: int | None = field(
        default=0,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": -127,
            "max_inclusive": 127,
        },
    )
    ope: int | None = field(
        default=0,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": -127,
            "max_inclusive": 127,
        },
    )


class VPrm2(BaseModel):
    class Meta:
        name = "vPrm2"
        namespace = VSQ4_NS

    bre: int | None = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": -127,
            "max_inclusive": 127,
        },
    )
    bri: int | None = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": -127,
            "max_inclusive": 127,
        },
    )
    cle: int | None = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": -127,
            "max_inclusive": 127,
        },
    )
    gen: int | None = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": -127,
            "max_inclusive": 127,
        },
    )
    ope: int | None = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": -127,
            "max_inclusive": 127,
        },
    )
    vol: int | None = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": -127,
            "max_inclusive": 127,
        },
    )


class MCtrl(BaseModel):
    class Meta:
        name = "cc"
        namespace = VSQ4_NS

    pos_tick: int = field(
        metadata={
            "name": "t",
            "type": "Element",
            "required": True,
        },
    )
    attr: TypeParamAttr = field(
        default_factory=TypeParamAttr,
        metadata={
            "name": "v",
            "type": "Element",
            "required": True,
        },
    )


class MasterTrack(BaseModel):
    class Meta:
        name = "masterTrack"
        namespace = VSQ4_NS

    seq_name: str | None = field(
        default="Untitled0",
        metadata={
            "name": "seqName",
            "type": "Element",
            "required": True,
        },
    )
    comment: str | None = field(
        default="New VSQ File",
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    resolution: int | None = field(
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
        name = "nStyle"
        namespace = VSQ4_NS

    attr: list[TypeParamAttr] = field(
        default_factory=list,
        metadata={
            "name": "v",
            "type": "Element",
        },
    )
    seq_attr: list[SeqAttr] = field(
        default_factory=list,
        metadata={
            "name": "seq",
            "type": "Element",
        },
    )


class PartStyle(BaseModel):
    class Meta:
        name = "pStyle"
        namespace = VSQ4_NS

    attr: list[TypeParamAttr] = field(
        default_factory=list,
        metadata={
            "name": "v",
            "type": "Element",
            "min_occurs": 1,
        },
    )


class VstPlugin(BaseModel):
    class Meta:
        name = "plug"
        namespace = VSQ4_NS

    vst_plugin_id: str | None = field(
        default=None,
        metadata={
            "name": "id",
            "type": "Element",
            "required": True,
        },
    )
    vst_plugin_name: str | None = field(
        default=None,
        metadata={
            "name": "name",
            "type": "Element",
            "required": True,
        },
    )
    vst_sdkversion: TypeVstSdkversion | None = field(
        default=None,
        metadata={
            "name": "sdkVer",
            "type": "Element",
            "required": True,
        },
    )
    vst_param_num: int | None = field(
        default=None,
        metadata={
            "name": "nPrm",
            "type": "Element",
            "required": True,
        },
    )
    vst_param_val: Optional["VstPlugin.VstParamVal"] = field(
        default=None,
        metadata={
            "name": "vPrm",
            "type": "Element",
        },
    )
    vst_preset_no: int | None = field(
        default=None,
        metadata={
            "name": "presetNo",
            "type": "Element",
        },
    )
    enable: int | None = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 1,
        },
    )
    bypass: int | None = field(
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
                "name": "v",
                "type": "Element",
            },
        )


class VstPluginSr(BaseModel):
    class Meta:
        name = "plugSR"
        namespace = VSQ4_NS

    vst_plugin_id: str | None = field(
        default=None,
        metadata={
            "name": "id",
            "type": "Element",
            "required": True,
        },
    )
    vst_plugin_name: str | None = field(
        default=None,
        metadata={
            "name": "name",
            "type": "Element",
            "required": True,
        },
    )
    vst_sdkversion: TypeVstSdkversion | None = field(
        default=None,
        metadata={
            "name": "sdkVer",
            "type": "Element",
            "required": True,
        },
    )
    vst_param_num: int | None = field(
        default=None,
        metadata={
            "name": "nPrm",
            "type": "Element",
            "required": True,
        },
    )
    vst_param_val: Optional["VstPluginSr.VstParamVal"] = field(
        default=None,
        metadata={
            "name": "vPrm",
            "type": "Element",
        },
    )
    vst_preset_no: int | None = field(
        default=None,
        metadata={
            "name": "presetNo",
            "type": "Element",
        },
    )
    enable: int | None = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 1,
        },
    )
    bypass: int | None = field(
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
                "name": "v",
                "type": "Element",
            },
        )


class VVoice(BaseModel):
    class Meta:
        name = "vVoice"
        namespace = VSQ4_NS

    v_bs: VocaloidLanguage | None = field(
        default=VocaloidLanguage.SIMPLIFIED_CHINESE,
        metadata={
            "name": "bs",
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 127,
        },
    )
    v_pc: int | None = field(
        default=0,
        metadata={
            "name": "pc",
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 127,
        },
    )
    comp_id: str | None = field(
        default=None,
        metadata={
            "name": "id",
            "type": "Element",
            "required": True,
            "length": 16,
        },
    )
    v_voice_name: str | None = field(
        default=None,
        metadata={
            "name": "name",
            "type": "Element",
            "required": True,
        },
    )
    v_voice_param: VVoiceParam | None = field(
        default_factory=VVoiceParam,
        metadata={
            "name": "vPrm",
            "type": "Element",
            "required": True,
        },
    )
    id2: str | None = field(
        default=None,
        metadata={
            "type": "Element",
            "length": 16,
        },
    )
    v_prm2: VPrm2 | None = field(
        default=None,
        metadata={
            "name": "vPrm2",
            "type": "Element",
        },
    )


class WavPart(BaseModel):
    class Meta:
        name = "wavPart"
        namespace = VSQ4_NS

    pos_tick: int | None = field(
        default=None,
        metadata={
            "name": "t",
            "type": "Element",
            "required": True,
        },
    )
    play_time: int | None = field(
        default=None,
        metadata={
            "name": "playTime",
            "type": "Element",
            "required": True,
        },
    )
    part_name: str | None = field(
        default=None,
        metadata={
            "name": "name",
            "type": "Element",
            "required": True,
        },
    )
    comment: str | None = field(
        default="New Wav Part",
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    sample_rate: TypeSamplerate | None = field(
        default=None,
        metadata={
            "name": "fs",
            "type": "Element",
            "required": True,
        },
    )
    sample_reso: TypeResolution | None = field(
        default=None,
        metadata={
            "name": "rs",
            "type": "Element",
            "required": True,
        },
    )
    channels: int | None = field(
        default=None,
        metadata={
            "name": "nCh",
            "type": "Element",
            "required": True,
            "min_inclusive": 1,
            "max_inclusive": 2,
        },
    )
    file_path: str | None = field(
        default=None,
        metadata={
            "name": "filePath",
            "type": "Element",
            "required": True,
        },
    )


class MasterUnit(BaseModel):
    class Meta:
        name = "masterUnit"
        namespace = VSQ4_NS

    out_dev: int | None = field(
        default=0,
        metadata={
            "name": "oDev",
            "type": "Element",
            "required": True,
        },
    )
    vst_plugin: list[VstPlugin] = field(
        default_factory=list,
        metadata={
            "name": "plug",
            "type": "Element",
            "max_occurs": 2,
        },
    )
    vst_plugin_sr: VstPluginSr | None = field(
        default=None,
        metadata={
            "name": "plugSR",
            "type": "Element",
        },
    )
    ret_level: int | None = field(
        default=0,
        metadata={
            "name": "rLvl",
            "type": "Element",
            "required": True,
        },
    )
    vol: int | None = field(
        default=0,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


class MonoTrack(BaseModel):
    class Meta:
        name = "monoTrack"
        namespace = VSQ4_NS

    wav_part: list[WavPart] = field(
        default_factory=list,
        metadata={
            "name": "wavPart",
            "type": "Element",
        },
    )


class MonoUnit(BaseModel):
    class Meta:
        name = "monoUnit"
        namespace = VSQ4_NS

    in_gain: int | None = field(
        default=0,
        metadata={
            "name": "iGin",
            "type": "Element",
            "required": True,
        },
    )
    vst_plugin: list[VstPlugin] = field(
        default_factory=list,
        metadata={
            "name": "plug",
            "type": "Element",
            "max_occurs": 2,
        },
    )
    send_level: int | None = field(
        default=-898,
        metadata={
            "name": "sLvl",
            "type": "Element",
            "required": True,
        },
    )
    send_enable: int | None = field(
        default=0,
        metadata={
            "name": "sEnable",
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 1,
        },
    )
    mute: int | None = field(
        default=0,
        metadata={
            "name": "m",
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 1,
        },
    )
    solo: int | None = field(
        default=0,
        metadata={
            "name": "s",
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 1,
        },
    )
    pan: int | None = field(
        default=64,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    vol: int | None = field(
        default=0,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


class Note(BaseModel):
    class Meta:
        name = "note"
        namespace = VSQ4_NS

    pos_tick: int = field(
        metadata={
            "name": "t",
            "type": "Element",
            "required": True,
        },
    )
    dur_tick: int = field(
        metadata={
            "name": "dur",
            "type": "Element",
            "required": True,
        },
    )
    note_num: int | None = field(
        default=None,
        metadata={
            "name": "n",
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 127,
        },
    )
    velocity: int | None = field(
        default=64,
        metadata={
            "name": "v",
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 127,
        },
    )
    lyric: str = field(
        metadata={
            "name": "y",
            "type": "Element",
            "required": True,
        },
    )
    phnms: TypePhonemes | None = field(
        default=None,
        metadata={
            "name": "p",
            "type": "Element",
            "required": True,
        },
    )
    note_style: NoteStyle = field(
        default_factory=NoteStyle,
        metadata={
            "name": "nStyle",
            "type": "Element",
        },
    )


class StereoTrack(BaseModel):
    class Meta:
        name = "stTrack"
        namespace = VSQ4_NS

    wav_part: list[WavPart] = field(
        default_factory=list,
        metadata={
            "name": "wavPart",
            "type": "Element",
        },
    )


class StereoUnit(BaseModel):
    class Meta:
        name = "stUnit"
        namespace = VSQ4_NS

    in_gain: int | None = field(
        default=0,
        metadata={
            "name": "iGin",
            "type": "Element",
            "required": True,
        },
    )
    vst_plugin: list[VstPlugin] = field(
        default_factory=list,
        metadata={
            "name": "plug",
            "type": "Element",
            "max_occurs": 2,
        },
    )
    mute: int | None = field(
        default=0,
        metadata={
            "name": "m",
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 1,
        },
    )
    solo: int | None = field(
        default=0,
        metadata={
            "name": "s",
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 1,
        },
    )
    vol: int | None = field(
        default=0,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


class VVoiceTable(BaseModel):
    class Meta:
        name = "vVoiceTable"
        namespace = VSQ4_NS

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
        namespace = VSQ4_NS

    vs_track_no: int | None = field(
        default=None,
        metadata={
            "name": "tNo",
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 127,
        },
    )
    in_gain: int | None = field(
        default=0,
        metadata={
            "name": "iGin",
            "type": "Element",
            "required": True,
        },
    )
    vst_plugin: list[VstPlugin] = field(
        default_factory=list,
        metadata={
            "name": "plug",
            "type": "Element",
            "max_occurs": 2,
        },
    )
    send_level: int | None = field(
        default=-898,
        metadata={
            "name": "sLvl",
            "type": "Element",
            "required": True,
        },
    )
    send_enable: int | None = field(
        default=0,
        metadata={
            "name": "sEnable",
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 1,
        },
    )
    mute: int | None = field(
        default=0,
        metadata={
            "name": "m",
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 1,
        },
    )
    solo: int | None = field(
        default=0,
        metadata={
            "name": "s",
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 1,
        },
    )
    pan: int | None = field(
        default=64,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    vol: int | None = field(
        default=0,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


class Mixer(BaseModel):
    class Meta:
        name = "mixer"
        namespace = VSQ4_NS

    master_unit: MasterUnit | None = field(
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
            "name": "monoUnit",
            "type": "Element",
            "required": True,
        },
    )
    stereo_unit: StereoUnit = field(
        default_factory=StereoUnit,
        metadata={
            "name": "stUnit",
            "type": "Element",
            "required": True,
        },
    )


class MusicalPart(BaseModel):
    class Meta:
        name = "vsPart"
        namespace = VSQ4_NS

    pos_tick: int = field(
        metadata={
            "name": "t",
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
    part_name: str | None = field(
        default="New Part",
        metadata={
            "name": "name",
            "type": "Element",
            "required": True,
        },
    )
    comment: str | None = field(
        default="New Musical Part",
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    style_plugin: StylePlugin | None = field(
        default_factory=StylePlugin,
        metadata={
            "name": "sPlug",
            "type": "Element",
            "required": True,
        },
    )
    part_style: PartStyle = field(
        default_factory=PartStyle,
        metadata={
            "name": "pStyle",
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
            "name": "cc",
            "type": "Element",
        },
    )
    note: list[Note] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    plane: int | None = field(
        default=None,
        metadata={
            "type": "Element",
            "min_inclusive": 0,
            "max_inclusive": 1,
        },
    )


class VsTrack(BaseModel):
    class Meta:
        name = "vsTrack"
        namespace = VSQ4_NS

    vs_track_no: int | None = field(
        default=None,
        metadata={
            "name": "tNo",
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 127,
        },
    )
    track_name: str | None = field(
        default=None,
        metadata={
            "name": "name",
            "type": "Element",
            "required": True,
        },
    )
    comment: str | None = field(
        default="Track",
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    musical_part: list[MusicalPart] = field(
        default_factory=list,
        metadata={
            "name": "vsPart",
            "type": "Element",
        },
    )


class Vsq4(BaseModel):
    class Meta:
        name = "vsq4"
        namespace = VSQ4_NS

    vender: str | None = field(
        default="Yamaha Corporation",
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    version: str | None = field(
        default="4.0.0.3",
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
    mono_track: MonoTrack | None = field(
        default_factory=MonoTrack,
        metadata={
            "name": "monoTrack",
            "type": "Element",
            "required": True,
        },
    )
    stereo_track: StereoTrack | None = field(
        default_factory=StereoTrack,
        metadata={
            "name": "stTrack",
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
