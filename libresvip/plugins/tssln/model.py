from construct import (
    Byte,
    Bytes,
    BytesInteger,
    Computed,
    CString,
    Float64l,
    Int8ub,
    Int64ub,
    LazyBound,
    Struct,
    Switch,
    this,
)
from construct import Enum as CSEnum

Int32sb = BytesInteger(4, swapped=False, signed=True)
Int32ub = BytesInteger(4, swapped=False)


VoiSonaTrackTypes = CSEnum(
    Int32ub,
    SINGING=0,
    INSTRUMENT=1,
)

VoiSonaTrackFlags = CSEnum(
    Int32ub,
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


JUCECompressedInt = Struct(
    "size" / Int8ub,
    "value" / BytesInteger(this.size, swapped=True),
)

JUCEVariant = Struct(
    "name" / CString("utf-8"),
    "size" / JUCECompressedInt,
    "type" / JUCEVarTypes,
    "value" / Switch(
        this.type,
        {
            "INT": Int32sb,
            "BOOL_TRUE": Struct(
                "value" / Computed(lambda ctx: True),
            ),
            "BOOL_FALSE": Struct(
                "value" / Computed(lambda ctx: False),
            ),
            "DOUBLE": Float64l,
            "STRING": CString("utf-8"),
            "INT64": Int64ub,
            "ARRAY": Struct(
                "size" / JUCECompressedInt,
                "value" / LazyBound(lambda: JUCEVariant)[this.size.value],
            ),
            "BINARY": Bytes(this.size.value - 1),
        },
    ),
)

JUCENode = Struct(
    "name" / CString("utf-8"),
    "attrs_count" / JUCECompressedInt,
    "attrs" / JUCEVariant[this.attrs_count.value],
    "children_count" / JUCECompressedInt,
    "children" / LazyBound(lambda: JUCENode)[this.children_count.value],
)
