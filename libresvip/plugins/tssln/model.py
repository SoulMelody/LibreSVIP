from construct import (
    Byte,
    Bytes,
    BytesInteger,
    Computed,
    CString,
    Float64l,
    FocusedSeq,
    Int8ul,
    Int64sl,
    LazyBound,
    PrefixedArray,
    Struct,
    Switch,
    this,
)
from construct import Enum as CSEnum

Int32sl = BytesInteger(4, swapped=True, signed=True)
Int32ul = BytesInteger(4, swapped=True)


VoiSonaTrackTypes = CSEnum(
    Int32ul,
    SINGING=0,
    INSTRUMENT=1,
)

VoiSonaTrackFlags = CSEnum(
    Int32ul,
    NONE=0,
    MUTE=1,
    SOLO=2,
)

JUCEVarTypes = CSEnum(
    Byte,
    INT=1,
    BOOL_TRUE=2,
    BOOL_FALSE=3,
    DOUBLE=4,
    STRING=5,
    INT64=6,
    ARRAY=7,
    BINARY=8,
    UNDEFINED=9,
)

JUCECompressedInt = FocusedSeq(
    "value",
    "size" / Int8ul,
    "value" / BytesInteger(this.size, swapped=True),
)

JUCEVariant = Struct(
    "name" / CString("utf-8"),
    "size" / JUCECompressedInt,
    "type" / JUCEVarTypes,
    "value"
    / Switch(
        this.type,
        {
            "INT": Int32sl,
            "BOOL_TRUE": Struct(
                "value" / Computed(lambda ctx: True),
            ),
            "BOOL_FALSE": Struct(
                "value" / Computed(lambda ctx: False),
            ),
            "DOUBLE": Float64l,
            "STRING": CString("utf-8"),
            "INT64": Int64sl,
            "ARRAY": PrefixedArray(
                JUCECompressedInt,
                LazyBound(lambda: JUCEVariant),
            ),
            "BINARY": Bytes(this.size - 1),
        },
    ),
)

JUCENode = Struct(
    "name" / CString("utf-8"),
    "attrs" / PrefixedArray(JUCECompressedInt, JUCEVariant),
    "children" / PrefixedArray(JUCECompressedInt, LazyBound(lambda: JUCENode)),
)
