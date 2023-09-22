from construct import (
    BytesInteger,
    Check,
    Const,
    FixedSized,
    Float64b,
    FocusedSeq,
    FormatField,
    GreedyString,
    If,
    Int8sb,
    Int16sb,
    PrefixedArray,
    Select,
    Struct,
    Switch,
    this,
)

Int32ub = BytesInteger(4)
Int32sb = BytesInteger(4, signed=True)

PraatItemType = FocusedSeq(
    "text",
    "size" / Int8sb,
    "text" / FixedSized(this.size, GreedyString("utf-8")),
)

PraatTierName = FocusedSeq(
    "text",
    "size" / Int16sb,
    "text" / FixedSized(this.size, GreedyString("utf-8")),
)

PraatString = Select(
    FocusedSeq(
        "text",
        "size" / Int16sb,
        Check(lambda ctx: ctx.size >= 0),
        "text" / FixedSized(this.size, GreedyString("utf-8")),
    ),
    FocusedSeq(
        "text",
        Const(-1, Int16sb),
        "size" / Int16sb,
        "text" / FixedSized(this.size * 2, GreedyString("utf-16-be")),
    ),
)

IntervalTier = Struct(
    "name" / PraatTierName,
    "xmin" / Float64b,
    "xmax" / Float64b,
    "points"
    / PrefixedArray(
        Int32ub,
        Struct(
            "xmin" / Float64b,
            "xmax" / Float64b,
            "text" / PraatString,
        ),
    ),
)

TextTier = Struct(
    "name" / PraatTierName,
    "xmin" / Float64b,
    "xmax" / Float64b,
    "points"
    / PrefixedArray(
        Int32ub,
        Struct(
            "number" / Float64b,
            "mark" / PraatString,
        ),
    ),
)

RootTier = Struct(
    "name" / PraatString,
    "xmin" / Float64b,
    "xmax" / Float64b,
    "points"
    / PrefixedArray(
        Int32ub,
        Struct(
            "number" / Float64b,
            "value" / Float64b,
        ),
    ),
)

TextGrid = Struct(
    "name" / PraatString,
    "xmin" / Float64b,
    "xmax" / Float64b,
    "has_tiers" / FormatField(">", "?"),
    "tiers"
    / If(
        this.has_tiers,
        PrefixedArray(
            Int32ub,
            Struct(
                "item_type" / PraatItemType,
                "data"
                / Switch(
                    this.item_type,
                    {
                        "IntervalTier": IntervalTier,
                        "TextTier": TextTier,
                    },
                ),
            ),
        ),
    ),
)

Pitch = Struct(
    "name" / PraatString,
    "xmin" / Float64b,
    "xmax" / Float64b,
    "nx" / Int32ub,
    "dx" / Float64b,
    "x1" / Float64b,
    "ceiling" / Int32sb,
    "unknown" / Int16sb,
    "size" / Int32ub,
    "frames"
    / Struct(
        "intensity" / Float64b,
        "candidates"
        / PrefixedArray(
            Int32ub,
            Struct(
                "frequency" / Float64b,
                "strength" / Float64b,
            ),
        ),
    )[this.nx],
)

Formant = Struct(
    "name" / PraatString,
    "xmin" / Float64b,
    "xmax" / Float64b,
    "nx" / Int32ub,
    "dx" / Float64b,
    "x1" / Float64b,
    "frames"
    / PrefixedArray(
        Int32ub,
        Struct(
            "intensity" / Float64b,
            "formants"
            / PrefixedArray(
                Int32ub,
                Struct(
                    "frequency" / Float64b,
                    "bandwidth" / Float64b,
                ),
            ),
        ),
    ),
)

PointProcess = Struct(
    "name" / PraatString,
    "xmin" / Float64b,
    "xmax" / Float64b,
    "t"
    / PrefixedArray(
        Int32ub,
        Float64b,
    ),
)

ThreeDimensional = Struct(
    "name" / PraatString,
    "xmin" / Float64b,
    "xmax" / Float64b,
    "nx" / Int32ub,
    "dx" / Float64b,
    "x1" / Float64b,
    "ymin" / Float64b,
    "ymax" / Float64b,
    "ny" / Int32ub,
    "dy" / Float64b,
    "y1" / Float64b,
    "z" / If(lambda ctx: (ctx.nx > 0 and ctx.ny > 0), Float64b[this.nx][this.ny]),
)

PraatRootItem = Struct(
    "item_type" / PraatItemType,
    "data"
    / Switch(
        this.item_type,
        {
            "TextGrid": TextGrid,
            "Pitch 1": Pitch,
            "PointProcess 1": PointProcess,
            "Intensity 2": ThreeDimensional,
            "Harmonicity 2": ThreeDimensional,
            "Sound 2": ThreeDimensional,
            "Formant 2": Formant,
            "PitchTier": RootTier,
            "IntensityTier": RootTier,
            "DurationTier": RootTier,
        },
    ),
)

PraatCollection = Struct(
    Const(b"ooBinaryFile"),
    PraatItemType,
    "items" / PrefixedArray(Int32sb, PraatRootItem),
)
