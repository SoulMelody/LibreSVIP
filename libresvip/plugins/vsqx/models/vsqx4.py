from dataclasses import field
from enum import Enum
from typing import List, Optional

from pydantic.dataclasses import dataclass

VSQ4_NS = "http://www.yamaha.co.jp/vocaloid/schema/vsq4/"


@dataclass
class Aux:
    class Meta:
        name = "aux"
        namespace = VSQ4_NS

    id: Optional[str] = field(
        default=None,
        metadata={
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
class SPlug:
    class Meta:
        name = "sPlug"
        namespace = VSQ4_NS

    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
            "length": 36,
        },
    )
    name: Optional[str] = field(
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


@dataclass
class Seq:
    class Meta:
        name = "seq"
        namespace = VSQ4_NS

    cc: List["Seq.Cc"] = field(
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
    class Cc:
        p: Optional[int] = field(
            default=None,
            metadata={
                "type": "Element",
                "required": True,
            },
        )
        v: Optional[int] = field(
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
        namespace = VSQ4_NS

    t: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    bs: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 127,
        },
    )
    pc: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 127,
        },
    )


@dataclass
class Tempo:
    class Meta:
        name = "tempo"
        namespace = VSQ4_NS

    t: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    v: Optional[int] = field(
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
        namespace = VSQ4_NS

    m: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    nu: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    de: Optional[int] = field(
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
class VPrm:
    class Meta:
        name = "vPrm"
        namespace = VSQ4_NS

    bre: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": -127,
            "max_inclusive": 127,
        },
    )
    bri: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": -127,
            "max_inclusive": 127,
        },
    )
    cle: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": -127,
            "max_inclusive": 127,
        },
    )
    gen: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": -127,
            "max_inclusive": 127,
        },
    )
    ope: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": -127,
            "max_inclusive": 127,
        },
    )


@dataclass
class VPrm2:
    class Meta:
        name = "vPrm2"
        namespace = VSQ4_NS

    bre: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": -127,
            "max_inclusive": 127,
        },
    )
    bri: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": -127,
            "max_inclusive": 127,
        },
    )
    cle: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": -127,
            "max_inclusive": 127,
        },
    )
    gen: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": -127,
            "max_inclusive": 127,
        },
    )
    ope: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": -127,
            "max_inclusive": 127,
        },
    )
    vol: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": -127,
            "max_inclusive": 127,
        },
    )


@dataclass
class Cc:
    class Meta:
        name = "cc"
        namespace = VSQ4_NS

    t: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    v: Optional[TypeParamAttr] = field(
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
        namespace = VSQ4_NS

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
        default=None,
        metadata={
            "name": "preMeasure",
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 127,
        },
    )
    time_sig: List[TimeSig] = field(
        default_factory=list,
        metadata={
            "name": "timeSig",
            "type": "Element",
            "min_occurs": 1,
        },
    )
    tempo: List[Tempo] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )


@dataclass
class NStyle:
    class Meta:
        name = "nStyle"
        namespace = VSQ4_NS

    v: List[TypeParamAttr] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    seq: List[Seq] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )


@dataclass
class PStyle:
    class Meta:
        name = "pStyle"
        namespace = VSQ4_NS

    v: List[TypeParamAttr] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )


@dataclass
class Plug:
    class Meta:
        name = "plug"
        namespace = VSQ4_NS

    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    sdk_ver: Optional[TypeVstSdkversion] = field(
        default=None,
        metadata={
            "name": "sdkVer",
            "type": "Element",
            "required": True,
        },
    )
    n_prm: Optional[int] = field(
        default=None,
        metadata={
            "name": "nPrm",
            "type": "Element",
            "required": True,
        },
    )
    v_prm: Optional["Plug.VPrm"] = field(
        default=None,
        metadata={
            "name": "vPrm",
            "type": "Element",
        },
    )
    preset_no: Optional[int] = field(
        default=None,
        metadata={
            "name": "presetNo",
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
    class VPrm:
        v: List[int] = field(
            default_factory=list,
            metadata={
                "type": "Element",
            },
        )


@dataclass
class PlugSr:
    class Meta:
        name = "plugSR"
        namespace = VSQ4_NS

    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    sdk_ver: Optional[TypeVstSdkversion] = field(
        default=None,
        metadata={
            "name": "sdkVer",
            "type": "Element",
            "required": True,
        },
    )
    n_prm: Optional[int] = field(
        default=None,
        metadata={
            "name": "nPrm",
            "type": "Element",
            "required": True,
        },
    )
    v_prm: Optional["PlugSr.VPrm"] = field(
        default=None,
        metadata={
            "name": "vPrm",
            "type": "Element",
        },
    )
    preset_no: Optional[int] = field(
        default=None,
        metadata={
            "name": "presetNo",
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
    class VPrm:
        v: List[int] = field(
            default_factory=list,
            metadata={
                "type": "Element",
            },
        )


@dataclass
class VVoice:
    class Meta:
        name = "vVoice"
        namespace = VSQ4_NS

    bs: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 127,
        },
    )
    pc: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 127,
        },
    )
    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
            "length": 16,
        },
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    v_prm: Optional[VPrm] = field(
        default=None,
        metadata={
            "name": "vPrm",
            "type": "Element",
            "required": True,
        },
    )
    id2: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "length": 16,
        },
    )
    v_prm2: Optional[VPrm2] = field(
        default=None,
        metadata={
            "name": "vPrm2",
            "type": "Element",
        },
    )


@dataclass
class WavPart:
    class Meta:
        name = "wavPart"
        namespace = VSQ4_NS

    t: Optional[int] = field(
        default=None,
        metadata={
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
    name: Optional[str] = field(
        default=None,
        metadata={
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
    fs: Optional[TypeSamplerate] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    rs: Optional[TypeResolution] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    n_ch: Optional[int] = field(
        default=None,
        metadata={
            "name": "nCh",
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
class MasterUnit:
    class Meta:
        name = "masterUnit"
        namespace = VSQ4_NS

    o_dev: Optional[int] = field(
        default=None,
        metadata={
            "name": "oDev",
            "type": "Element",
            "required": True,
        },
    )
    plug: List[Plug] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "max_occurs": 2,
        },
    )
    plug_sr: Optional[PlugSr] = field(
        default=None,
        metadata={
            "name": "plugSR",
            "type": "Element",
        },
    )
    r_lvl: Optional[int] = field(
        default=None,
        metadata={
            "name": "rLvl",
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
class MonoTrack:
    class Meta:
        name = "monoTrack"
        namespace = VSQ4_NS

    wav_part: List[WavPart] = field(
        default_factory=list,
        metadata={
            "name": "wavPart",
            "type": "Element",
        },
    )


@dataclass
class MonoUnit:
    class Meta:
        name = "monoUnit"
        namespace = VSQ4_NS

    i_gin: Optional[int] = field(
        default=None,
        metadata={
            "name": "iGin",
            "type": "Element",
            "required": True,
        },
    )
    plug: List[Plug] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "max_occurs": 2,
        },
    )
    s_lvl: Optional[int] = field(
        default=None,
        metadata={
            "name": "sLvl",
            "type": "Element",
            "required": True,
        },
    )
    s_enable: Optional[int] = field(
        default=None,
        metadata={
            "name": "sEnable",
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 1,
        },
    )
    m: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 1,
        },
    )
    s: Optional[int] = field(
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
class Note:
    class Meta:
        name = "note"
        namespace = VSQ4_NS

    t: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    dur: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    n: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 127,
        },
    )
    v: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 127,
        },
    )
    y: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    p: Optional[TypePhonemes] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    n_style: Optional[NStyle] = field(
        default=None,
        metadata={
            "name": "nStyle",
            "type": "Element",
        },
    )


@dataclass
class StTrack:
    class Meta:
        name = "stTrack"
        namespace = VSQ4_NS

    wav_part: List[WavPart] = field(
        default_factory=list,
        metadata={
            "name": "wavPart",
            "type": "Element",
        },
    )


@dataclass
class StUnit:
    class Meta:
        name = "stUnit"
        namespace = VSQ4_NS

    i_gin: Optional[int] = field(
        default=None,
        metadata={
            "name": "iGin",
            "type": "Element",
            "required": True,
        },
    )
    plug: List[Plug] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "max_occurs": 2,
        },
    )
    m: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 1,
        },
    )
    s: Optional[int] = field(
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
class VVoiceTable:
    class Meta:
        name = "vVoiceTable"
        namespace = VSQ4_NS

    v_voice: List[VVoice] = field(
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
        namespace = VSQ4_NS

    t_no: Optional[int] = field(
        default=None,
        metadata={
            "name": "tNo",
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 127,
        },
    )
    i_gin: Optional[int] = field(
        default=None,
        metadata={
            "name": "iGin",
            "type": "Element",
            "required": True,
        },
    )
    plug: List[Plug] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "max_occurs": 2,
        },
    )
    s_lvl: Optional[int] = field(
        default=None,
        metadata={
            "name": "sLvl",
            "type": "Element",
            "required": True,
        },
    )
    s_enable: Optional[int] = field(
        default=None,
        metadata={
            "name": "sEnable",
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 1,
        },
    )
    m: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 1,
        },
    )
    s: Optional[int] = field(
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
        namespace = VSQ4_NS

    master_unit: Optional[MasterUnit] = field(
        default=None,
        metadata={
            "name": "masterUnit",
            "type": "Element",
            "required": True,
        },
    )
    vs_unit: List[VsUnit] = field(
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
            "name": "monoUnit",
            "type": "Element",
            "required": True,
        },
    )
    st_unit: Optional[StUnit] = field(
        default=None,
        metadata={
            "name": "stUnit",
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class VsPart:
    class Meta:
        name = "vsPart"
        namespace = VSQ4_NS

    t: Optional[int] = field(
        default=None,
        metadata={
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
    name: Optional[str] = field(
        default=None,
        metadata={
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
    s_plug: Optional[SPlug] = field(
        default=None,
        metadata={
            "name": "sPlug",
            "type": "Element",
            "required": True,
        },
    )
    p_style: Optional[PStyle] = field(
        default=None,
        metadata={
            "name": "pStyle",
            "type": "Element",
        },
    )
    singer: List[Singer] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )
    cc: List[Cc] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    note: List[Note] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    plane: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "min_inclusive": 0,
            "max_inclusive": 1,
        },
    )


@dataclass
class VsTrack:
    class Meta:
        name = "vsTrack"
        namespace = VSQ4_NS

    t_no: Optional[int] = field(
        default=None,
        metadata={
            "name": "tNo",
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 127,
        },
    )
    name: Optional[str] = field(
        default=None,
        metadata={
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
    vs_part: List[VsPart] = field(
        default_factory=list,
        metadata={
            "name": "vsPart",
            "type": "Element",
        },
    )


@dataclass
class Vsq4:
    class Meta:
        name = "vsq4"
        namespace = VSQ4_NS

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
        default=None,
        metadata={
            "name": "vVoiceTable",
            "type": "Element",
            "required": True,
        },
    )
    mixer: Optional[Mixer] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    master_track: Optional[MasterTrack] = field(
        default=None,
        metadata={
            "name": "masterTrack",
            "type": "Element",
            "required": True,
        },
    )
    vs_track: List[VsTrack] = field(
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
            "name": "monoTrack",
            "type": "Element",
            "required": True,
        },
    )
    st_track: Optional[StTrack] = field(
        default=None,
        metadata={
            "name": "stTrack",
            "type": "Element",
            "required": True,
        },
    )
    aux: List[Aux] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
