import math
import struct

from construct import (
    Byte,
    Bytes,
    BytesInteger,
    Computed,
    Construct,
    CString,
    Float64l,
    Int64sl,
    LazyBound,
    PrefixedArray,
    SizeofError,
    Struct,
    Switch,
    this,
)
from construct import Enum as CSEnum

Int32sl = BytesInteger(4, swapped=True, signed=True)
Int32ul = BytesInteger(4, swapped=True)

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


class JUCECompressedIntStruct(Construct):
    def _sizeof(self, context, path):
        msg = "JUCECompressedInt has no static size"
        raise SizeofError(msg)

    def _parse(self, stream, context, path) -> int:
        byte = stream.read(1)
        if not byte:
            raise EOFError
        width = struct.unpack("<B", byte)[0]
        return int.from_bytes(stream.read(width), "little", signed=False)

    def _build(self, obj: int, stream, context, path):
        if obj < 0:
            msg = "Negative numbers not supported"
            raise ValueError(msg)
        width = math.ceil(math.log(obj + 1, 16))
        try:
            content = obj.to_bytes(width, "little", signed=False)
            stream.write(struct.pack("<B", width))
            stream.write(struct.pack(content, obj))
        except OverflowError as e:
            msg = "Number too large to be compressed"
            raise ValueError(msg) from e


JUCECompressedInt = JUCECompressedIntStruct()


JUCEVariant = Struct(
    "name" / CString("utf-8"),
    "size" / JUCECompressedInt,
    "type" / JUCEVarTypes,
    "value"
    / Switch(
        this.type,
        {
            "INT": Int32sl,
            "BOOL_TRUE": Computed(lambda ctx: True),
            "BOOL_FALSE": Computed(lambda ctx: False),
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
