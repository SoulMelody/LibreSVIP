import dataclasses
from typing import Union

from construct import (
    Byte,
    Bytes,
    BytesInteger,
    Const,
    IfThenElse,
    PascalString,
    PrefixedArray,
    this,
)
from construct_typed import DataclassMixin, DataclassStruct, EnumBase, TEnum, csfield

Int32ul = BytesInteger(4, swapped=True)
Int32sl = BytesInteger(4, swapped=True, signed=True)


@dataclasses.dataclass
class DvBytes(DataclassMixin):
    length: int = csfield(Int32ul)
    value: bytes = csfield(Bytes(lambda this: this.length))


DvStr = PascalString(Int32ul, "utf-8")


@dataclasses.dataclass
class DvPoint(DataclassMixin):
    x: int = csfield(Int32ul)
    y: int = csfield(Int32ul)


@dataclasses.dataclass
class DvTempo(DataclassMixin):
    position: int = csfield(Int32ul)
    bpm: int = csfield(Int32ul)


@dataclasses.dataclass
class DvTimeSignature(DataclassMixin):
    measure_position: int = csfield(Int32sl)
    numerator: int = csfield(Int32ul)
    denominator: int = csfield(Int32ul)


@dataclasses.dataclass
class DvNoteParameter(DataclassMixin):
    param_size: int = csfield(Int32ul)
    amplitude_size: int = csfield(Int32ul)
    amplitude_points: list[DvPoint] = csfield(
        PrefixedArray(Int32ul, DataclassStruct(DvPoint))
    )
    frequency_size: int = csfield(Int32ul)
    frequency_points: list[DvPoint] = csfield(
        PrefixedArray(Int32ul, DataclassStruct(DvPoint))
    )
    vibrato_size: int = csfield(Int32ul)
    vibrato_points: list[DvPoint] = csfield(
        PrefixedArray(Int32ul, DataclassStruct(DvPoint))
    )


@dataclasses.dataclass
class DvNote(DataclassMixin):
    start: int = csfield(Int32ul)
    length: int = csfield(Int32ul)
    key: int = csfield(Int32ul)
    vibrato: int = csfield(Int32ul)
    phoneme: DvStr = csfield(DvStr)
    word: DvStr = csfield(DvStr)
    padding_1: int = csfield(Byte)
    note_vibrato_data: DvNoteParameter = csfield(DataclassStruct(DvNoteParameter))
    unknown: bytes = csfield(
        Const(
            b"\x04\x10\x00\x00\x00\x04\x00\x00\x07\xefR\xb4y\xca\xc6\xbb\xd0\xd8F\xbcI,\x95\xbc\x98\xf1\xc6\xbc\xac\xbb\xf8\xbc\xeeD\x15\xbd\x81-.\xbd\xbb\x17G\xbd\x07\x03`\xbd\x15\xefx\xbd\xc9\xed\x88\xbd\x16d\x95\xbdG\xda\xa1\xbd6P\xae\xbd\xb8\xc5\xba\xbd\xa6:\xc7\xbd\xd6\xae\xd3\xbd#\"\xe0\xbdb\x94\xec\xbdn\x05\xf9\xbd\x8e\xba\x02\xbe\x95\xf1\x08\xbe\xd5'\x0f\xbe-]\x15\xbe\x88\x91\x1b\xbe\xd4\xc4!\xbe\xfd\xf6'\xbe\xef'.\xbe\x98W4\xbe\xe6\x85:\xbe\xc3\xb2@\xbe\x1f\xdeF\xbe\xe6\x07M\xbe\x050S\xbeZVY\xbe\xf3z_\xbe\xad\x9de\xbes\xbek\xbe7\xddq\xbe\xe6\xf9w\xbej\x14~\xbe[\x16\x82\xbe[!\x85\xbe++\x88\xbe\xc53\x8b\xbe\x1d;\x8e\xbe+A\x91\xbe\xe8E\x94\xbeII\x97\xbe?K\x9a\xbe\xd0K\x9d\xbe\xedJ\xa0\xbe\x8cH\xa3\xbe\xa4D\xa6\xbe/?\xa9\xbe\"8\xac\xbew/\xaf\xbe$%\xb2\xbe \x19\xb5\xbee\x0b\xb8\xbe\xe9\xfb\xba\xbe\x9d\xea\xbd\xbe\x89\xd7\xc0\xbe\x9a\xc2\xc3\xbe\xcc\xab\xc6\xbe\x15\x93\xc9\xbelx\xcc\xbe\xcb[\xcf\xbe)=\xd2\xbe\x7f\x1c\xd5\xbe\xc4\xf9\xd7\xbe\xf1\xd4\xda\xbe\xff\xad\xdd\xbe\xe5\x84\xe0\xbe\x9bY\xe3\xbe\x1d,\xe6\xbeW\xfc\xe8\xbeU\xca\xeb\xbe\x04\x96\xee\xbe^_\xf1\xbe\\&\xf4\xbe\xf9\xea\xf6\xbe)\xad\xf9\xbe\xe7l\xfc\xbe,*\xff\xbez\xf2\x00\xbf\x98N\x02\xbfp\xa9\x03\xbf\xf9\x02\x05\xbf8[\x06\xbf%\xb2\x07\xbf\xbd\x07\t\xbf\xfc[\n\xbf\xde\xae\x0b\xbfb\x00\r\xbf\x83P\x0e\xbf=\x9f\x0f\xbf\x8e\xec\x10\xbfr8\x12\xbf\xe6\x82\x13\xbf\xe6\xcb\x14\xbfo\x13\x16\xbf\x80Y\x17\xbf\x12\x9e\x18\xbf$\xe1\x19\xbf\xb0\"\x1b\xbf\xb8b\x1c\xbf7\xa1\x1d\xbf(\xde\x1e\xbf\x8a\x19 \xbfXS!\xbf\x91\x8b\"\xbf0\xc2#\xbf4\xf7$\xbf\x98*&\xbfX\\'\xbfu\x8c(\xbf\xea\xba)\xbf\xb4\xe7*\xbf\xd1\x12,\xbf><-\xbf\xf7c.\xbf\xfa\x89/\xbfD\xae0\xbf\xd3\xd01\xbf\xa3\xf12\xbf\xb1\x104\xbf\xfc-5\xbf\x80I6\xbf;c7\xbf+{8\xbfK\x919\xbf\x9a\xa5:\xbf\x13\xb8;\xbf\xb9\xc8<\xbf\x85\xd7=\xbfv\xe4>\xbf\x8a\xef?\xbf\xbd\xf8@\xbf\r\x00B\xbfx\x05C\xbf\xfc\x08D\xbf\x95\nE\xbf?\nF\xbf\xfe\x07G\xbf\xcc\x03H\xbf\xa5\xfdH\xbf\x89\xf5I\xbfu\xebJ\xbfg\xdfK\xbf^\xd1L\xbfU\xc1M\xbfK\xafN\xbf>\x9bO\xbf,\x85P\xbf\x12mQ\xbf\xefRR\xbf\xc26S\xbf\x87\x18T\xbf<\xf8T\xbf\xdd\xd5U\xbfl\xb1V\xbf\xe7\x8aW\xbfKbX\xbf\x947Y\xbf\xc2\nZ\xbf\xd3\xdbZ\xbf\xc5\xaa[\xbf\x95w\\\xbfBB]\xbf\xcc\n^\xbf/\xd1^\xbfj\x95_\xbf{W`\xbf`\x17a\xbf\x1a\xd5a\xbf\xa3\x90b\xbf\xfbIc\xbf!\x01d\xbf\x14\xb6d\xbf\xd0he\xbfV\x19f\xbf\xa3\xc7f\xbf\xb6sg\xbf\x8e\x1dh\xbf(\xc5h\xbf\x82ji\xbf\x9d\rj\xbfw\xaej\xbf\rMk\xbf`\xe9k\xbfl\x83l\xbf1\x1bm\xbf\xae\xb0m\xbf\xe2Cn\xbf\xca\xd4n\xbffco\xbf\xb4\xefo\xbf\xb4yp\xbfd\x01q\xbf\xc2\x86q\xbf\xcf\tr\xbf\x88\x8ar\xbf\xed\x08s\xbf\xfb\x84s\xbf\xb3\xfes\xbf\x13vt\xbf\x1a\xebt\xbf\xc8]u\xbf\x1b\xceu\xbf\x13<v\xbf\xac\xa7v\xbf\xe9\x10w\xbf\xc7ww\xbfE\xdcw\xbfc>x\xbf!\x9ex\xbf{\xfbx\xbfsVy\xbf\x08\xafy\xbf8\x05z\xbf\x03Yz\xbfj\xaaz\xbfh\xf9z\xbf\xffE{\xbf.\x90{\xbf\xf5\xd7{\xbfS\x1d|\xbfI`|\xbf\xd3\xa0|\xbf\xf2\xde|\xbf\xa5\x1a}\xbf\xedS}\xbf\xc9\x8a}\xbf8\xbf}\xbf9\xf1}\xbf\xcd ~\xbf\xf2M~\xbf\xa9x~\xbf\xf1\xa0~\xbf\xca\xc6~\xbf3\xea~\xbf,\x0b\x7f\xbf\xb6)\x7f\xbf\xceE\x7f\xbfv_\x7f\xbf\xaev\x7f\xbft\x8b\x7f\xbf\xc9\x9d\x7f\xbf\xac\xad\x7f\xbf\x1e\xbb\x7f\xbf\x1f\xc6\x7f\xbf\xad\xce\x7f\xbf\xca\xd4\x7f\xbfu\xd8\x7f\xbf\xae\xd9\x7f\xbfu\xd8\x7f\xbf\xca\xd4\x7f\xbf\xad\xce\x7f\xbf\x1f\xc6\x7f\xbf\x1e\xbb\x7f\xbf\xac\xad\x7f\xbf\xc9\x9d\x7f\xbft\x8b\x7f\xbf\xaev\x7f\xbfv_\x7f\xbf\xceE\x7f\xbf\xb6)\x7f\xbf,\x0b\x7f\xbf3\xea~\xbf\xca\xc6~\xbf\xf1\xa0~\xbf\xa9x~\xbf\xf2M~\xbf\xcd ~\xbf9\xf1}\xbf8\xbf}\xbf\xc9\x8a}\xbf\xeeS}\xbf\xa6\x1a}\xbf\xf2\xde|\xbf\xd3\xa0|\xbfI`|\xbfU\x1d|\xbf\xf7\xd7{\xbf0\x90{\xbf\x00F{\xbfh\xf9z\xbfj\xaaz\xbf\x04Yz\xbf9\x05z\xbf\t\xafy\xbfuVy\xbf|\xfbx\xbf!\x9ex\xbfd>x\xbfF\xdcw\xbf\xc8ww\xbf\xea\x10w\xbf\xad\xa7v\xbf\x13<v\xbf\x1c\xceu\xbf\xc9]u\xbf\x1c\xebt\xbf\x14vt\xbf\xb4\xfes\xbf\xfc\x84s\xbf\xed\x08s\xbf\x89\x8ar\xbf\xd0\tr\xbf\xc4\x86q\xbfe\x01q\xbf\xb5yp\xbf\xb5\xefo\xbfgco\xbf\xcb\xd4n\xbf\xe3Cn\xbf\xb0\xb0m\xbf3\x1bm\xbfm\x83l\xbfa\xe9k\xbf\x10Mk\xbfx\xaej\xbf\x9f\rj\xbf\x83ji\xbf)\xc5h\xbf\x8f\x1dh\xbf\xb8sg\xbf\xa6\xc7f\xbfW\x19f\xbf\xd2he\xbf\x15\xb6d\xbf#\x01d\xbf\xfcIc\xbf\xa4\x90b\xbf\x1b\xd5a\xbfc\x17a\xbf}W`\xbfl\x95_\xbf2\xd1^\xbf\xcf\n^\xbfFB]\xbf\x98w\\\xbf\xc7\xaa[\xbf\xd4\xdbZ\xbf\xc3\nZ\xbf\x957Y\xbfLbX\xbf\xe9\x8aW\xbfo\xb1V\xbf\xdf\xd5U\xbf<\xf8T\xbf\x88\x18T\xbf\xc46S\xbf\xf2RR\xbf\x14mQ\xbf.\x85P\xbf@\x9bO\xbfM\xafN\xbfV\xc1M\xbf_\xd1L\xbfj\xdfK\xbfx\xebJ\xbf\x8c\xf5I\xbf\xa8\xfdH\xbf\xce\x03H\xbf\x03\x08G\xbfD\nF\xbf\x97\nE\xbf\xfe\x08D\xbfz\x05C\xbf\x10\x00B\xbf\xbf\xf8@\xbf\x8b\xef?\xbfx\xe4>\xbf\x87\xd7=\xbf\xbb\xc8<\xbf\x16\xb8;\xbf\x9a\xa5:\xbfJ\x919\xbf-{8\xbf>c7\xbf\x82I6\xbf\xfe-5\xbf\xb4\x104\xbf\xa5\xf12\xbf\xd5\xd01\xbfF\xae0\xbf\xfc\x89/\xbf\xfac.\xbfA<-\xbf\xd4\x12,\xbf\xb8\xe7*\xbf\xec\xba)\xbfz\x8c(\xbf]\\'\xbf\x9b*&\xbf6\xf7$\xbf3\xc2#\xbf\x93\x8b\"\xbf[S!\xbf\x8d\x19 \xbf*\xde\x1e\xbf9\xa1\x1d\xbf\xbbb\x1c\xbf\xb3\"\x1b\xbf#\xe1\x19\xbf\x11\x9e\x18\xbf\x82Y\x17\xbfr\x13\x16\xbf\xe9\xcb\x14\xbf\xe8\x82\x13\xbft8\x12\xbf\x91\xec\x10\xbf@\x9f\x0f\xbf\x86P\x0e\xbfe\x00\r\xbf\xe1\xae\x0b\xbf\xff[\n\xbf\xc0\x07\t\xbf'\xb2\x07\xbf;[\x06\xbf\x00\x03\x05\xbfs\xa9\x03\xbf\x9bN\x02\xbf|\xf2\x00\xbf2*\xff\xbe\xedl\xfc\xbe/\xad\xf9\xbe\xff\xea\xf6\xbeb&\xf4\xbed_\xf1\xbe\n\x96\xee\xbe[\xca\xeb\xbe]\xfc\xe8\xbe#,\xe6\xbe\xa1Y\xe3\xbe\xeb\x84\xe0\xbe\x05\xae\xdd\xbe\xf7\xd4\xda\xbe\xca\xf9\xd7\xbe\x85\x1c\xd5\xbe/=\xd2\xbe\xd1[\xcf\xberx\xcc\xbe\x1b\x93\xc9\xbe\xd2\xab\xc6\xbe\xa1\xc2\xc3\xbe\x8e\xd7\xc0\xbe\xab\xea\xbd\xbe\xf0\xfb\xba\xbek\x0b\xb8\xbe'\x19\xb5\xbe*%\xb2\xbe}/\xaf\xbe)8\xac\xbe6?\xa9\xbe\xabD\xa6\xbe\x91H\xa3\xbe\xf3J\xa0\xbe\xd6K\x9d\xbeFK\x9a\xbeHI\x97\xbe\xeeE\x94\xbe2A\x91\xbe$;\x8e\xbe\xcb3\x8b\xbe2+\x88\xbeb!\x85\xbeb\x16\x82\xbey\x14~\xbe\xf3\xf9w\xbeD\xddq\xbe\x81\xbek\xbe\xb9\x9de\xbe\xffz_\xbehVY\xbe\x130S\xbe\xf4\x07M\xbe,\xdeF\xbe\xd1\xb2@\xbe\xf3\x85:\xbe\xa5W4\xbe\xfc'.\xbe\n\xf7'\xbe\xe1\xc4!\xbe\x95\x91\x1b\xbe:]\x15\xbe\xe3'\x0f\xbe\xa1\xf1\x08\xbe\x8c\xba\x02\xbe\x88\x05\xf9\xbd}\x94\xec\xbd>\"\xe0\xbd\xf1\xae\xd3\xbd\xc0:\xc7\xbd\xd2\xc5\xba\xbdPP\xae\xbdb\xda\xa1\xbd1d\x95\xbd\xe4\xed\x88\xbdK\xefx\xbd=\x03`\xbd\xef\x17G\xbd\xb6-.\xbd#E\x15\xbd\x16\xbc\xf8\xbc\x02\xf2\xc6\xbc\xb3,\x95\xbc\xa4\xd9F\xbc \xcc\xc6\xbb\x00\x00\x00\x00 \xcc\xc6;\xa4\xd9F<\xb3,\x95<\x02\xf2\xc6<\x16\xbc\xf8<#E\x15=\xb6-.=\xef\x17G==\x03`=K\xefx=\xe4\xed\x88=1d\x95=b\xda\xa1=PP\xae=\xd2\xc5\xba=\xc0:\xc7=\xf1\xae\xd3=>\"\xe0=}\x94\xec=\x88\x05\xf9=\x8c\xba\x02>\xa1\xf1\x08>\xe3'\x0f>:]\x15>\x95\x91\x1b>\xe1\xc4!>\n\xf7'>\xfc'.>\xa5W4>\xf3\x85:>\xd1\xb2@>,\xdeF>\xf4\x07M>\x130S>hVY>\xffz_>\xb9\x9de>\x81\xbek>D\xddq>\xf3\xf9w>y\x14~>b\x16\x82>b!\x85>2+\x88>\xcb3\x8b>$;\x8e>2A\x91>\xeeE\x94>HI\x97>FK\x9a>\xd6K\x9d>\xf3J\xa0>\x91H\xa3>\xabD\xa6>6?\xa9>)8\xac>}/\xaf>*%\xb2>'\x19\xb5>k\x0b\xb8>\xf0\xfb\xba>\xab\xea\xbd>\x8e\xd7\xc0>\xa1\xc2\xc3>\xd2\xab\xc6>\x1b\x93\xc9>rx\xcc>\xd1[\xcf>/=\xd2>\x85\x1c\xd5>\xca\xf9\xd7>\xf7\xd4\xda>\x05\xae\xdd>\xeb\x84\xe0>\xa1Y\xe3>#,\xe6>]\xfc\xe8>[\xca\xeb>\n\x96\xee>d_\xf1>b&\xf4>\xff\xea\xf6>/\xad\xf9>\xedl\xfc>2*\xff>|\xf2\x00?\x9bN\x02?s\xa9\x03?\x00\x03\x05?;[\x06?'\xb2\x07?\xc0\x07\t?\xff[\n?\xe1\xae\x0b?e\x00\r?\x86P\x0e?@\x9f\x0f?\x91\xec\x10?t8\x12?\xe8\x82\x13?\xe9\xcb\x14?r\x13\x16?\x82Y\x17?\x11\x9e\x18?#\xe1\x19?\xb3\"\x1b?\xbbb\x1c?9\xa1\x1d?*\xde\x1e?\x8d\x19 ?[S!?\x93\x8b\"?3\xc2#?6\xf7$?\x9b*&?]\\'?z\x8c(?\xec\xba)?\xb8\xe7*?\xd4\x12,?A<-?\xfac.?\xfc\x89/?F\xae0?\xd5\xd01?\xa5\xf12?\xb4\x104?\xfe-5?\x82I6?>c7?-{8?J\x919?\x9a\xa5:?\x16\xb8;?\xbb\xc8<?\x87\xd7=?x\xe4>?\x8b\xef??\xbf\xf8@?\x0c\x00B?x\x05C?\xfc\x08D?\x95\nE?B\nF?\x00\x08G?\xce\x03H?\xa8\xfdH?\x8c\xf5I?x\xebJ?j\xdfK?_\xd1L?V\xc1M?M\xafN?@\x9bO?.\x85P?\x14mQ?\xf2RR?\xc46S?\x88\x18T?=\xf8T?\xe1\xd5U?q\xb1V?\xeb\x8aW?NbX?\x977Y?\xc6\nZ?\xd3\xdbZ?\xc5\xaa[?\x95w\\?CB]?\xcd\n^?0\xd1^?l\x95_?}W`?c\x17a?\x1b\xd5a?\xa4\x90b?\xfcIc?#\x01d?\x15\xb6d?\xd2he?W\x19f?\xa6\xc7f?\xb8sg?\x8f\x1dh?)\xc5h?\x85ji?\xa0\rj?y\xaej?\x10Mk?b\xe9k?n\x83l?4\x1bm?\xae\xb0m?\xe2Cn?\xca\xd4n?fco?\xb4\xefo?\xb4yp?e\x01q?\xc4\x86q?\xd0\tr?\x89\x8ar?\xed\x08s?\xfc\x84s?\xb4\xfes?\x14vt?\x1c\xebt?\xc9]u?\x1c\xceu?\x13<v?\xad\xa7v?\xea\x10w?\xc8ww?F\xdcw?f>x?#\x9ex?~\xfbx?vVy?\n\xafy?;\x05z?\x03Yz?h\xaaz?g\xf9z?\x00F{?0\x90{?\xf7\xd7{?U\x1d|?I`|?\xd3\xa0|?\xf2\xde|?\xa6\x1a}?\xeeS}?\xc9\x8a}?8\xbf}?9\xf1}?\xcd ~?\xf2M~?\xa9x~?\xf1\xa0~?\xca\xc6~?3\xea~?,\x0b\x7f?\xb6)\x7f?\xceE\x7f?v_\x7f?\xaev\x7f?t\x8b\x7f?\xc9\x9d\x7f?\xac\xad\x7f?\x1e\xbb\x7f?\x1f\xc6\x7f?\xad\xce\x7f?\xca\xd4\x7f?u\xd8\x7f?\xae\xd9\x7f?u\xd8\x7f?\xca\xd4\x7f?\xad\xce\x7f?\x1f\xc6\x7f?\x1e\xbb\x7f?\xac\xad\x7f?\xc9\x9d\x7f?t\x8b\x7f?\xaev\x7f?v_\x7f?\xceE\x7f?\xb6)\x7f?,\x0b\x7f?2\xea~?\xc9\xc6~?\xf0\xa0~?\xa8x~?\xf1M~?\xcc ~?8\xf1}?8\xbf}?\xc9\x8a}?\xeeS}?\xa6\x1a}?\xf2\xde|?\xd3\xa0|?I`|?U\x1d|?\xf7\xd7{?0\x90{?\x00F{?h\xf9z?j\xaaz?\x03Yz?8\x05z?\x08\xafy?sVy?{\xfbx? \x9ex?c>x?E\xdcw?\xc7ww?\xe9\x10w?\xac\xa7v?\x12<v?\x1b\xceu?\xc7]u?\x19\xebt?\x14vt?\xb4\xfes?\xfc\x84s?\xed\x08s?\x89\x8ar?\xd0\tr?\xc4\x86q?e\x01q?\xb5yp?\xb5\xefo?fco?\xca\xd4n?\xe2Cn?\xae\xb0m?1\x1bm?l\x83l?`\xe9k?\rMk?w\xaej?\x9d\rj?\x81ji?&\xc5h?\x8c\x1dh?\xb5sg?\xa2\xc7f?U\x19f?\xcfhe?\x13\xb6d?#\x01d?\xfcIc?\xa4\x90b?\x1b\xd5a?c\x17a?}W`?l\x95_?1\xd1^?\xce\n^?CB]?\x95w\\?\xc5\xaa[?\xd3\xdbZ?\xc2\nZ?\x947Y?KbX?\xe7\x8aW?l\xb1V?\xdd\xd5U?9\xf8T?\x85\x18T?\xc06S?\xedRR?\x10mQ?)\x85P?;\x9bO?H\xafN?W\xc1M?`\xd1L?j\xdfK?x\xebJ?\x8c\xf5I?\xa8\xfdH?\xce\x03H?\x01\x08G?C\nF?\x95\nE?\xfc\x08D?x\x05C?\r\x00B?\xbd\xf8@?\x8a\xef??v\xe4>?\x85\xd7=?\xb9\xc8<?\x13\xb8;?\x98\xa5:?H\x919?'{8?8c7?~I6?\xfa-5?\xae\x104?\xa0\xf12?\xd0\xd01?G\xae0?\xfd\x89/?\xfbc.?A<-?\xd4\x12,?\xb8\xe7*?\xed\xba)?x\x8c(?Z\\'?\x98*&?4\xf7$?0\xc2#?\x91\x8b\"?XS!?\x8a\x19 ?(\xde\x1e?7\xa1\x1d?\xb8b\x1c?\xb0\"\x1b?!\xe1\x19?\x0f\x9e\x18?|Y\x17?l\x13\x16?\xe3\xcb\x14?\xe3\x82\x13?n8\x12?\x8a\xec\x10?:\x9f\x0f?\x86P\x0e?f\x00\r?\xe2\xae\x0b?\xff[\n?\xc0\x07\t?)\xb2\x07?<[\x06?\xfc\x02\x05?p\xa9\x03?\x98N\x02?z\xf2\x00?,*\xff>\xe7l\xfc>)\xad\xf9>\xf9\xea\xf6>\\&\xf4>^_\xf1>\x04\x96\xee>U\xca\xeb>W\xfc\xe8>\x15,\xe6>\x95Y\xe3>\xde\x84\xe0>\xf7\xad\xdd>\xea\xd4\xda>\xbd\xf9\xd7>x\x1c\xd5>0=\xd2>\xd2[\xcf>tx\xcc>\x1b\x93\xc9>\xd4\xab\xc6>\xa2\xc2\xc3>\x90\xd7\xc0>\xa5\xea\xbd>\xe9\xfb\xba>e\x0b\xb8> \x19\xb5>$%\xb2>w/\xaf>\"8\xac>/?\xa9>\xa4D\xa6>\x8cH\xa3>\xedJ\xa0>\xd0K\x9d>?K\x9a>AI\x97>\xdfE\x94>$A\x91>\x15;\x8e>\xbd3\x8b>$+\x88>S!\x85>T\x16\x82>{\x14~>\xf4\xf9w>H\xddq>\x83\xbek>\xbb\x9de>\x03{_>jVY>\x050S>\xe6\x07M>\x1f\xdeF>\xc3\xb2@>\xe6\x85:>\x98W4>\xef'.>\xfd\xf6'>\xd4\xc4!>\x88\x91\x1b>-]\x15>\xd5'\x0f>\x95\xf1\x08>~\xba\x02>N\x05\xf9=B\x94\xec=\x04\"\xe0=\xb6\xae\xd3=\x86:\xc7=\x99\xc5\xba=\x16P\xae=g\xda\xa1=5d\x95=\xe9\xed\x88=V\xefx=H\x03`=\xfa\x17G=\xc1-.=\xeeD\x15=\xac\xbb\xf8<\x98\xf1\xc6<I,\x95<\xd0\xd8F<y\xca\xc6;"
        )
    )
    unknown_phonemes: bytes = csfield(Bytes(18))
    ben_depth: int = csfield(Int32ul)
    ben_length: int = csfield(Int32ul)
    por_tail: int = csfield(Int32ul)
    por_head: int = csfield(Int32ul)
    timbre: int = csfield(Int32ul)
    cross_lyric: DvStr = csfield(DvStr)
    cross_timbre: int = csfield(Int32ul)


@dataclasses.dataclass
class DvSegment(DataclassMixin):
    start: int = csfield(Int32ul)
    length: int = csfield(Int32ul)
    name: DvStr = csfield(DvStr)
    singer_name: DvStr = csfield(DvStr)
    notes_size: int = csfield(Int32ul)
    notes: list[DvNote] = csfield(PrefixedArray(Int32ul, DataclassStruct(DvNote)))
    volume_length: int = csfield(Int32ul)
    volume_data: list[DvPoint] = csfield(
        PrefixedArray(Int32ul, DataclassStruct(DvPoint))
    )
    pitch_length: int = csfield(Int32ul)
    pitch_data: list[DvPoint] = csfield(
        PrefixedArray(Int32ul, DataclassStruct(DvPoint))
    )
    unknown_1: bytes = csfield(DataclassStruct(DvBytes))
    breath_length: int = csfield(Int32ul)
    breath_data: list[int] = csfield(Int32ul[this.breath_length // 4])
    gender_length: int = csfield(Int32ul)
    gender_data: list[int] = csfield(Int32ul[this.gender_length // 4])
    unknown_2: bytes = csfield(DataclassStruct(DvBytes))
    unknown_3: bytes = csfield(DataclassStruct(DvBytes))


@dataclasses.dataclass
class DvSingingTrack(DataclassMixin):
    name: DvStr = csfield(DvStr)
    mute: int = csfield(Byte)
    solo: int = csfield(Byte)
    volume: int = csfield(Int32ul)
    balance: int = csfield(Int32ul)
    segments_size: int = csfield(Int32ul)
    segments: list[DvSegment] = csfield(
        PrefixedArray(Int32ul, DataclassStruct(DvSegment))
    )


@dataclasses.dataclass
class DvAudioInfo(DataclassMixin):
    start: int = csfield(Int32ul)
    length: int = csfield(Int32ul)
    name: DvStr = csfield(DvStr)
    path: DvStr = csfield(DvStr)


@dataclasses.dataclass
class DvAudioTrack(DataclassMixin):
    name: DvStr = csfield(DvStr)
    mute: int = csfield(Byte)
    solo: int = csfield(Byte)
    volume: int = csfield(Int32ul)
    balance: int = csfield(Int32ul)
    info_size: int = csfield(Int32ul)
    not_empty: int = csfield(Int32ul)
    other_info: Union[bytes, DvAudioInfo] = csfield(
        IfThenElse(this.not_empty == 0, Bytes(0), DataclassStruct(DvAudioInfo))
    )


class DvTrackType(EnumBase):
    SINGING = 0
    AUDIO = 1


@dataclasses.dataclass
class DvTrack(DataclassMixin):
    track_type: DvTrackType = csfield(TEnum(Int32ul, DvTrackType))
    track_data: Union[DvSingingTrack, DvAudioTrack] = csfield(
        IfThenElse(
            this.track_type == DvTrackType.SINGING,
            DataclassStruct(DvSingingTrack),
            DataclassStruct(DvAudioTrack),
        )
    )


@dataclasses.dataclass
class DvProject(DataclassMixin):
    header: bytes = csfield(Const(b"SHARPKEY\x05\x00\x00\x00"))
    rest_length_in_hex: bytes = csfield(Bytes(4))
    ext_string: bytes = csfield(Const(b"ext1ext2ext3ext4ext5ext6ext7"))
    tempo_size: int = csfield(Int32ul)
    tempos: list[DvTempo] = csfield(PrefixedArray(Int32ul, DataclassStruct(DvTempo)))
    time_signature_size: int = csfield(Int32ul)
    time_signatures: list[DvTimeSignature] = csfield(
        PrefixedArray(Int32ul, DataclassStruct(DvTimeSignature))
    )
    tracks: list[DvTrack] = csfield(PrefixedArray(Int32ul, DataclassStruct(DvTrack)))


dv_project_struct = DataclassStruct(DvProject)
