import math
import struct
from typing import BinaryIO, Union

import more_itertools
from construct import (
    Byte,
    Bytes,
    BytesInteger,
    Computed,
    Const,
    Construct,
    Container,
    CString,
    Float64l,
    GreedyBytes,
    Int64sl,
    LazyBound,
    Prefixed,
    PrefixedArray,
    SizeofError,
    Struct,
    Switch,
    this,
)
from construct import Enum as CSEnum
from construct import Path as CSPath
from construct_typed import Context
from typing_extensions import Never

Int32sl = BytesInteger(4, swapped=True, signed=True)
Int32ul = BytesInteger(4, swapped=True)
Node = dict[str, Union[bool, int, float, str, bytes, "Node", list["Node"]]]

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
    def _sizeof(self, context: Context, path: CSPath) -> Never:
        msg = "JUCECompressedInt has no static size"
        raise SizeofError(msg)

    def _parse(self, stream: BinaryIO, context: Context, path: CSPath) -> int:
        byte = stream.read(1)
        if not byte:
            raise EOFError
        width = struct.unpack("<B", byte)[0]
        return int.from_bytes(stream.read(width), "little", signed=False)

    def _build(self, obj: int, stream: BinaryIO, context: Context, path: CSPath) -> int:
        if obj < 0:
            msg = "Negative numbers not supported"
            raise ValueError(msg)
        width = math.ceil(math.log(obj + 1, 256))
        try:
            content = obj.to_bytes(width, "little", signed=False)
            stream.write(struct.pack("<B", width))
            stream.write(content)
        except OverflowError as e:
            msg = "Number too large to be compressed"
            raise ValueError(msg) from e
        else:
            return obj


JUCECompressedInt = JUCECompressedIntStruct()


JUCEVariant: Container = Struct(
    "name" / CString("utf-8"),
    "data"
    / Prefixed(
        JUCECompressedInt,
        Struct(
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
                    "BINARY": GreedyBytes,
                },
            ),
        ),
    ),
)

JUCENode: Container = Struct(
    "name" / CString("utf-8"),
    "attrs" / PrefixedArray(JUCECompressedInt, JUCEVariant),
    "children" / PrefixedArray(JUCECompressedInt, LazyBound(lambda: JUCENode)),
)


JUCEPluginData = Prefixed(
    Int64sl,
    Struct(
        "data" / JUCENode,
        "padding" / Const(b"\x00" * 8),
        "private_data" / Bytes(100),
    ),
)


def build_tree_dict(node: Container) -> Node:
    attr_dict: Node = {
        attr.name: build_tree_dict(JUCENode.parse(attr.data.value))
        if isinstance(attr.data.value, bytes)
        else attr.data.value
        for attr in node.attrs
    }
    buckets = more_itertools.bucket(
        (build_tree_dict(child) for child in node.children),
        key=lambda item: next(iter(item.keys())),
    )
    children_dict: Node = {
        key: [next(iter(item.values())) for item in buckets[key]] for key in buckets
    }
    return {node.name: children_dict | attr_dict}
