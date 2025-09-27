import math
import struct
from typing import Any, BinaryIO, TypeAlias, TypeVar

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
from construct import Optional as CSOptional
from construct import Path as CSPath
from construct_typed import Context
from typing_extensions import Never

from . import singleton

Int32sl = BytesInteger(4, swapped=True, signed=True)
VariantList: TypeAlias = list["Variant"]
Variant = bool | int | float | str | bytes | VariantList
NodeType = TypeVar("NodeType", bound="Node[Any]")
Node = dict[str, Variant | NodeType | list[NodeType]]

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


@singleton
class JUCECompressedInt(Construct):
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
        width = max(math.ceil(obj.bit_length() / 8), 1)
        try:
            content = obj.to_bytes(width, "little", signed=False)
            stream.write(struct.pack("<B", width))
            stream.write(content)
        except OverflowError as e:
            msg = "Number too large to be compressed"
            raise ValueError(msg) from e
        else:
            return obj


JUCEVariant: Container = Prefixed(
    JUCECompressedInt,
    CSOptional(
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
        )
    ),
)

JUCENamedVariant: Container = Struct(
    "name" / CString("utf-8"),
    "data" / JUCEVariant,
)

JUCENode: Container = Struct(
    "name" / CString("utf-8"),
    "attrs" / PrefixedArray(JUCECompressedInt, JUCENamedVariant),
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


def build_variant(variant: Container) -> Variant:
    if isinstance(variant.value, list):
        return [build_variant(x) for x in variant.value]
    return variant.value


def build_tree_dict(node: Container) -> Node[Any]:
    attr_dict: Node[Any] = {
        attr.name: (
            build_tree_dict(JUCENode.parse(attr.data.value))
            if isinstance(attr.data.value, bytes)
            else build_variant(attr.data)
        )
        for attr in node.attrs
        if attr.data is not None
    }
    buckets = more_itertools.bucket(
        (build_tree_dict(child) for child in node.children),
        key=lambda item: next(iter(item.keys())),
    )
    children_dict: Node[Any] = {
        key: [next(iter(item.values())) for item in buckets[key]] for key in buckets
    }
    return {node.name: children_dict | attr_dict}
