from construct import (
    Bytes,
    BytesInteger,
    Const,
    GreedyRange,
    Int16ul,
    PascalString,
    Prefixed,
    Struct,
    this,
)

Int32ul = BytesInteger(4, swapped=True)

PpsfChunk = Struct(
    "magic" / Bytes(4),
    "size" / Int32ul,
    "data" / Bytes(this.size),
)

PpsfLegacyProject = Struct(
    "magic" / Const(b"PPSF"),
    "body"
    / Prefixed(
        Int32ul,
        Struct(
            "version" / PascalString(Int16ul, "utf8"),
            "chunks" / GreedyRange(PpsfChunk),
        ),
    ),
)
