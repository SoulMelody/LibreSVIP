from decimal import Decimal

from pydantic import BaseModel, ConfigDict
from xsdata_pydantic.fields import field

from .enums import (
    AboveBelow,
    AccidentalValue,
    ActuateValue,
    ArrowDirection,
    ArrowStyle,
    BackwardForward,
    BarStyle,
    BeamValue,
    BeaterValue,
    BendShape,
    BreathMarkValue,
    CaesuraValue,
    CancelLocation,
    CircularArrow,
    ClefSign,
    CssFontSize,
    DegreeSymbolValue,
    DegreeTypeValue,
    EffectValue,
    EnclosureShape,
    Fan,
    FermataShape,
    FontStyle,
    FontWeight,
    GlassValue,
    GroupBarlineValue,
    GroupSymbolValue,
    HandbellValue,
    HarmonClosedLocation,
    HarmonClosedValue,
    HarmonyArrangement,
    HarmonyType,
    HoleClosedLocation,
    HoleClosedValue,
    KindValue,
    LangValue,
    LeftCenterRight,
    LeftRight,
    LineEnd,
    LineLength,
    LineShape,
    LineType,
    MarginType,
    MeasureNumberingValue,
    MembraneValue,
    MetalValue,
    Mute,
    NoteheadValue,
    NoteSizeType,
    NoteTypeValue,
    NumberOrNormalValue,
    NumeralMode,
    OnOff,
    OverUnder,
    PedalType,
    PitchedValue,
    PositiveIntegerOrEmptyValue,
    PrincipalVoiceSymbol,
    RightLeftMiddle,
    SemiPitched,
    ShowFrets,
    ShowTuplet,
    ShowValue,
    SpaceValue,
    StaffDivideSymbol,
    StaffType,
    StartNote,
    StartStop,
    StartStopContinue,
    StartStopDiscontinue,
    StartStopSingle,
    StemValue,
    Step,
    StickLocation,
    StickMaterial,
    StickType,
    SwingTypeValue,
    Syllabic,
    SymbolSize,
    SyncType,
    SystemRelation,
    SystemRelationNumber,
    TapHand,
    TextDirection,
    TiedType,
    TimeRelation,
    TimeSeparator,
    TimeSymbol,
    TipDirection,
    TopBottom,
    TremoloType,
    TrillStep,
    TwoNoteTurn,
    TypeValue,
    UpDown,
    UpDownStopContinue,
    UprightInverted,
    Valign,
    ValignImage,
    WedgeType,
    Winged,
    WoodValue,
    YesNo,
)

XLINK_NS = "http://www.w3.org/1999/xlink"
XML_NS = "http://www.w3.org/XML/1998/namespace"


class Bookmark(BaseModel):
    class Meta:
        name = "bookmark"

    model_config = ConfigDict(defer_build=True)
    id: str = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    name: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    element: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    position: int | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Distance(BaseModel):
    class Meta:
        name = "distance"

    model_config = ConfigDict(defer_build=True)
    value: Decimal = field(
        metadata={
            "required": True,
        }
    )
    type_value: str = field(
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        }
    )


class Empty(BaseModel):
    class Meta:
        name = "empty"

    model_config = ConfigDict(defer_build=True)


class Feature(BaseModel):
    class Meta:
        name = "feature"

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    type_value: str | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
        },
    )


class Glyph(BaseModel):
    class Meta:
        name = "glyph"

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    type_value: str = field(
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        }
    )


class Instrument(BaseModel):
    class Meta:
        name = "instrument"

    model_config = ConfigDict(defer_build=True)
    id: str = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )


class InstrumentLink(BaseModel):
    class Meta:
        name = "instrument-link"

    model_config = ConfigDict(defer_build=True)
    id: str = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )


class MeasureLayout(BaseModel):
    class Meta:
        name = "measure-layout"

    model_config = ConfigDict(defer_build=True)
    measure_distance: Decimal | None = field(
        default=None,
        metadata={
            "name": "measure-distance",
            "type": "Element",
        },
    )


class MidiDevice(BaseModel):
    class Meta:
        name = "midi-device"

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    port: int | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 1,
            "max_inclusive": 16,
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class MidiInstrument(BaseModel):
    class Meta:
        name = "midi-instrument"

    model_config = ConfigDict(defer_build=True)
    midi_channel: int | None = field(
        default=None,
        metadata={
            "name": "midi-channel",
            "type": "Element",
            "min_inclusive": 1,
            "max_inclusive": 16,
        },
    )
    midi_name: str | None = field(
        default=None,
        metadata={
            "name": "midi-name",
            "type": "Element",
        },
    )
    midi_bank: int | None = field(
        default=None,
        metadata={
            "name": "midi-bank",
            "type": "Element",
            "min_inclusive": 1,
            "max_inclusive": 16384,
        },
    )
    midi_program: int | None = field(
        default=None,
        metadata={
            "name": "midi-program",
            "type": "Element",
            "min_inclusive": 1,
            "max_inclusive": 128,
        },
    )
    midi_unpitched: int | None = field(
        default=None,
        metadata={
            "name": "midi-unpitched",
            "type": "Element",
            "min_inclusive": 1,
            "max_inclusive": 128,
        },
    )
    volume: Decimal | None = field(
        default=None,
        metadata={
            "type": "Element",
            "min_inclusive": Decimal("0"),
            "max_inclusive": Decimal("100"),
        },
    )
    pan: Decimal | None = field(
        default=None,
        metadata={
            "type": "Element",
            "min_inclusive": Decimal("-180"),
            "max_inclusive": Decimal("180"),
        },
    )
    elevation: Decimal | None = field(
        default=None,
        metadata={
            "type": "Element",
            "min_inclusive": Decimal("-180"),
            "max_inclusive": Decimal("180"),
        },
    )
    id: str = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )


class MiscellaneousField(BaseModel):
    class Meta:
        name = "miscellaneous-field"

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    name: str = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )


class OtherAppearance(BaseModel):
    class Meta:
        name = "other-appearance"

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    type_value: str = field(
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        }
    )


class OtherListening(BaseModel):
    class Meta:
        name = "other-listening"

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    type_value: str = field(
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        }
    )
    player: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    time_only: str | None = field(
        default=None,
        metadata={
            "name": "time-only",
            "type": "Attribute",
            "pattern": r"[1-9][0-9]*(, ?[1-9][0-9]*)*",
        },
    )


class OtherPlay(BaseModel):
    class Meta:
        name = "other-play"

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    type_value: str = field(
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        }
    )


class OtherText(BaseModel):
    class Meta:
        name = "other-text"

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    smufl: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Player(BaseModel):
    class Meta:
        name = "player"

    model_config = ConfigDict(defer_build=True)
    player_name: str = field(
        metadata={
            "name": "player-name",
            "type": "Element",
            "required": True,
        }
    )
    id: str = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )


class Scaling(BaseModel):
    class Meta:
        name = "scaling"

    model_config = ConfigDict(defer_build=True)
    millimeters: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        }
    )
    tenths: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        }
    )


class StaffLayout(BaseModel):
    class Meta:
        name = "staff-layout"

    model_config = ConfigDict(defer_build=True)
    staff_distance: Decimal | None = field(
        default=None,
        metadata={
            "name": "staff-distance",
            "type": "Element",
        },
    )
    number: int | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class StaffSize(BaseModel):
    class Meta:
        name = "staff-size"

    model_config = ConfigDict(defer_build=True)
    value: Decimal = field(
        metadata={
            "required": True,
            "min_inclusive": Decimal("0"),
        }
    )
    scaling: Decimal | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": Decimal("0"),
        },
    )


class SystemMargins(BaseModel):
    class Meta:
        name = "system-margins"

    model_config = ConfigDict(defer_build=True)
    left_margin: Decimal = field(
        metadata={
            "name": "left-margin",
            "type": "Element",
            "required": True,
        }
    )
    right_margin: Decimal = field(
        metadata={
            "name": "right-margin",
            "type": "Element",
            "required": True,
        }
    )


class Timpani(BaseModel):
    class Meta:
        name = "timpani"

    model_config = ConfigDict(defer_build=True)
    smufl: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"pict\c+",
        },
    )


class TypedText(BaseModel):
    class Meta:
        name = "typed-text"

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    type_value: str | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
        },
    )


class VirtualInstrument(BaseModel):
    class Meta:
        name = "virtual-instrument"

    model_config = ConfigDict(defer_build=True)
    virtual_library: str | None = field(
        default=None,
        metadata={
            "name": "virtual-library",
            "type": "Element",
        },
    )
    virtual_name: str | None = field(
        default=None,
        metadata={
            "name": "virtual-name",
            "type": "Element",
        },
    )


class Wait(BaseModel):
    class Meta:
        name = "wait"

    model_config = ConfigDict(defer_build=True)
    player: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    time_only: str | None = field(
        default=None,
        metadata={
            "name": "time-only",
            "type": "Attribute",
            "pattern": r"[1-9][0-9]*(, ?[1-9][0-9]*)*",
        },
    )


class Accidental(BaseModel):
    class Meta:
        name = "accidental"

    model_config = ConfigDict(defer_build=True)
    value: AccidentalValue = field(
        metadata={
            "required": True,
        }
    )
    cautionary: YesNo | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    editorial: YesNo | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    parentheses: YesNo | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    bracket: YesNo | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    size: SymbolSize | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    smufl: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"(acc|medRenFla|medRenNatura|medRenShar|kievanAccidental)(\c+)",
        },
    )


class AccidentalMark(BaseModel):
    class Meta:
        name = "accidental-mark"

    model_config = ConfigDict(defer_build=True)
    value: AccidentalValue = field(
        metadata={
            "required": True,
        }
    )
    parentheses: YesNo | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    bracket: YesNo | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    size: SymbolSize | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    placement: AboveBelow | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    smufl: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"(acc|medRenFla|medRenNatura|medRenShar|kievanAccidental)(\c+)",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class AccidentalText(BaseModel):
    class Meta:
        name = "accidental-text"

    model_config = ConfigDict(defer_build=True)
    value: AccidentalValue = field(
        metadata={
            "required": True,
        }
    )
    justify: LeftCenterRight | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    halign: LeftCenterRight | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    valign: Valign | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    underline: int | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 3,
        },
    )
    overline: int | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 3,
        },
    )
    line_through: int | None = field(
        default=None,
        metadata={
            "name": "line-through",
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 3,
        },
    )
    rotation: Decimal | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": Decimal("-180"),
            "max_inclusive": Decimal("180"),
        },
    )
    letter_spacing: Decimal | NumberOrNormalValue | None = field(
        default=None,
        metadata={
            "name": "letter-spacing",
            "type": "Attribute",
        },
    )
    line_height: Decimal | NumberOrNormalValue | None = field(
        default=None,
        metadata={
            "name": "line-height",
            "type": "Attribute",
        },
    )
    lang: str | LangValue | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "namespace": XML_NS,
        },
    )
    space: SpaceValue | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "namespace": XML_NS,
        },
    )
    dir: TextDirection | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    enclosure: EnclosureShape | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    smufl: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"(acc|medRenFla|medRenNatura|medRenShar|kievanAccidental)(\c+)",
        },
    )


class Accord(BaseModel):
    class Meta:
        name = "accord"

    model_config = ConfigDict(defer_build=True)
    tuning_step: Step = field(
        metadata={
            "name": "tuning-step",
            "type": "Element",
            "required": True,
        }
    )
    tuning_alter: Decimal | None = field(
        default=None,
        metadata={
            "name": "tuning-alter",
            "type": "Element",
        },
    )
    tuning_octave: int = field(
        metadata={
            "name": "tuning-octave",
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 9,
        }
    )
    string: int | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class AccordionRegistration(BaseModel):
    class Meta:
        name = "accordion-registration"

    model_config = ConfigDict(defer_build=True)
    accordion_high: Empty | None = field(
        default=None,
        metadata={
            "name": "accordion-high",
            "type": "Element",
        },
    )
    accordion_middle: int | None = field(
        default=None,
        metadata={
            "name": "accordion-middle",
            "type": "Element",
            "min_inclusive": 1,
            "max_inclusive": 3,
        },
    )
    accordion_low: Empty | None = field(
        default=None,
        metadata={
            "name": "accordion-low",
            "type": "Element",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    halign: LeftCenterRight | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    valign: Valign | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Arpeggiate(BaseModel):
    class Meta:
        name = "arpeggiate"

    model_config = ConfigDict(defer_build=True)
    number: int | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 1,
            "max_inclusive": 16,
        },
    )
    direction: UpDown | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    unbroken: YesNo | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    placement: AboveBelow | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Arrow(BaseModel):
    class Meta:
        name = "arrow"

    model_config = ConfigDict(defer_build=True)
    arrow_direction: ArrowDirection | None = field(
        default=None,
        metadata={
            "name": "arrow-direction",
            "type": "Element",
        },
    )
    arrow_style: ArrowStyle | None = field(
        default=None,
        metadata={
            "name": "arrow-style",
            "type": "Element",
        },
    )
    arrowhead: Empty | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    circular_arrow: CircularArrow | None = field(
        default=None,
        metadata={
            "name": "circular-arrow",
            "type": "Element",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    placement: AboveBelow | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    smufl: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Assess(BaseModel):
    class Meta:
        name = "assess"

    model_config = ConfigDict(defer_build=True)
    type_value: YesNo = field(
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        }
    )
    player: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    time_only: str | None = field(
        default=None,
        metadata={
            "name": "time-only",
            "type": "Attribute",
            "pattern": r"[1-9][0-9]*(, ?[1-9][0-9]*)*",
        },
    )


class BarStyleColor(BaseModel):
    class Meta:
        name = "bar-style-color"

    model_config = ConfigDict(defer_build=True)
    value: BarStyle = field(
        metadata={
            "required": True,
        }
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class Barre(BaseModel):
    class Meta:
        name = "barre"

    model_config = ConfigDict(defer_build=True)
    type_value: StartStop = field(
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        }
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class BassStep(BaseModel):
    class Meta:
        name = "bass-step"

    model_config = ConfigDict(defer_build=True)
    value: Step = field(
        metadata={
            "required": True,
        }
    )
    text: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class Beam(BaseModel):
    class Meta:
        name = "beam"

    model_config = ConfigDict(defer_build=True)
    value: BeamValue = field(
        metadata={
            "required": True,
        }
    )
    number: int = field(
        default=1,
        metadata={
            "type": "Attribute",
            "min_inclusive": 1,
            "max_inclusive": 8,
        },
    )
    repeater: YesNo | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    fan: Fan | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class BeatRepeat(BaseModel):
    class Meta:
        name = "beat-repeat"

    model_config = ConfigDict(defer_build=True)
    slash_type: NoteTypeValue | None = field(
        default=None,
        metadata={
            "name": "slash-type",
            "type": "Element",
        },
    )
    slash_dot: list[Empty] = field(
        default_factory=list,
        metadata={
            "name": "slash-dot",
            "type": "Element",
        },
    )
    except_voice: list[str] = field(
        default_factory=list,
        metadata={
            "name": "except-voice",
            "type": "Element",
        },
    )
    type_value: StartStop = field(
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        }
    )
    slashes: int | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    use_dots: YesNo | None = field(
        default=None,
        metadata={
            "name": "use-dots",
            "type": "Attribute",
        },
    )


class BeatUnitTied(BaseModel):
    class Meta:
        name = "beat-unit-tied"

    model_config = ConfigDict(defer_build=True)
    beat_unit: NoteTypeValue = field(
        metadata={
            "name": "beat-unit",
            "type": "Element",
            "required": True,
        }
    )
    beat_unit_dot: list[Empty] = field(
        default_factory=list,
        metadata={
            "name": "beat-unit-dot",
            "type": "Element",
        },
    )


class Beater(BaseModel):
    class Meta:
        name = "beater"

    model_config = ConfigDict(defer_build=True)
    value: BeaterValue = field(
        metadata={
            "required": True,
        }
    )
    tip: TipDirection | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Bracket(BaseModel):
    class Meta:
        name = "bracket"

    model_config = ConfigDict(defer_build=True)
    type_value: StartStopContinue = field(
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        }
    )
    number: int | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 1,
            "max_inclusive": 16,
        },
    )
    line_end: LineEnd = field(
        metadata={
            "name": "line-end",
            "type": "Attribute",
            "required": True,
        }
    )
    end_length: Decimal | None = field(
        default=None,
        metadata={
            "name": "end-length",
            "type": "Attribute",
        },
    )
    line_type: LineType | None = field(
        default=None,
        metadata={
            "name": "line-type",
            "type": "Attribute",
        },
    )
    dash_length: Decimal | None = field(
        default=None,
        metadata={
            "name": "dash-length",
            "type": "Attribute",
        },
    )
    space_length: Decimal | None = field(
        default=None,
        metadata={
            "name": "space-length",
            "type": "Attribute",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class BreathMark(BaseModel):
    class Meta:
        name = "breath-mark"

    model_config = ConfigDict(defer_build=True)
    value: BreathMarkValue = field(
        metadata={
            "required": True,
        }
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    placement: AboveBelow | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Caesura(BaseModel):
    class Meta:
        name = "caesura"

    model_config = ConfigDict(defer_build=True)
    value: CaesuraValue = field(
        metadata={
            "required": True,
        }
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    placement: AboveBelow | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Cancel(BaseModel):
    class Meta:
        name = "cancel"

    model_config = ConfigDict(defer_build=True)
    value: int = field(
        metadata={
            "required": True,
        }
    )
    location: CancelLocation | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Clef(BaseModel):
    class Meta:
        name = "clef"

    model_config = ConfigDict(defer_build=True)
    sign: ClefSign = field(
        metadata={
            "type": "Element",
            "required": True,
        }
    )
    line: int | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    clef_octave_change: int | None = field(
        default=None,
        metadata={
            "name": "clef-octave-change",
            "type": "Element",
        },
    )
    number: int | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    additional: YesNo | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    size: SymbolSize | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    after_barline: YesNo | None = field(
        default=None,
        metadata={
            "name": "after-barline",
            "type": "Attribute",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    print_object: YesNo | None = field(
        default=None,
        metadata={
            "name": "print-object",
            "type": "Attribute",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Coda(BaseModel):
    class Meta:
        name = "coda"

    model_config = ConfigDict(defer_build=True)
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    halign: LeftCenterRight | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    valign: Valign | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    smufl: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"coda\c*",
        },
    )


class Dashes(BaseModel):
    class Meta:
        name = "dashes"

    model_config = ConfigDict(defer_build=True)
    type_value: StartStopContinue = field(
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        }
    )
    number: int | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 1,
            "max_inclusive": 16,
        },
    )
    dash_length: Decimal | None = field(
        default=None,
        metadata={
            "name": "dash-length",
            "type": "Attribute",
        },
    )
    space_length: Decimal | None = field(
        default=None,
        metadata={
            "name": "space-length",
            "type": "Attribute",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class DegreeAlter(BaseModel):
    class Meta:
        name = "degree-alter"

    model_config = ConfigDict(defer_build=True)
    value: Decimal = field(
        metadata={
            "required": True,
        }
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    plus_minus: YesNo | None = field(
        default=None,
        metadata={
            "name": "plus-minus",
            "type": "Attribute",
        },
    )


class DegreeType(BaseModel):
    class Meta:
        name = "degree-type"

    model_config = ConfigDict(defer_build=True)
    value: DegreeTypeValue = field(
        metadata={
            "required": True,
        }
    )
    text: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class DegreeValue(BaseModel):
    class Meta:
        name = "degree-value"

    model_config = ConfigDict(defer_build=True)
    value: int = field(
        metadata={
            "required": True,
        }
    )
    symbol: DegreeSymbolValue | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    text: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class Double(BaseModel):
    class Meta:
        name = "double"

    model_config = ConfigDict(defer_build=True)
    above: YesNo | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Dynamics(BaseModel):
    class Meta:
        name = "dynamics"

    model_config = ConfigDict(defer_build=True)
    p: list[Empty] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    pp: list[Empty] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    ppp: list[Empty] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    pppp: list[Empty] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    ppppp: list[Empty] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    pppppp: list[Empty] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    f: list[Empty] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    ff: list[Empty] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    fff: list[Empty] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    ffff: list[Empty] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    fffff: list[Empty] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    ffffff: list[Empty] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    mp: list[Empty] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    mf: list[Empty] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    sf: list[Empty] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    sfp: list[Empty] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    sfpp: list[Empty] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    fp: list[Empty] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    rf: list[Empty] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    rfz: list[Empty] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    sfz: list[Empty] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    sffz: list[Empty] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    fz: list[Empty] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    n: list[Empty] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    pf: list[Empty] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    sfzp: list[Empty] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    other_dynamics: list[OtherText] = field(
        default_factory=list,
        metadata={
            "name": "other-dynamics",
            "type": "Element",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    halign: LeftCenterRight | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    valign: Valign | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    placement: AboveBelow | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    underline: int | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 3,
        },
    )
    overline: int | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 3,
        },
    )
    line_through: int | None = field(
        default=None,
        metadata={
            "name": "line-through",
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 3,
        },
    )
    enclosure: EnclosureShape | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Effect(BaseModel):
    class Meta:
        name = "effect"

    model_config = ConfigDict(defer_build=True)
    value: EffectValue = field(
        metadata={
            "required": True,
        }
    )
    smufl: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"pict\c+",
        },
    )


class Elision(BaseModel):
    class Meta:
        name = "elision"

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    smufl: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"lyrics\c+",
        },
    )


class EmptyFont(BaseModel):
    class Meta:
        name = "empty-font"

    model_config = ConfigDict(defer_build=True)
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )


class EmptyLine(BaseModel):
    class Meta:
        name = "empty-line"

    model_config = ConfigDict(defer_build=True)
    line_shape: LineShape | None = field(
        default=None,
        metadata={
            "name": "line-shape",
            "type": "Attribute",
        },
    )
    line_type: LineType | None = field(
        default=None,
        metadata={
            "name": "line-type",
            "type": "Attribute",
        },
    )
    line_length: LineLength | None = field(
        default=None,
        metadata={
            "name": "line-length",
            "type": "Attribute",
        },
    )
    dash_length: Decimal | None = field(
        default=None,
        metadata={
            "name": "dash-length",
            "type": "Attribute",
        },
    )
    space_length: Decimal | None = field(
        default=None,
        metadata={
            "name": "space-length",
            "type": "Attribute",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    placement: AboveBelow | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class EmptyPlacement(BaseModel):
    class Meta:
        name = "empty-placement"

    model_config = ConfigDict(defer_build=True)
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    placement: AboveBelow | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class EmptyPlacementSmufl(BaseModel):
    class Meta:
        name = "empty-placement-smufl"

    model_config = ConfigDict(defer_build=True)
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    placement: AboveBelow | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    smufl: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class EmptyPrintObjectStyleAlign(BaseModel):
    class Meta:
        name = "empty-print-object-style-align"

    model_config = ConfigDict(defer_build=True)
    print_object: YesNo | None = field(
        default=None,
        metadata={
            "name": "print-object",
            "type": "Attribute",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    halign: LeftCenterRight | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    valign: Valign | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class EmptyPrintStyle(BaseModel):
    class Meta:
        name = "empty-print-style"

    model_config = ConfigDict(defer_build=True)
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class EmptyPrintStyleAlign(BaseModel):
    class Meta:
        name = "empty-print-style-align"

    model_config = ConfigDict(defer_build=True)
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    halign: LeftCenterRight | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    valign: Valign | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class EmptyPrintStyleAlignId(BaseModel):
    class Meta:
        name = "empty-print-style-align-id"

    model_config = ConfigDict(defer_build=True)
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    halign: LeftCenterRight | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    valign: Valign | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class EmptyTrillSound(BaseModel):
    class Meta:
        name = "empty-trill-sound"

    model_config = ConfigDict(defer_build=True)
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    placement: AboveBelow | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    start_note: StartNote | None = field(
        default=None,
        metadata={
            "name": "start-note",
            "type": "Attribute",
        },
    )
    trill_step: TrillStep | None = field(
        default=None,
        metadata={
            "name": "trill-step",
            "type": "Attribute",
        },
    )
    two_note_turn: TwoNoteTurn | None = field(
        default=None,
        metadata={
            "name": "two-note-turn",
            "type": "Attribute",
        },
    )
    accelerate: YesNo | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    beats: Decimal | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": Decimal("2"),
        },
    )
    second_beat: Decimal | None = field(
        default=None,
        metadata={
            "name": "second-beat",
            "type": "Attribute",
            "min_inclusive": Decimal("0"),
            "max_inclusive": Decimal("100"),
        },
    )
    last_beat: Decimal | None = field(
        default=None,
        metadata={
            "name": "last-beat",
            "type": "Attribute",
            "min_inclusive": Decimal("0"),
            "max_inclusive": Decimal("100"),
        },
    )


class Ending(BaseModel):
    class Meta:
        name = "ending"

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    number: str = field(
        metadata={
            "type": "Attribute",
            "required": True,
            "pattern": r"([ ]*)|([1-9][0-9]*(, ?[1-9][0-9]*)*)",
        }
    )
    type_value: StartStopDiscontinue = field(
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        }
    )
    print_object: YesNo | None = field(
        default=None,
        metadata={
            "name": "print-object",
            "type": "Attribute",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    system: SystemRelation | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    end_length: Decimal | None = field(
        default=None,
        metadata={
            "name": "end-length",
            "type": "Attribute",
        },
    )
    text_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "text-x",
            "type": "Attribute",
        },
    )
    text_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "text-y",
            "type": "Attribute",
        },
    )


class Extend(BaseModel):
    class Meta:
        name = "extend"

    model_config = ConfigDict(defer_build=True)
    type_value: StartStopContinue | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class Fermata(BaseModel):
    class Meta:
        name = "fermata"

    model_config = ConfigDict(defer_build=True)
    value: FermataShape = field(
        metadata={
            "required": True,
        }
    )
    type_value: UprightInverted | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Fingering(BaseModel):
    class Meta:
        name = "fingering"

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    substitution: YesNo | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    alternate: YesNo | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    placement: AboveBelow | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class FirstFret(BaseModel):
    class Meta:
        name = "first-fret"

    model_config = ConfigDict(defer_build=True)
    value: int = field(
        metadata={
            "required": True,
        }
    )
    text: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    location: LeftRight | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class FormattedSymbol(BaseModel):
    class Meta:
        name = "formatted-symbol"

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    justify: LeftCenterRight | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    halign: LeftCenterRight | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    valign: Valign | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    underline: int | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 3,
        },
    )
    overline: int | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 3,
        },
    )
    line_through: int | None = field(
        default=None,
        metadata={
            "name": "line-through",
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 3,
        },
    )
    rotation: Decimal | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": Decimal("-180"),
            "max_inclusive": Decimal("180"),
        },
    )
    letter_spacing: Decimal | NumberOrNormalValue | None = field(
        default=None,
        metadata={
            "name": "letter-spacing",
            "type": "Attribute",
        },
    )
    line_height: Decimal | NumberOrNormalValue | None = field(
        default=None,
        metadata={
            "name": "line-height",
            "type": "Attribute",
        },
    )
    dir: TextDirection | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    enclosure: EnclosureShape | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class FormattedSymbolId(BaseModel):
    class Meta:
        name = "formatted-symbol-id"

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    justify: LeftCenterRight | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    halign: LeftCenterRight | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    valign: Valign | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    underline: int | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 3,
        },
    )
    overline: int | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 3,
        },
    )
    line_through: int | None = field(
        default=None,
        metadata={
            "name": "line-through",
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 3,
        },
    )
    rotation: Decimal | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": Decimal("-180"),
            "max_inclusive": Decimal("180"),
        },
    )
    letter_spacing: Decimal | NumberOrNormalValue | None = field(
        default=None,
        metadata={
            "name": "letter-spacing",
            "type": "Attribute",
        },
    )
    line_height: Decimal | NumberOrNormalValue | None = field(
        default=None,
        metadata={
            "name": "line-height",
            "type": "Attribute",
        },
    )
    dir: TextDirection | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    enclosure: EnclosureShape | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class FormattedText(BaseModel):
    class Meta:
        name = "formatted-text"

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    justify: LeftCenterRight | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    halign: LeftCenterRight | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    valign: Valign | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    underline: int | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 3,
        },
    )
    overline: int | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 3,
        },
    )
    line_through: int | None = field(
        default=None,
        metadata={
            "name": "line-through",
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 3,
        },
    )
    rotation: Decimal | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": Decimal("-180"),
            "max_inclusive": Decimal("180"),
        },
    )
    letter_spacing: Decimal | NumberOrNormalValue | None = field(
        default=None,
        metadata={
            "name": "letter-spacing",
            "type": "Attribute",
        },
    )
    line_height: Decimal | NumberOrNormalValue | None = field(
        default=None,
        metadata={
            "name": "line-height",
            "type": "Attribute",
        },
    )
    lang: str | LangValue | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "namespace": XML_NS,
        },
    )
    space: SpaceValue | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "namespace": XML_NS,
        },
    )
    dir: TextDirection | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    enclosure: EnclosureShape | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class FormattedTextId(BaseModel):
    class Meta:
        name = "formatted-text-id"

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    justify: LeftCenterRight | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    halign: LeftCenterRight | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    valign: Valign | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    underline: int | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 3,
        },
    )
    overline: int | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 3,
        },
    )
    line_through: int | None = field(
        default=None,
        metadata={
            "name": "line-through",
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 3,
        },
    )
    rotation: Decimal | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": Decimal("-180"),
            "max_inclusive": Decimal("180"),
        },
    )
    letter_spacing: Decimal | NumberOrNormalValue | None = field(
        default=None,
        metadata={
            "name": "letter-spacing",
            "type": "Attribute",
        },
    )
    line_height: Decimal | NumberOrNormalValue | None = field(
        default=None,
        metadata={
            "name": "line-height",
            "type": "Attribute",
        },
    )
    lang: str | LangValue | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "namespace": XML_NS,
        },
    )
    space: SpaceValue | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "namespace": XML_NS,
        },
    )
    dir: TextDirection | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    enclosure: EnclosureShape | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Fret(BaseModel):
    class Meta:
        name = "fret"

    model_config = ConfigDict(defer_build=True)
    value: int = field(
        metadata={
            "required": True,
        }
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class Glass(BaseModel):
    class Meta:
        name = "glass"

    model_config = ConfigDict(defer_build=True)
    value: GlassValue = field(
        metadata={
            "required": True,
        }
    )
    smufl: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"pict\c+",
        },
    )


class Glissando(BaseModel):
    class Meta:
        name = "glissando"

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    type_value: StartStop = field(
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        }
    )
    number: int = field(
        default=1,
        metadata={
            "type": "Attribute",
            "min_inclusive": 1,
            "max_inclusive": 16,
        },
    )
    line_type: LineType | None = field(
        default=None,
        metadata={
            "name": "line-type",
            "type": "Attribute",
        },
    )
    dash_length: Decimal | None = field(
        default=None,
        metadata={
            "name": "dash-length",
            "type": "Attribute",
        },
    )
    space_length: Decimal | None = field(
        default=None,
        metadata={
            "name": "space-length",
            "type": "Attribute",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Grace(BaseModel):
    class Meta:
        name = "grace"

    model_config = ConfigDict(defer_build=True)
    steal_time_previous: Decimal | None = field(
        default=None,
        metadata={
            "name": "steal-time-previous",
            "type": "Attribute",
            "min_inclusive": Decimal("0"),
            "max_inclusive": Decimal("100"),
        },
    )
    steal_time_following: Decimal | None = field(
        default=None,
        metadata={
            "name": "steal-time-following",
            "type": "Attribute",
            "min_inclusive": Decimal("0"),
            "max_inclusive": Decimal("100"),
        },
    )
    make_time: Decimal | None = field(
        default=None,
        metadata={
            "name": "make-time",
            "type": "Attribute",
        },
    )
    slash: YesNo | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class GroupBarline(BaseModel):
    class Meta:
        name = "group-barline"

    model_config = ConfigDict(defer_build=True)
    value: GroupBarlineValue = field(
        metadata={
            "required": True,
        }
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class GroupName(BaseModel):
    class Meta:
        name = "group-name"

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    justify: LeftCenterRight | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class GroupSymbol(BaseModel):
    class Meta:
        name = "group-symbol"

    model_config = ConfigDict(defer_build=True)
    value: GroupSymbolValue = field(
        metadata={
            "required": True,
        }
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class Grouping(BaseModel):
    class Meta:
        name = "grouping"

    model_config = ConfigDict(defer_build=True)
    feature: list[Feature] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    type_value: StartStopSingle = field(
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        }
    )
    number: str = field(
        default="1",
        metadata={
            "type": "Attribute",
        },
    )
    member_of: str | None = field(
        default=None,
        metadata={
            "name": "member-of",
            "type": "Attribute",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class HammerOnPullOff(BaseModel):
    class Meta:
        name = "hammer-on-pull-off"

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    type_value: StartStop = field(
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        }
    )
    number: int = field(
        default=1,
        metadata={
            "type": "Attribute",
            "min_inclusive": 1,
            "max_inclusive": 16,
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    placement: AboveBelow | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Handbell(BaseModel):
    class Meta:
        name = "handbell"

    model_config = ConfigDict(defer_build=True)
    value: HandbellValue = field(
        metadata={
            "required": True,
        }
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    placement: AboveBelow | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class HarmonClosed(BaseModel):
    class Meta:
        name = "harmon-closed"

    model_config = ConfigDict(defer_build=True)
    value: HarmonClosedValue = field(
        metadata={
            "required": True,
        }
    )
    location: HarmonClosedLocation | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Harmonic(BaseModel):
    class Meta:
        name = "harmonic"

    model_config = ConfigDict(defer_build=True)
    natural: Empty | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    artificial: Empty | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    base_pitch: Empty | None = field(
        default=None,
        metadata={
            "name": "base-pitch",
            "type": "Element",
        },
    )
    touching_pitch: Empty | None = field(
        default=None,
        metadata={
            "name": "touching-pitch",
            "type": "Element",
        },
    )
    sounding_pitch: Empty | None = field(
        default=None,
        metadata={
            "name": "sounding-pitch",
            "type": "Element",
        },
    )
    print_object: YesNo | None = field(
        default=None,
        metadata={
            "name": "print-object",
            "type": "Attribute",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    placement: AboveBelow | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class HarmonyAlter(BaseModel):
    class Meta:
        name = "harmony-alter"

    model_config = ConfigDict(defer_build=True)
    value: Decimal = field(
        metadata={
            "required": True,
        }
    )
    print_object: YesNo | None = field(
        default=None,
        metadata={
            "name": "print-object",
            "type": "Attribute",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    location: LeftRight | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class HoleClosed(BaseModel):
    class Meta:
        name = "hole-closed"

    model_config = ConfigDict(defer_build=True)
    value: HoleClosedValue = field(
        metadata={
            "required": True,
        }
    )
    location: HoleClosedLocation | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class HorizontalTurn(BaseModel):
    class Meta:
        name = "horizontal-turn"

    model_config = ConfigDict(defer_build=True)
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    placement: AboveBelow | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    start_note: StartNote | None = field(
        default=None,
        metadata={
            "name": "start-note",
            "type": "Attribute",
        },
    )
    trill_step: TrillStep | None = field(
        default=None,
        metadata={
            "name": "trill-step",
            "type": "Attribute",
        },
    )
    two_note_turn: TwoNoteTurn | None = field(
        default=None,
        metadata={
            "name": "two-note-turn",
            "type": "Attribute",
        },
    )
    accelerate: YesNo | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    beats: Decimal | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": Decimal("2"),
        },
    )
    second_beat: Decimal | None = field(
        default=None,
        metadata={
            "name": "second-beat",
            "type": "Attribute",
            "min_inclusive": Decimal("0"),
            "max_inclusive": Decimal("100"),
        },
    )
    last_beat: Decimal | None = field(
        default=None,
        metadata={
            "name": "last-beat",
            "type": "Attribute",
            "min_inclusive": Decimal("0"),
            "max_inclusive": Decimal("100"),
        },
    )
    slash: YesNo | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Image(BaseModel):
    class Meta:
        name = "image"

    model_config = ConfigDict(defer_build=True)
    source: str = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    type_value: str = field(
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        }
    )
    height: Decimal | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    width: Decimal | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    halign: LeftCenterRight | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    valign: ValignImage | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class InstrumentChange(BaseModel):
    class Meta:
        name = "instrument-change"

    model_config = ConfigDict(defer_build=True)
    instrument_sound: str | None = field(
        default=None,
        metadata={
            "name": "instrument-sound",
            "type": "Element",
        },
    )
    solo: Empty | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    ensemble: int | PositiveIntegerOrEmptyValue | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    virtual_instrument: VirtualInstrument | None = field(
        default=None,
        metadata={
            "name": "virtual-instrument",
            "type": "Element",
        },
    )
    id: str = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )


class Interchangeable(BaseModel):
    class Meta:
        name = "interchangeable"

    model_config = ConfigDict(defer_build=True)
    time_relation: TimeRelation | None = field(
        default=None,
        metadata={
            "name": "time-relation",
            "type": "Element",
        },
    )
    beats: list[str] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )
    beat_type: list[str] = field(
        default_factory=list,
        metadata={
            "name": "beat-type",
            "type": "Element",
            "min_occurs": 1,
        },
    )
    symbol: TimeSymbol | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    separator: TimeSeparator | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Inversion(BaseModel):
    class Meta:
        name = "inversion"

    model_config = ConfigDict(defer_build=True)
    value: int = field(
        metadata={
            "required": True,
        }
    )
    text: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class KeyAccidental(BaseModel):
    class Meta:
        name = "key-accidental"

    model_config = ConfigDict(defer_build=True)
    value: AccidentalValue = field(
        metadata={
            "required": True,
        }
    )
    smufl: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"(acc|medRenFla|medRenNatura|medRenShar|kievanAccidental)(\c+)",
        },
    )


class KeyOctave(BaseModel):
    class Meta:
        name = "key-octave"

    model_config = ConfigDict(defer_build=True)
    value: int = field(
        metadata={
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 9,
        }
    )
    number: int = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    cancel: YesNo | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Kind(BaseModel):
    class Meta:
        name = "kind"

    model_config = ConfigDict(defer_build=True)
    value: KindValue = field(
        metadata={
            "required": True,
        }
    )
    use_symbols: YesNo | None = field(
        default=None,
        metadata={
            "name": "use-symbols",
            "type": "Attribute",
        },
    )
    text: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    stack_degrees: YesNo | None = field(
        default=None,
        metadata={
            "name": "stack-degrees",
            "type": "Attribute",
        },
    )
    parentheses_degrees: YesNo | None = field(
        default=None,
        metadata={
            "name": "parentheses-degrees",
            "type": "Attribute",
        },
    )
    bracket_degrees: YesNo | None = field(
        default=None,
        metadata={
            "name": "bracket-degrees",
            "type": "Attribute",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    halign: LeftCenterRight | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    valign: Valign | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Level(BaseModel):
    class Meta:
        name = "level"

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    reference: YesNo | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    type_value: StartStopSingle | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
        },
    )
    parentheses: YesNo | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    bracket: YesNo | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    size: SymbolSize | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class LineDetail(BaseModel):
    class Meta:
        name = "line-detail"

    model_config = ConfigDict(defer_build=True)
    line: int = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    width: Decimal | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    line_type: LineType | None = field(
        default=None,
        metadata={
            "name": "line-type",
            "type": "Attribute",
        },
    )
    print_object: YesNo | None = field(
        default=None,
        metadata={
            "name": "print-object",
            "type": "Attribute",
        },
    )


class Link(BaseModel):
    class Meta:
        name = "link"

    model_config = ConfigDict(defer_build=True)
    href: str = field(
        metadata={
            "type": "Attribute",
            "namespace": XLINK_NS,
            "required": True,
        }
    )
    type_value: TypeValue = field(
        const=True,
        default=TypeValue.SIMPLE,
        metadata={
            "name": "type",
            "type": "Attribute",
            "namespace": XLINK_NS,
        },
    )
    role: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "namespace": XLINK_NS,
        },
    )
    title: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "namespace": XLINK_NS,
        },
    )
    show: ShowValue = field(
        default=ShowValue.REPLACE,
        metadata={
            "type": "Attribute",
            "namespace": XLINK_NS,
        },
    )
    actuate: ActuateValue = field(
        default=ActuateValue.ON_REQUEST,
        metadata={
            "type": "Attribute",
            "namespace": XLINK_NS,
        },
    )
    name: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    element: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    position: int | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )


class LyricFont(BaseModel):
    class Meta:
        name = "lyric-font"

    model_config = ConfigDict(defer_build=True)
    number: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    name: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )


class LyricLanguage(BaseModel):
    class Meta:
        name = "lyric-language"

    model_config = ConfigDict(defer_build=True)
    number: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    name: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    lang: str | LangValue = field(
        metadata={
            "type": "Attribute",
            "namespace": XML_NS,
            "required": True,
        }
    )


class MeasureNumbering(BaseModel):
    class Meta:
        name = "measure-numbering"

    model_config = ConfigDict(defer_build=True)
    value: MeasureNumberingValue = field(
        metadata={
            "required": True,
        }
    )
    system: SystemRelationNumber | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    staff: int | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    multiple_rest_always: YesNo | None = field(
        default=None,
        metadata={
            "name": "multiple-rest-always",
            "type": "Attribute",
        },
    )
    multiple_rest_range: YesNo | None = field(
        default=None,
        metadata={
            "name": "multiple-rest-range",
            "type": "Attribute",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    halign: LeftCenterRight | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    valign: Valign | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class MeasureRepeat(BaseModel):
    class Meta:
        name = "measure-repeat"

    model_config = ConfigDict(defer_build=True)
    value: int | PositiveIntegerOrEmptyValue = field()
    type_value: StartStop = field(
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        }
    )
    slashes: int | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Membrane(BaseModel):
    class Meta:
        name = "membrane"

    model_config = ConfigDict(defer_build=True)
    value: MembraneValue = field(
        metadata={
            "required": True,
        }
    )
    smufl: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"pict\c+",
        },
    )


class Metal(BaseModel):
    class Meta:
        name = "metal"

    model_config = ConfigDict(defer_build=True)
    value: MetalValue = field(
        metadata={
            "required": True,
        }
    )
    smufl: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"pict\c+",
        },
    )


class MetronomeBeam(BaseModel):
    class Meta:
        name = "metronome-beam"

    model_config = ConfigDict(defer_build=True)
    value: BeamValue = field(
        metadata={
            "required": True,
        }
    )
    number: int = field(
        default=1,
        metadata={
            "type": "Attribute",
            "min_inclusive": 1,
            "max_inclusive": 8,
        },
    )


class MetronomeTied(BaseModel):
    class Meta:
        name = "metronome-tied"

    model_config = ConfigDict(defer_build=True)
    type_value: StartStop = field(
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        }
    )


class Miscellaneous(BaseModel):
    class Meta:
        name = "miscellaneous"

    model_config = ConfigDict(defer_build=True)
    miscellaneous_field: list[MiscellaneousField] = field(
        default_factory=list,
        metadata={
            "name": "miscellaneous-field",
            "type": "Element",
        },
    )


class MultipleRest(BaseModel):
    class Meta:
        name = "multiple-rest"

    model_config = ConfigDict(defer_build=True)
    value: int = field(
        metadata={
            "required": True,
        }
    )
    use_symbols: YesNo | None = field(
        default=None,
        metadata={
            "name": "use-symbols",
            "type": "Attribute",
        },
    )


class NonArpeggiate(BaseModel):
    class Meta:
        name = "non-arpeggiate"

    model_config = ConfigDict(defer_build=True)
    type_value: TopBottom = field(
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        }
    )
    number: int | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 1,
            "max_inclusive": 16,
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    placement: AboveBelow | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class NoteSize(BaseModel):
    class Meta:
        name = "note-size"

    model_config = ConfigDict(defer_build=True)
    value: Decimal = field(
        metadata={
            "required": True,
            "min_inclusive": Decimal("0"),
        }
    )
    type_value: NoteSizeType = field(
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        }
    )


class NoteType(BaseModel):
    class Meta:
        name = "note-type"

    model_config = ConfigDict(defer_build=True)
    value: NoteTypeValue = field(
        metadata={
            "required": True,
        }
    )
    size: SymbolSize | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Notehead(BaseModel):
    class Meta:
        name = "notehead"

    model_config = ConfigDict(defer_build=True)
    value: NoteheadValue = field(
        metadata={
            "required": True,
        }
    )
    filled: YesNo | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    parentheses: YesNo | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    smufl: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class NumeralKey(BaseModel):
    class Meta:
        name = "numeral-key"

    model_config = ConfigDict(defer_build=True)
    numeral_fifths: int = field(
        metadata={
            "name": "numeral-fifths",
            "type": "Element",
            "required": True,
        }
    )
    numeral_mode: NumeralMode = field(
        metadata={
            "name": "numeral-mode",
            "type": "Element",
            "required": True,
        }
    )
    print_object: YesNo | None = field(
        default=None,
        metadata={
            "name": "print-object",
            "type": "Attribute",
        },
    )


class NumeralRoot(BaseModel):
    class Meta:
        name = "numeral-root"

    model_config = ConfigDict(defer_build=True)
    value: int = field(
        metadata={
            "required": True,
            "min_inclusive": 1,
            "max_inclusive": 7,
        }
    )
    text: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class OctaveShift(BaseModel):
    class Meta:
        name = "octave-shift"

    model_config = ConfigDict(defer_build=True)
    type_value: UpDownStopContinue = field(
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        }
    )
    number: int | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 1,
            "max_inclusive": 16,
        },
    )
    size: int = field(
        default=8,
        metadata={
            "type": "Attribute",
        },
    )
    dash_length: Decimal | None = field(
        default=None,
        metadata={
            "name": "dash-length",
            "type": "Attribute",
        },
    )
    space_length: Decimal | None = field(
        default=None,
        metadata={
            "name": "space-length",
            "type": "Attribute",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Offset(BaseModel):
    class Meta:
        name = "offset"

    model_config = ConfigDict(defer_build=True)
    value: Decimal = field(
        metadata={
            "required": True,
        }
    )
    sound: YesNo | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Opus(BaseModel):
    class Meta:
        name = "opus"

    model_config = ConfigDict(defer_build=True)
    href: str = field(
        metadata={
            "type": "Attribute",
            "namespace": XLINK_NS,
            "required": True,
        }
    )
    type_value: TypeValue = field(
        const=True,
        default=TypeValue.SIMPLE,
        metadata={
            "name": "type",
            "type": "Attribute",
            "namespace": XLINK_NS,
        },
    )
    role: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "namespace": XLINK_NS,
        },
    )
    title: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "namespace": XLINK_NS,
        },
    )
    show: ShowValue = field(
        default=ShowValue.REPLACE,
        metadata={
            "type": "Attribute",
            "namespace": XLINK_NS,
        },
    )
    actuate: ActuateValue = field(
        default=ActuateValue.ON_REQUEST,
        metadata={
            "type": "Attribute",
            "namespace": XLINK_NS,
        },
    )


class OtherDirection(BaseModel):
    class Meta:
        name = "other-direction"

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    print_object: YesNo | None = field(
        default=None,
        metadata={
            "name": "print-object",
            "type": "Attribute",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    halign: LeftCenterRight | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    valign: Valign | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    smufl: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class OtherNotation(BaseModel):
    class Meta:
        name = "other-notation"

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    type_value: StartStopSingle = field(
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        }
    )
    number: int = field(
        default=1,
        metadata={
            "type": "Attribute",
            "min_inclusive": 1,
            "max_inclusive": 16,
        },
    )
    print_object: YesNo | None = field(
        default=None,
        metadata={
            "name": "print-object",
            "type": "Attribute",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    placement: AboveBelow | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    smufl: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class OtherPlacementText(BaseModel):
    class Meta:
        name = "other-placement-text"

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    placement: AboveBelow | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    smufl: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class PageMargins(BaseModel):
    class Meta:
        name = "page-margins"

    model_config = ConfigDict(defer_build=True)
    left_margin: Decimal = field(
        metadata={
            "name": "left-margin",
            "type": "Element",
            "required": True,
        }
    )
    right_margin: Decimal = field(
        metadata={
            "name": "right-margin",
            "type": "Element",
            "required": True,
        }
    )
    top_margin: Decimal = field(
        metadata={
            "name": "top-margin",
            "type": "Element",
            "required": True,
        }
    )
    bottom_margin: Decimal = field(
        metadata={
            "name": "bottom-margin",
            "type": "Element",
            "required": True,
        }
    )
    type_value: MarginType | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
        },
    )


class PartClef(BaseModel):
    class Meta:
        name = "part-clef"

    model_config = ConfigDict(defer_build=True)
    sign: ClefSign = field(
        metadata={
            "type": "Element",
            "required": True,
        }
    )
    line: int | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    clef_octave_change: int | None = field(
        default=None,
        metadata={
            "name": "clef-octave-change",
            "type": "Element",
        },
    )


class PartLink(BaseModel):
    class Meta:
        name = "part-link"

    model_config = ConfigDict(defer_build=True)
    instrument_link: list[InstrumentLink] = field(
        default_factory=list,
        metadata={
            "name": "instrument-link",
            "type": "Element",
        },
    )
    group_link: list[str] = field(
        default_factory=list,
        metadata={
            "name": "group-link",
            "type": "Element",
        },
    )
    href: str = field(
        metadata={
            "type": "Attribute",
            "namespace": XLINK_NS,
            "required": True,
        }
    )
    type_value: TypeValue = field(
        const=True,
        default=TypeValue.SIMPLE,
        metadata={
            "name": "type",
            "type": "Attribute",
            "namespace": XLINK_NS,
        },
    )
    role: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "namespace": XLINK_NS,
        },
    )
    title: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "namespace": XLINK_NS,
        },
    )
    show: ShowValue = field(
        default=ShowValue.REPLACE,
        metadata={
            "type": "Attribute",
            "namespace": XLINK_NS,
        },
    )
    actuate: ActuateValue = field(
        default=ActuateValue.ON_REQUEST,
        metadata={
            "type": "Attribute",
            "namespace": XLINK_NS,
        },
    )


class PartName(BaseModel):
    class Meta:
        name = "part-name"

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    print_object: YesNo | None = field(
        default=None,
        metadata={
            "name": "print-object",
            "type": "Attribute",
        },
    )
    justify: LeftCenterRight | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class PartSymbol(BaseModel):
    class Meta:
        name = "part-symbol"

    model_config = ConfigDict(defer_build=True)
    value: GroupSymbolValue = field(
        metadata={
            "required": True,
        }
    )
    top_staff: int | None = field(
        default=None,
        metadata={
            "name": "top-staff",
            "type": "Attribute",
        },
    )
    bottom_staff: int | None = field(
        default=None,
        metadata={
            "name": "bottom-staff",
            "type": "Attribute",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class Pedal(BaseModel):
    class Meta:
        name = "pedal"

    model_config = ConfigDict(defer_build=True)
    type_value: PedalType = field(
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        }
    )
    number: int | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 1,
            "max_inclusive": 16,
        },
    )
    line: YesNo | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    sign: YesNo | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    abbreviated: YesNo | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    halign: LeftCenterRight | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    valign: Valign | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class PedalTuning(BaseModel):
    class Meta:
        name = "pedal-tuning"

    model_config = ConfigDict(defer_build=True)
    pedal_step: Step = field(
        metadata={
            "name": "pedal-step",
            "type": "Element",
            "required": True,
        }
    )
    pedal_alter: Decimal = field(
        metadata={
            "name": "pedal-alter",
            "type": "Element",
            "required": True,
        }
    )


class PerMinute(BaseModel):
    class Meta:
        name = "per-minute"

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )


class Pitch(BaseModel):
    class Meta:
        name = "pitch"

    model_config = ConfigDict(defer_build=True)
    step: Step = field(
        metadata={
            "type": "Element",
            "required": True,
        }
    )
    alter: Decimal | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    octave: int = field(
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 9,
        }
    )


class Pitched(BaseModel):
    class Meta:
        name = "pitched"

    model_config = ConfigDict(defer_build=True)
    value: PitchedValue = field(
        metadata={
            "required": True,
        }
    )
    smufl: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"pict\c+",
        },
    )


class PlacementText(BaseModel):
    class Meta:
        name = "placement-text"

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    placement: AboveBelow | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Play(BaseModel):
    class Meta:
        name = "play"

    model_config = ConfigDict(defer_build=True)
    ipa: list[str] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    mute: list[Mute] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    semi_pitched: list[SemiPitched] = field(
        default_factory=list,
        metadata={
            "name": "semi-pitched",
            "type": "Element",
        },
    )
    other_play: list[OtherPlay] = field(
        default_factory=list,
        metadata={
            "name": "other-play",
            "type": "Element",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class PrincipalVoice(BaseModel):
    class Meta:
        name = "principal-voice"

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    type_value: StartStop = field(
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        }
    )
    symbol: PrincipalVoiceSymbol = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    halign: LeftCenterRight | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    valign: Valign | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Release(Empty):
    class Meta:
        name = "release"

    model_config = ConfigDict(defer_build=True)
    offset: Decimal | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Repeat(BaseModel):
    class Meta:
        name = "repeat"

    model_config = ConfigDict(defer_build=True)
    direction: BackwardForward = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    times: int | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    after_jump: YesNo | None = field(
        default=None,
        metadata={
            "name": "after-jump",
            "type": "Attribute",
        },
    )
    winged: Winged | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Rest(BaseModel):
    class Meta:
        name = "rest"

    model_config = ConfigDict(defer_build=True)
    display_step: Step | None = field(
        default=None,
        metadata={
            "name": "display-step",
            "type": "Element",
        },
    )
    display_octave: int | None = field(
        default=None,
        metadata={
            "name": "display-octave",
            "type": "Element",
            "min_inclusive": 0,
            "max_inclusive": 9,
        },
    )
    measure: YesNo | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class RootStep(BaseModel):
    class Meta:
        name = "root-step"

    model_config = ConfigDict(defer_build=True)
    value: Step = field(
        metadata={
            "required": True,
        }
    )
    text: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class ScoreInstrument(BaseModel):
    class Meta:
        name = "score-instrument"

    model_config = ConfigDict(defer_build=True)
    instrument_name: str = field(
        metadata={
            "name": "instrument-name",
            "type": "Element",
            "required": True,
        }
    )
    instrument_abbreviation: str | None = field(
        default=None,
        metadata={
            "name": "instrument-abbreviation",
            "type": "Element",
        },
    )
    instrument_sound: str | None = field(
        default=None,
        metadata={
            "name": "instrument-sound",
            "type": "Element",
        },
    )
    solo: Empty | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    ensemble: int | PositiveIntegerOrEmptyValue | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    virtual_instrument: VirtualInstrument | None = field(
        default=None,
        metadata={
            "name": "virtual-instrument",
            "type": "Element",
        },
    )
    id: str = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )


class Segno(BaseModel):
    class Meta:
        name = "segno"

    model_config = ConfigDict(defer_build=True)
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    halign: LeftCenterRight | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    valign: Valign | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    smufl: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"segno\c*",
        },
    )


class Slash(BaseModel):
    class Meta:
        name = "slash"

    model_config = ConfigDict(defer_build=True)
    slash_type: NoteTypeValue | None = field(
        default=None,
        metadata={
            "name": "slash-type",
            "type": "Element",
        },
    )
    slash_dot: list[Empty] = field(
        default_factory=list,
        metadata={
            "name": "slash-dot",
            "type": "Element",
        },
    )
    except_voice: list[str] = field(
        default_factory=list,
        metadata={
            "name": "except-voice",
            "type": "Element",
        },
    )
    type_value: StartStop = field(
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        }
    )
    use_dots: YesNo | None = field(
        default=None,
        metadata={
            "name": "use-dots",
            "type": "Attribute",
        },
    )
    use_stems: YesNo | None = field(
        default=None,
        metadata={
            "name": "use-stems",
            "type": "Attribute",
        },
    )


class Slide(BaseModel):
    class Meta:
        name = "slide"

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    type_value: StartStop = field(
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        }
    )
    number: int = field(
        default=1,
        metadata={
            "type": "Attribute",
            "min_inclusive": 1,
            "max_inclusive": 16,
        },
    )
    line_type: LineType | None = field(
        default=None,
        metadata={
            "name": "line-type",
            "type": "Attribute",
        },
    )
    dash_length: Decimal | None = field(
        default=None,
        metadata={
            "name": "dash-length",
            "type": "Attribute",
        },
    )
    space_length: Decimal | None = field(
        default=None,
        metadata={
            "name": "space-length",
            "type": "Attribute",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    accelerate: YesNo | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    beats: Decimal | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": Decimal("2"),
        },
    )
    first_beat: Decimal | None = field(
        default=None,
        metadata={
            "name": "first-beat",
            "type": "Attribute",
            "min_inclusive": Decimal("0"),
            "max_inclusive": Decimal("100"),
        },
    )
    last_beat: Decimal | None = field(
        default=None,
        metadata={
            "name": "last-beat",
            "type": "Attribute",
            "min_inclusive": Decimal("0"),
            "max_inclusive": Decimal("100"),
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Slur(BaseModel):
    class Meta:
        name = "slur"

    model_config = ConfigDict(defer_build=True)
    type_value: StartStopContinue = field(
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        }
    )
    number: int = field(
        default=1,
        metadata={
            "type": "Attribute",
            "min_inclusive": 1,
            "max_inclusive": 16,
        },
    )
    line_type: LineType | None = field(
        default=None,
        metadata={
            "name": "line-type",
            "type": "Attribute",
        },
    )
    dash_length: Decimal | None = field(
        default=None,
        metadata={
            "name": "dash-length",
            "type": "Attribute",
        },
    )
    space_length: Decimal | None = field(
        default=None,
        metadata={
            "name": "space-length",
            "type": "Attribute",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    placement: AboveBelow | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    orientation: OverUnder | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    bezier_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "bezier-x",
            "type": "Attribute",
        },
    )
    bezier_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "bezier-y",
            "type": "Attribute",
        },
    )
    bezier_x2: Decimal | None = field(
        default=None,
        metadata={
            "name": "bezier-x2",
            "type": "Attribute",
        },
    )
    bezier_y2: Decimal | None = field(
        default=None,
        metadata={
            "name": "bezier-y2",
            "type": "Attribute",
        },
    )
    bezier_offset: Decimal | None = field(
        default=None,
        metadata={
            "name": "bezier-offset",
            "type": "Attribute",
        },
    )
    bezier_offset2: Decimal | None = field(
        default=None,
        metadata={
            "name": "bezier-offset2",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class StaffDivide(BaseModel):
    class Meta:
        name = "staff-divide"

    model_config = ConfigDict(defer_build=True)
    type_value: StaffDivideSymbol = field(
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        }
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    halign: LeftCenterRight | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    valign: Valign | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class StaffTuning(BaseModel):
    class Meta:
        name = "staff-tuning"

    model_config = ConfigDict(defer_build=True)
    tuning_step: Step = field(
        metadata={
            "name": "tuning-step",
            "type": "Element",
            "required": True,
        }
    )
    tuning_alter: Decimal | None = field(
        default=None,
        metadata={
            "name": "tuning-alter",
            "type": "Element",
        },
    )
    tuning_octave: int = field(
        metadata={
            "name": "tuning-octave",
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 9,
        }
    )
    line: int = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )


class Stem(BaseModel):
    class Meta:
        name = "stem"

    model_config = ConfigDict(defer_build=True)
    value: StemValue = field(
        metadata={
            "required": True,
        }
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class Stick(BaseModel):
    class Meta:
        name = "stick"

    model_config = ConfigDict(defer_build=True)
    stick_type: StickType = field(
        metadata={
            "name": "stick-type",
            "type": "Element",
            "required": True,
        }
    )
    stick_material: StickMaterial = field(
        metadata={
            "name": "stick-material",
            "type": "Element",
            "required": True,
        }
    )
    tip: TipDirection | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    parentheses: YesNo | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    dashed_circle: YesNo | None = field(
        default=None,
        metadata={
            "name": "dashed-circle",
            "type": "Attribute",
        },
    )


class String(BaseModel):
    class Meta:
        name = "string"

    model_config = ConfigDict(defer_build=True)
    value: int = field(
        metadata={
            "required": True,
        }
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    placement: AboveBelow | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class StringMute(BaseModel):
    class Meta:
        name = "string-mute"

    model_config = ConfigDict(defer_build=True)
    type_value: OnOff = field(
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        }
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    halign: LeftCenterRight | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    valign: Valign | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class StyleText(BaseModel):
    class Meta:
        name = "style-text"

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class Supports(BaseModel):
    class Meta:
        name = "supports"

    model_config = ConfigDict(defer_build=True)
    type_value: YesNo = field(
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        }
    )
    element: str = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    attribute: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    value: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Swing(BaseModel):
    class Meta:
        name = "swing"

    model_config = ConfigDict(defer_build=True)
    straight: Empty | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    first: int | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    second: int | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    swing_type: SwingTypeValue | None = field(
        default=None,
        metadata={
            "name": "swing-type",
            "type": "Element",
        },
    )
    swing_style: str | None = field(
        default=None,
        metadata={
            "name": "swing-style",
            "type": "Element",
        },
    )


class Sync(BaseModel):
    class Meta:
        name = "sync"

    model_config = ConfigDict(defer_build=True)
    type_value: SyncType = field(
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        }
    )
    latency: int | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    player: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    time_only: str | None = field(
        default=None,
        metadata={
            "name": "time-only",
            "type": "Attribute",
            "pattern": r"[1-9][0-9]*(, ?[1-9][0-9]*)*",
        },
    )


class Tap(BaseModel):
    class Meta:
        name = "tap"

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    hand: TapHand | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    placement: AboveBelow | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class TextElementData(BaseModel):
    class Meta:
        name = "text-element-data"

    model_config = ConfigDict(defer_build=True)
    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    underline: int | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 3,
        },
    )
    overline: int | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 3,
        },
    )
    line_through: int | None = field(
        default=None,
        metadata={
            "name": "line-through",
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 3,
        },
    )
    rotation: Decimal | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": Decimal("-180"),
            "max_inclusive": Decimal("180"),
        },
    )
    letter_spacing: Decimal | NumberOrNormalValue | None = field(
        default=None,
        metadata={
            "name": "letter-spacing",
            "type": "Attribute",
        },
    )
    lang: str | LangValue | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "namespace": XML_NS,
        },
    )
    dir: TextDirection | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Tie(BaseModel):
    class Meta:
        name = "tie"

    model_config = ConfigDict(defer_build=True)
    type_value: StartStop = field(
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        }
    )
    time_only: str | None = field(
        default=None,
        metadata={
            "name": "time-only",
            "type": "Attribute",
            "pattern": r"[1-9][0-9]*(, ?[1-9][0-9]*)*",
        },
    )


class Tied(BaseModel):
    class Meta:
        name = "tied"

    model_config = ConfigDict(defer_build=True)
    type_value: TiedType = field(
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        }
    )
    number: int | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 1,
            "max_inclusive": 16,
        },
    )
    line_type: LineType | None = field(
        default=None,
        metadata={
            "name": "line-type",
            "type": "Attribute",
        },
    )
    dash_length: Decimal | None = field(
        default=None,
        metadata={
            "name": "dash-length",
            "type": "Attribute",
        },
    )
    space_length: Decimal | None = field(
        default=None,
        metadata={
            "name": "space-length",
            "type": "Attribute",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    placement: AboveBelow | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    orientation: OverUnder | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    bezier_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "bezier-x",
            "type": "Attribute",
        },
    )
    bezier_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "bezier-y",
            "type": "Attribute",
        },
    )
    bezier_x2: Decimal | None = field(
        default=None,
        metadata={
            "name": "bezier-x2",
            "type": "Attribute",
        },
    )
    bezier_y2: Decimal | None = field(
        default=None,
        metadata={
            "name": "bezier-y2",
            "type": "Attribute",
        },
    )
    bezier_offset: Decimal | None = field(
        default=None,
        metadata={
            "name": "bezier-offset",
            "type": "Attribute",
        },
    )
    bezier_offset2: Decimal | None = field(
        default=None,
        metadata={
            "name": "bezier-offset2",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class TimeModification(BaseModel):
    class Meta:
        name = "time-modification"

    model_config = ConfigDict(defer_build=True)
    actual_notes: int = field(
        metadata={
            "name": "actual-notes",
            "type": "Element",
            "required": True,
        }
    )
    normal_notes: int = field(
        metadata={
            "name": "normal-notes",
            "type": "Element",
            "required": True,
        }
    )
    normal_type: NoteTypeValue | None = field(
        default=None,
        metadata={
            "name": "normal-type",
            "type": "Element",
        },
    )
    normal_dot: list[Empty] = field(
        default_factory=list,
        metadata={
            "name": "normal-dot",
            "type": "Element",
        },
    )


class Tremolo(BaseModel):
    class Meta:
        name = "tremolo"

    model_config = ConfigDict(defer_build=True)
    value: int = field(
        metadata={
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 8,
        }
    )
    type_value: TremoloType = field(
        default=TremoloType.SINGLE,
        metadata={
            "name": "type",
            "type": "Attribute",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    placement: AboveBelow | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    smufl: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class TupletDot(BaseModel):
    class Meta:
        name = "tuplet-dot"

    model_config = ConfigDict(defer_build=True)
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class TupletNumber(BaseModel):
    class Meta:
        name = "tuplet-number"

    model_config = ConfigDict(defer_build=True)
    value: int = field(
        metadata={
            "required": True,
        }
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class TupletType(BaseModel):
    class Meta:
        name = "tuplet-type"

    model_config = ConfigDict(defer_build=True)
    value: NoteTypeValue = field(
        metadata={
            "required": True,
        }
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class Unpitched(BaseModel):
    class Meta:
        name = "unpitched"

    model_config = ConfigDict(defer_build=True)
    display_step: Step | None = field(
        default=None,
        metadata={
            "name": "display-step",
            "type": "Element",
        },
    )
    display_octave: int | None = field(
        default=None,
        metadata={
            "name": "display-octave",
            "type": "Element",
            "min_inclusive": 0,
            "max_inclusive": 9,
        },
    )


class WavyLine(BaseModel):
    class Meta:
        name = "wavy-line"

    model_config = ConfigDict(defer_build=True)
    type_value: StartStopContinue = field(
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        }
    )
    number: int | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 1,
            "max_inclusive": 16,
        },
    )
    smufl: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"(wiggle\c+)|(guitar\c*VibratoStroke)",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    placement: AboveBelow | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    start_note: StartNote | None = field(
        default=None,
        metadata={
            "name": "start-note",
            "type": "Attribute",
        },
    )
    trill_step: TrillStep | None = field(
        default=None,
        metadata={
            "name": "trill-step",
            "type": "Attribute",
        },
    )
    two_note_turn: TwoNoteTurn | None = field(
        default=None,
        metadata={
            "name": "two-note-turn",
            "type": "Attribute",
        },
    )
    accelerate: YesNo | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    beats: Decimal | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": Decimal("2"),
        },
    )
    second_beat: Decimal | None = field(
        default=None,
        metadata={
            "name": "second-beat",
            "type": "Attribute",
            "min_inclusive": Decimal("0"),
            "max_inclusive": Decimal("100"),
        },
    )
    last_beat: Decimal | None = field(
        default=None,
        metadata={
            "name": "last-beat",
            "type": "Attribute",
            "min_inclusive": Decimal("0"),
            "max_inclusive": Decimal("100"),
        },
    )


class Wedge(BaseModel):
    class Meta:
        name = "wedge"

    model_config = ConfigDict(defer_build=True)
    type_value: WedgeType = field(
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        }
    )
    number: int | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 1,
            "max_inclusive": 16,
        },
    )
    spread: Decimal | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    niente: YesNo | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    line_type: LineType | None = field(
        default=None,
        metadata={
            "name": "line-type",
            "type": "Attribute",
        },
    )
    dash_length: Decimal | None = field(
        default=None,
        metadata={
            "name": "dash-length",
            "type": "Attribute",
        },
    )
    space_length: Decimal | None = field(
        default=None,
        metadata={
            "name": "space-length",
            "type": "Attribute",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Wood(BaseModel):
    class Meta:
        name = "wood"

    model_config = ConfigDict(defer_build=True)
    value: WoodValue = field(
        metadata={
            "required": True,
        }
    )
    smufl: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"pict\c+",
        },
    )


class LineWidth(BaseModel):
    class Meta:
        name = "line-width"

    model_config = ConfigDict(defer_build=True)
    value: Decimal = field(
        metadata={
            "required": True,
        }
    )
    type_value: str = field(
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        }
    )


class Appearance(BaseModel):
    class Meta:
        name = "appearance"

    model_config = ConfigDict(defer_build=True)
    line_width: list[LineWidth] = field(
        default_factory=list,
        metadata={
            "name": "line-width",
            "type": "Element",
        },
    )
    note_size: list[NoteSize] = field(
        default_factory=list,
        metadata={
            "name": "note-size",
            "type": "Element",
        },
    )
    distance: list[Distance] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    glyph: list[Glyph] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    other_appearance: list[OtherAppearance] = field(
        default_factory=list,
        metadata={
            "name": "other-appearance",
            "type": "Element",
        },
    )


class Backup(BaseModel):
    class Meta:
        name = "backup"

    model_config = ConfigDict(defer_build=True)
    duration: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
            "min_exclusive": Decimal("0"),
        }
    )
    footnote: FormattedText | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    level: Level | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )


class Barline(BaseModel):
    class Meta:
        name = "barline"

    model_config = ConfigDict(defer_build=True)
    bar_style: BarStyleColor | None = field(
        default=None,
        metadata={
            "name": "bar-style",
            "type": "Element",
        },
    )
    footnote: FormattedText | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    level: Level | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    wavy_line: WavyLine | None = field(
        default=None,
        metadata={
            "name": "wavy-line",
            "type": "Element",
        },
    )
    segno: Segno | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    coda: Coda | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    fermata: list[Fermata] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "max_occurs": 2,
        },
    )
    ending: Ending | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    repeat: Repeat | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    location: RightLeftMiddle = field(
        default=RightLeftMiddle.RIGHT,
        metadata={
            "type": "Attribute",
        },
    )
    segno_attribute: str | None = field(
        default=None,
        metadata={
            "name": "segno",
            "type": "Attribute",
        },
    )
    coda_attribute: str | None = field(
        default=None,
        metadata={
            "name": "coda",
            "type": "Attribute",
        },
    )
    divisions: Decimal | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Bass(BaseModel):
    class Meta:
        name = "bass"

    model_config = ConfigDict(defer_build=True)
    bass_separator: StyleText | None = field(
        default=None,
        metadata={
            "name": "bass-separator",
            "type": "Element",
        },
    )
    bass_step: BassStep = field(
        metadata={
            "name": "bass-step",
            "type": "Element",
            "required": True,
        }
    )
    bass_alter: HarmonyAlter | None = field(
        default=None,
        metadata={
            "name": "bass-alter",
            "type": "Element",
        },
    )
    arrangement: HarmonyArrangement | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Bend(BaseModel):
    class Meta:
        name = "bend"

    model_config = ConfigDict(defer_build=True)
    bend_alter: Decimal = field(
        metadata={
            "name": "bend-alter",
            "type": "Element",
            "required": True,
        }
    )
    pre_bend: Empty | None = field(
        default=None,
        metadata={
            "name": "pre-bend",
            "type": "Element",
        },
    )
    release: Release | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    with_bar: PlacementText | None = field(
        default=None,
        metadata={
            "name": "with-bar",
            "type": "Element",
        },
    )
    shape: BendShape | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    accelerate: YesNo | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    beats: Decimal | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": Decimal("2"),
        },
    )
    first_beat: Decimal | None = field(
        default=None,
        metadata={
            "name": "first-beat",
            "type": "Attribute",
            "min_inclusive": Decimal("0"),
            "max_inclusive": Decimal("100"),
        },
    )
    last_beat: Decimal | None = field(
        default=None,
        metadata={
            "name": "last-beat",
            "type": "Attribute",
            "min_inclusive": Decimal("0"),
            "max_inclusive": Decimal("100"),
        },
    )


class Credit(BaseModel):
    class Meta:
        name = "credit"

    model_config = ConfigDict(defer_build=True)
    credit_type: list[str] = field(
        default_factory=list,
        metadata={
            "name": "credit-type",
            "type": "Element",
        },
    )
    link: list[Link] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    bookmark: list[Bookmark] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    credit_image: Image | None = field(
        default=None,
        metadata={
            "name": "credit-image",
            "type": "Element",
        },
    )
    credit_words: list[FormattedTextId] = field(
        default_factory=list,
        metadata={
            "name": "credit-words",
            "type": "Element",
        },
    )
    credit_symbol: list[FormattedSymbolId] = field(
        default_factory=list,
        metadata={
            "name": "credit-symbol",
            "type": "Element",
        },
    )
    page: int | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Degree(BaseModel):
    class Meta:
        name = "degree"

    model_config = ConfigDict(defer_build=True)
    degree_value: DegreeValue = field(
        metadata={
            "name": "degree-value",
            "type": "Element",
            "required": True,
        }
    )
    degree_alter: DegreeAlter = field(
        metadata={
            "name": "degree-alter",
            "type": "Element",
            "required": True,
        }
    )
    degree_type: DegreeType = field(
        metadata={
            "name": "degree-type",
            "type": "Element",
            "required": True,
        }
    )
    print_object: YesNo | None = field(
        default=None,
        metadata={
            "name": "print-object",
            "type": "Attribute",
        },
    )


class Encoding(BaseModel):
    class Meta:
        name = "encoding"

    model_config = ConfigDict(defer_build=True)
    encoding_date: list[str] = field(
        default_factory=list,
        metadata={
            "name": "encoding-date",
            "type": "Element",
            "pattern": r"[^:Z]*",
        },
    )
    encoder: list[TypedText] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    software: list[str] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    encoding_description: list[str] = field(
        default_factory=list,
        metadata={
            "name": "encoding-description",
            "type": "Element",
        },
    )
    supports: list[Supports] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )


class Figure(BaseModel):
    class Meta:
        name = "figure"

    model_config = ConfigDict(defer_build=True)
    prefix: StyleText | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    figure_number: StyleText | None = field(
        default=None,
        metadata={
            "name": "figure-number",
            "type": "Element",
        },
    )
    suffix: StyleText | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    extend: Extend | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    footnote: FormattedText | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    level: Level | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )


class Forward(BaseModel):
    class Meta:
        name = "forward"

    model_config = ConfigDict(defer_build=True)
    duration: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
            "min_exclusive": Decimal("0"),
        }
    )
    footnote: FormattedText | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    level: Level | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    voice: str | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    staff: int | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )


class FrameNote(BaseModel):
    class Meta:
        name = "frame-note"

    model_config = ConfigDict(defer_build=True)
    string: String = field(
        metadata={
            "type": "Element",
            "required": True,
        }
    )
    fret: Fret = field(
        metadata={
            "type": "Element",
            "required": True,
        }
    )
    fingering: Fingering | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    barre: Barre | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )


class HarmonMute(BaseModel):
    class Meta:
        name = "harmon-mute"

    model_config = ConfigDict(defer_build=True)
    harmon_closed: HarmonClosed = field(
        metadata={
            "name": "harmon-closed",
            "type": "Element",
            "required": True,
        }
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    placement: AboveBelow | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class HarpPedals(BaseModel):
    class Meta:
        name = "harp-pedals"

    model_config = ConfigDict(defer_build=True)
    pedal_tuning: list[PedalTuning] = field(
        default_factory=list,
        metadata={
            "name": "pedal-tuning",
            "type": "Element",
            "min_occurs": 1,
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    halign: LeftCenterRight | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    valign: Valign | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class HeelToe(EmptyPlacement):
    class Meta:
        name = "heel-toe"

    model_config = ConfigDict(defer_build=True)
    substitution: YesNo | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Hole(BaseModel):
    class Meta:
        name = "hole"

    model_config = ConfigDict(defer_build=True)
    hole_type: str | None = field(
        default=None,
        metadata={
            "name": "hole-type",
            "type": "Element",
        },
    )
    hole_closed: HoleClosed = field(
        metadata={
            "name": "hole-closed",
            "type": "Element",
            "required": True,
        }
    )
    hole_shape: str | None = field(
        default=None,
        metadata={
            "name": "hole-shape",
            "type": "Element",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    placement: AboveBelow | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Key(BaseModel):
    class Meta:
        name = "key"

    model_config = ConfigDict(defer_build=True)
    cancel: Cancel | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    fifths: int | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    mode: str | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    key_step: list[Step] = field(
        default_factory=list,
        metadata={
            "name": "key-step",
            "type": "Element",
        },
    )
    key_alter: list[Decimal] = field(
        default_factory=list,
        metadata={
            "name": "key-alter",
            "type": "Element",
        },
    )
    key_accidental: list[KeyAccidental] = field(
        default_factory=list,
        metadata={
            "name": "key-accidental",
            "type": "Element",
        },
    )
    key_octave: list[KeyOctave] = field(
        default_factory=list,
        metadata={
            "name": "key-octave",
            "type": "Element",
        },
    )
    number: int | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    print_object: YesNo | None = field(
        default=None,
        metadata={
            "name": "print-object",
            "type": "Attribute",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Listen(BaseModel):
    class Meta:
        name = "listen"

    model_config = ConfigDict(defer_build=True)
    assess: list[Assess] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    wait: list[Wait] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    other_listen: list[OtherListening] = field(
        default_factory=list,
        metadata={
            "name": "other-listen",
            "type": "Element",
        },
    )


class Listening(BaseModel):
    class Meta:
        name = "listening"

    model_config = ConfigDict(defer_build=True)
    sync: list[Sync] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    other_listening: list[OtherListening] = field(
        default_factory=list,
        metadata={
            "name": "other-listening",
            "type": "Element",
        },
    )
    offset: Offset | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )


class Lyric(BaseModel):
    class Meta:
        name = "lyric"

    model_config = ConfigDict(defer_build=True)
    syllabic: list[Syllabic] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    text: list[TextElementData] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    elision: list[Elision] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    extend: list[Extend] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
            "max_occurs": 2,
            "sequence": 1,
        },
    )
    laughing: Empty | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    humming: Empty | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    end_line: Empty | None = field(
        default=None,
        metadata={
            "name": "end-line",
            "type": "Element",
        },
    )
    end_paragraph: Empty | None = field(
        default=None,
        metadata={
            "name": "end-paragraph",
            "type": "Element",
        },
    )
    footnote: FormattedText | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    level: Level | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    number: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    name: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    justify: LeftCenterRight | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    placement: AboveBelow | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    print_object: YesNo | None = field(
        default=None,
        metadata={
            "name": "print-object",
            "type": "Attribute",
        },
    )
    time_only: str | None = field(
        default=None,
        metadata={
            "name": "time-only",
            "type": "Attribute",
            "pattern": r"[1-9][0-9]*(, ?[1-9][0-9]*)*",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class MeasureStyle(BaseModel):
    class Meta:
        name = "measure-style"

    model_config = ConfigDict(defer_build=True)
    multiple_rest: MultipleRest | None = field(
        default=None,
        metadata={
            "name": "multiple-rest",
            "type": "Element",
        },
    )
    measure_repeat: MeasureRepeat | None = field(
        default=None,
        metadata={
            "name": "measure-repeat",
            "type": "Element",
        },
    )
    beat_repeat: BeatRepeat | None = field(
        default=None,
        metadata={
            "name": "beat-repeat",
            "type": "Element",
        },
    )
    slash: Slash | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    number: int | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class MetronomeTuplet(TimeModification):
    class Meta:
        name = "metronome-tuplet"

    model_config = ConfigDict(defer_build=True)
    type_value: StartStop = field(
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        }
    )
    bracket: YesNo | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    show_number: ShowTuplet | None = field(
        default=None,
        metadata={
            "name": "show-number",
            "type": "Attribute",
        },
    )


class Mordent(EmptyTrillSound):
    class Meta:
        name = "mordent"

    model_config = ConfigDict(defer_build=True)
    long: YesNo | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    approach: AboveBelow | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    departure: AboveBelow | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class NameDisplay(BaseModel):
    class Meta:
        name = "name-display"

    model_config = ConfigDict(defer_build=True)
    display_text: list[FormattedText] = field(
        default_factory=list,
        metadata={
            "name": "display-text",
            "type": "Element",
        },
    )
    accidental_text: list[AccidentalText] = field(
        default_factory=list,
        metadata={
            "name": "accidental-text",
            "type": "Element",
        },
    )
    print_object: YesNo | None = field(
        default=None,
        metadata={
            "name": "print-object",
            "type": "Attribute",
        },
    )


class NoteheadText(BaseModel):
    class Meta:
        name = "notehead-text"

    model_config = ConfigDict(defer_build=True)
    display_text: list[FormattedText] = field(
        default_factory=list,
        metadata={
            "name": "display-text",
            "type": "Element",
        },
    )
    accidental_text: list[AccidentalText] = field(
        default_factory=list,
        metadata={
            "name": "accidental-text",
            "type": "Element",
        },
    )


class Numeral(BaseModel):
    class Meta:
        name = "numeral"

    model_config = ConfigDict(defer_build=True)
    numeral_root: NumeralRoot = field(
        metadata={
            "name": "numeral-root",
            "type": "Element",
            "required": True,
        }
    )
    numeral_alter: HarmonyAlter | None = field(
        default=None,
        metadata={
            "name": "numeral-alter",
            "type": "Element",
        },
    )
    numeral_key: NumeralKey | None = field(
        default=None,
        metadata={
            "name": "numeral-key",
            "type": "Element",
        },
    )


class PageLayout(BaseModel):
    class Meta:
        name = "page-layout"

    model_config = ConfigDict(defer_build=True)
    page_height: Decimal | None = field(
        default=None,
        metadata={
            "name": "page-height",
            "type": "Element",
        },
    )
    page_width: Decimal | None = field(
        default=None,
        metadata={
            "name": "page-width",
            "type": "Element",
        },
    )
    page_margins: list[PageMargins] = field(
        default_factory=list,
        metadata={
            "name": "page-margins",
            "type": "Element",
            "max_occurs": 2,
        },
    )


class PartTranspose(BaseModel):
    class Meta:
        name = "part-transpose"

    model_config = ConfigDict(defer_build=True)
    diatonic: int | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    chromatic: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        }
    )
    octave_change: int | None = field(
        default=None,
        metadata={
            "name": "octave-change",
            "type": "Element",
        },
    )
    double: Double | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )


class Percussion(BaseModel):
    class Meta:
        name = "percussion"

    model_config = ConfigDict(defer_build=True)
    glass: Glass | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    metal: Metal | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    wood: Wood | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    pitched: Pitched | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    membrane: Membrane | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    effect: Effect | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    timpani: Timpani | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    beater: Beater | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    stick: Stick | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    stick_location: StickLocation | None = field(
        default=None,
        metadata={
            "name": "stick-location",
            "type": "Element",
        },
    )
    other_percussion: OtherText | None = field(
        default=None,
        metadata={
            "name": "other-percussion",
            "type": "Element",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    halign: LeftCenterRight | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    valign: Valign | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    enclosure: EnclosureShape | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Root(BaseModel):
    class Meta:
        name = "root"

    model_config = ConfigDict(defer_build=True)
    root_step: RootStep = field(
        metadata={
            "name": "root-step",
            "type": "Element",
            "required": True,
        }
    )
    root_alter: HarmonyAlter | None = field(
        default=None,
        metadata={
            "name": "root-alter",
            "type": "Element",
        },
    )


class Scordatura(BaseModel):
    class Meta:
        name = "scordatura"

    model_config = ConfigDict(defer_build=True)
    accord: list[Accord] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Sound(BaseModel):
    class Meta:
        name = "sound"

    model_config = ConfigDict(defer_build=True)
    instrument_change: list[InstrumentChange] = field(
        default_factory=list,
        metadata={
            "name": "instrument-change",
            "type": "Element",
        },
    )
    midi_device: list[MidiDevice] = field(
        default_factory=list,
        metadata={
            "name": "midi-device",
            "type": "Element",
        },
    )
    midi_instrument: list[MidiInstrument] = field(
        default_factory=list,
        metadata={
            "name": "midi-instrument",
            "type": "Element",
        },
    )
    play: list[Play] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    swing: Swing | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    offset: Offset | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    tempo: Decimal | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": Decimal("0"),
        },
    )
    dynamics: Decimal | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": Decimal("0"),
        },
    )
    dacapo: YesNo | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    segno: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    dalsegno: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    coda: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    tocoda: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    divisions: Decimal | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    forward_repeat: YesNo | None = field(
        default=None,
        metadata={
            "name": "forward-repeat",
            "type": "Attribute",
        },
    )
    fine: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    time_only: str | None = field(
        default=None,
        metadata={
            "name": "time-only",
            "type": "Attribute",
            "pattern": r"[1-9][0-9]*(, ?[1-9][0-9]*)*",
        },
    )
    pizzicato: YesNo | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    pan: Decimal | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": Decimal("-180"),
            "max_inclusive": Decimal("180"),
        },
    )
    elevation: Decimal | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": Decimal("-180"),
            "max_inclusive": Decimal("180"),
        },
    )
    damper_pedal: YesNo | Decimal | None = field(
        default=None,
        metadata={
            "name": "damper-pedal",
            "type": "Attribute",
        },
    )
    soft_pedal: YesNo | Decimal | None = field(
        default=None,
        metadata={
            "name": "soft-pedal",
            "type": "Attribute",
        },
    )
    sostenuto_pedal: YesNo | Decimal | None = field(
        default=None,
        metadata={
            "name": "sostenuto-pedal",
            "type": "Attribute",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class StaffDetails(BaseModel):
    class Meta:
        name = "staff-details"

    model_config = ConfigDict(defer_build=True)
    staff_type: StaffType | None = field(
        default=None,
        metadata={
            "name": "staff-type",
            "type": "Element",
        },
    )
    staff_lines: int | None = field(
        default=None,
        metadata={
            "name": "staff-lines",
            "type": "Element",
        },
    )
    line_detail: list[LineDetail] = field(
        default_factory=list,
        metadata={
            "name": "line-detail",
            "type": "Element",
        },
    )
    staff_tuning: list[StaffTuning] = field(
        default_factory=list,
        metadata={
            "name": "staff-tuning",
            "type": "Element",
        },
    )
    capo: int | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    staff_size: StaffSize | None = field(
        default=None,
        metadata={
            "name": "staff-size",
            "type": "Element",
        },
    )
    number: int | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    show_frets: ShowFrets | None = field(
        default=None,
        metadata={
            "name": "show-frets",
            "type": "Attribute",
        },
    )
    print_object: YesNo | None = field(
        default=None,
        metadata={
            "name": "print-object",
            "type": "Attribute",
        },
    )
    print_spacing: YesNo | None = field(
        default=None,
        metadata={
            "name": "print-spacing",
            "type": "Attribute",
        },
    )


class StrongAccent(EmptyPlacement):
    class Meta:
        name = "strong-accent"

    model_config = ConfigDict(defer_build=True)
    type_value: UpDown = field(
        default=UpDown.UP,
        metadata={
            "name": "type",
            "type": "Attribute",
        },
    )


class SystemDividers(BaseModel):
    class Meta:
        name = "system-dividers"

    model_config = ConfigDict(defer_build=True)
    left_divider: EmptyPrintObjectStyleAlign = field(
        metadata={
            "name": "left-divider",
            "type": "Element",
            "required": True,
        }
    )
    right_divider: EmptyPrintObjectStyleAlign = field(
        metadata={
            "name": "right-divider",
            "type": "Element",
            "required": True,
        }
    )


class Time(BaseModel):
    class Meta:
        name = "time"

    model_config = ConfigDict(defer_build=True)
    beats: list[str] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    beat_type: list[str] = field(
        default_factory=list,
        metadata={
            "name": "beat-type",
            "type": "Element",
        },
    )
    interchangeable: Interchangeable | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    senza_misura: str | None = field(
        default=None,
        metadata={
            "name": "senza-misura",
            "type": "Element",
        },
    )
    number: int | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    symbol: TimeSymbol | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    separator: TimeSeparator | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    halign: LeftCenterRight | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    valign: Valign | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    print_object: YesNo | None = field(
        default=None,
        metadata={
            "name": "print-object",
            "type": "Attribute",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Transpose(BaseModel):
    class Meta:
        name = "transpose"

    model_config = ConfigDict(defer_build=True)
    diatonic: int | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    chromatic: Decimal = field(
        metadata={
            "type": "Element",
            "required": True,
        }
    )
    octave_change: int | None = field(
        default=None,
        metadata={
            "name": "octave-change",
            "type": "Element",
        },
    )
    double: Double | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    number: int | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class TupletPortion(BaseModel):
    class Meta:
        name = "tuplet-portion"

    model_config = ConfigDict(defer_build=True)
    tuplet_number: TupletNumber | None = field(
        default=None,
        metadata={
            "name": "tuplet-number",
            "type": "Element",
        },
    )
    tuplet_type: TupletType | None = field(
        default=None,
        metadata={
            "name": "tuplet-type",
            "type": "Element",
        },
    )
    tuplet_dot: list[TupletDot] = field(
        default_factory=list,
        metadata={
            "name": "tuplet-dot",
            "type": "Element",
        },
    )


class Work(BaseModel):
    class Meta:
        name = "work"

    model_config = ConfigDict(defer_build=True)
    work_number: str | None = field(
        default=None,
        metadata={
            "name": "work-number",
            "type": "Element",
        },
    )
    work_title: str | None = field(
        default=None,
        metadata={
            "name": "work-title",
            "type": "Element",
        },
    )
    opus: Opus | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )


class Articulations(BaseModel):
    class Meta:
        name = "articulations"

    model_config = ConfigDict(defer_build=True)
    accent: list[EmptyPlacement] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    strong_accent: list[StrongAccent] = field(
        default_factory=list,
        metadata={
            "name": "strong-accent",
            "type": "Element",
        },
    )
    staccato: list[EmptyPlacement] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    tenuto: list[EmptyPlacement] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    detached_legato: list[EmptyPlacement] = field(
        default_factory=list,
        metadata={
            "name": "detached-legato",
            "type": "Element",
        },
    )
    staccatissimo: list[EmptyPlacement] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    spiccato: list[EmptyPlacement] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    scoop: list[EmptyLine] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    plop: list[EmptyLine] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    doit: list[EmptyLine] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    falloff: list[EmptyLine] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    breath_mark: list[BreathMark] = field(
        default_factory=list,
        metadata={
            "name": "breath-mark",
            "type": "Element",
        },
    )
    caesura: list[Caesura] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    stress: list[EmptyPlacement] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    unstress: list[EmptyPlacement] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    soft_accent: list[EmptyPlacement] = field(
        default_factory=list,
        metadata={
            "name": "soft-accent",
            "type": "Element",
        },
    )
    other_articulation: list[OtherPlacementText] = field(
        default_factory=list,
        metadata={
            "name": "other-articulation",
            "type": "Element",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class FiguredBass(BaseModel):
    class Meta:
        name = "figured-bass"

    model_config = ConfigDict(defer_build=True)
    figure: list[Figure] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )
    duration: Decimal | None = field(
        default=None,
        metadata={
            "type": "Element",
            "min_exclusive": Decimal("0"),
        },
    )
    footnote: FormattedText | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    level: Level | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    halign: LeftCenterRight | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    valign: Valign | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    placement: AboveBelow | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    print_object: YesNo | None = field(
        default=None,
        metadata={
            "name": "print-object",
            "type": "Attribute",
        },
    )
    print_dot: YesNo | None = field(
        default=None,
        metadata={
            "name": "print-dot",
            "type": "Attribute",
        },
    )
    print_spacing: YesNo | None = field(
        default=None,
        metadata={
            "name": "print-spacing",
            "type": "Attribute",
        },
    )
    print_lyric: YesNo | None = field(
        default=None,
        metadata={
            "name": "print-lyric",
            "type": "Attribute",
        },
    )
    parentheses: YesNo | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class ForPart(BaseModel):
    class Meta:
        name = "for-part"

    model_config = ConfigDict(defer_build=True)
    part_clef: PartClef | None = field(
        default=None,
        metadata={
            "name": "part-clef",
            "type": "Element",
        },
    )
    part_transpose: PartTranspose = field(
        metadata={
            "name": "part-transpose",
            "type": "Element",
            "required": True,
        }
    )
    number: int | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Frame(BaseModel):
    class Meta:
        name = "frame"

    model_config = ConfigDict(defer_build=True)
    frame_strings: int = field(
        metadata={
            "name": "frame-strings",
            "type": "Element",
            "required": True,
        }
    )
    frame_frets: int = field(
        metadata={
            "name": "frame-frets",
            "type": "Element",
            "required": True,
        }
    )
    first_fret: FirstFret | None = field(
        default=None,
        metadata={
            "name": "first-fret",
            "type": "Element",
        },
    )
    frame_note: list[FrameNote] = field(
        default_factory=list,
        metadata={
            "name": "frame-note",
            "type": "Element",
            "min_occurs": 1,
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    halign: LeftCenterRight | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    valign: ValignImage | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    height: Decimal | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    width: Decimal | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    unplayed: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Identification(BaseModel):
    class Meta:
        name = "identification"

    model_config = ConfigDict(defer_build=True)
    creator: list[TypedText] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    rights: list[TypedText] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    encoding: Encoding | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    source: str | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    relation: list[TypedText] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    miscellaneous: Miscellaneous | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )


class MetronomeNote(BaseModel):
    class Meta:
        name = "metronome-note"

    model_config = ConfigDict(defer_build=True)
    metronome_type: NoteTypeValue = field(
        metadata={
            "name": "metronome-type",
            "type": "Element",
            "required": True,
        }
    )
    metronome_dot: list[Empty] = field(
        default_factory=list,
        metadata={
            "name": "metronome-dot",
            "type": "Element",
        },
    )
    metronome_beam: list[MetronomeBeam] = field(
        default_factory=list,
        metadata={
            "name": "metronome-beam",
            "type": "Element",
        },
    )
    metronome_tied: MetronomeTied | None = field(
        default=None,
        metadata={
            "name": "metronome-tied",
            "type": "Element",
        },
    )
    metronome_tuplet: MetronomeTuplet | None = field(
        default=None,
        metadata={
            "name": "metronome-tuplet",
            "type": "Element",
        },
    )


class Ornaments(BaseModel):
    class Meta:
        name = "ornaments"

    model_config = ConfigDict(defer_build=True)
    trill_mark: list[EmptyTrillSound] = field(
        default_factory=list,
        metadata={
            "name": "trill-mark",
            "type": "Element",
            "sequence": 1,
        },
    )
    turn: list[HorizontalTurn] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "sequence": 1,
        },
    )
    delayed_turn: list[HorizontalTurn] = field(
        default_factory=list,
        metadata={
            "name": "delayed-turn",
            "type": "Element",
            "sequence": 1,
        },
    )
    inverted_turn: list[HorizontalTurn] = field(
        default_factory=list,
        metadata={
            "name": "inverted-turn",
            "type": "Element",
            "sequence": 1,
        },
    )
    delayed_inverted_turn: list[HorizontalTurn] = field(
        default_factory=list,
        metadata={
            "name": "delayed-inverted-turn",
            "type": "Element",
            "sequence": 1,
        },
    )
    vertical_turn: list[EmptyTrillSound] = field(
        default_factory=list,
        metadata={
            "name": "vertical-turn",
            "type": "Element",
            "sequence": 1,
        },
    )
    inverted_vertical_turn: list[EmptyTrillSound] = field(
        default_factory=list,
        metadata={
            "name": "inverted-vertical-turn",
            "type": "Element",
            "sequence": 1,
        },
    )
    shake: list[EmptyTrillSound] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "sequence": 1,
        },
    )
    wavy_line: list[WavyLine] = field(
        default_factory=list,
        metadata={
            "name": "wavy-line",
            "type": "Element",
            "sequence": 1,
        },
    )
    mordent: list[Mordent] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "sequence": 1,
        },
    )
    inverted_mordent: list[Mordent] = field(
        default_factory=list,
        metadata={
            "name": "inverted-mordent",
            "type": "Element",
            "sequence": 1,
        },
    )
    schleifer: list[EmptyPlacement] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "sequence": 1,
        },
    )
    tremolo: list[Tremolo] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "sequence": 1,
        },
    )
    haydn: list[EmptyTrillSound] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "sequence": 1,
        },
    )
    other_ornament: list[OtherPlacementText] = field(
        default_factory=list,
        metadata={
            "name": "other-ornament",
            "type": "Element",
            "sequence": 1,
        },
    )
    accidental_mark: list[AccidentalMark] = field(
        default_factory=list,
        metadata={
            "name": "accidental-mark",
            "type": "Element",
            "sequence": 1,
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class PartGroup(BaseModel):
    class Meta:
        name = "part-group"

    model_config = ConfigDict(defer_build=True)
    group_name: GroupName | None = field(
        default=None,
        metadata={
            "name": "group-name",
            "type": "Element",
        },
    )
    group_name_display: NameDisplay | None = field(
        default=None,
        metadata={
            "name": "group-name-display",
            "type": "Element",
        },
    )
    group_abbreviation: GroupName | None = field(
        default=None,
        metadata={
            "name": "group-abbreviation",
            "type": "Element",
        },
    )
    group_abbreviation_display: NameDisplay | None = field(
        default=None,
        metadata={
            "name": "group-abbreviation-display",
            "type": "Element",
        },
    )
    group_symbol: GroupSymbol | None = field(
        default=None,
        metadata={
            "name": "group-symbol",
            "type": "Element",
        },
    )
    group_barline: GroupBarline | None = field(
        default=None,
        metadata={
            "name": "group-barline",
            "type": "Element",
        },
    )
    group_time: Empty | None = field(
        default=None,
        metadata={
            "name": "group-time",
            "type": "Element",
        },
    )
    footnote: FormattedText | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    level: Level | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    type_value: StartStop = field(
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        }
    )
    number: str = field(
        default="1",
        metadata={
            "type": "Attribute",
        },
    )


class SystemLayout(BaseModel):
    class Meta:
        name = "system-layout"

    model_config = ConfigDict(defer_build=True)
    system_margins: SystemMargins | None = field(
        default=None,
        metadata={
            "name": "system-margins",
            "type": "Element",
        },
    )
    system_distance: Decimal | None = field(
        default=None,
        metadata={
            "name": "system-distance",
            "type": "Element",
        },
    )
    top_system_distance: Decimal | None = field(
        default=None,
        metadata={
            "name": "top-system-distance",
            "type": "Element",
        },
    )
    system_dividers: SystemDividers | None = field(
        default=None,
        metadata={
            "name": "system-dividers",
            "type": "Element",
        },
    )


class Technical(BaseModel):
    class Meta:
        name = "technical"

    model_config = ConfigDict(defer_build=True)
    up_bow: list[EmptyPlacement] = field(
        default_factory=list,
        metadata={
            "name": "up-bow",
            "type": "Element",
        },
    )
    down_bow: list[EmptyPlacement] = field(
        default_factory=list,
        metadata={
            "name": "down-bow",
            "type": "Element",
        },
    )
    harmonic: list[Harmonic] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    open_string: list[EmptyPlacement] = field(
        default_factory=list,
        metadata={
            "name": "open-string",
            "type": "Element",
        },
    )
    thumb_position: list[EmptyPlacement] = field(
        default_factory=list,
        metadata={
            "name": "thumb-position",
            "type": "Element",
        },
    )
    fingering: list[Fingering] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    pluck: list[PlacementText] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    double_tongue: list[EmptyPlacement] = field(
        default_factory=list,
        metadata={
            "name": "double-tongue",
            "type": "Element",
        },
    )
    triple_tongue: list[EmptyPlacement] = field(
        default_factory=list,
        metadata={
            "name": "triple-tongue",
            "type": "Element",
        },
    )
    stopped: list[EmptyPlacementSmufl] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    snap_pizzicato: list[EmptyPlacement] = field(
        default_factory=list,
        metadata={
            "name": "snap-pizzicato",
            "type": "Element",
        },
    )
    fret: list[Fret] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    string: list[String] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    hammer_on: list[HammerOnPullOff] = field(
        default_factory=list,
        metadata={
            "name": "hammer-on",
            "type": "Element",
        },
    )
    pull_off: list[HammerOnPullOff] = field(
        default_factory=list,
        metadata={
            "name": "pull-off",
            "type": "Element",
        },
    )
    bend: list[Bend] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    tap: list[Tap] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    heel: list[HeelToe] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    toe: list[HeelToe] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    fingernails: list[EmptyPlacement] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    hole: list[Hole] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    arrow: list[Arrow] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    handbell: list[Handbell] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    brass_bend: list[EmptyPlacement] = field(
        default_factory=list,
        metadata={
            "name": "brass-bend",
            "type": "Element",
        },
    )
    flip: list[EmptyPlacement] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    smear: list[EmptyPlacement] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    open: list[EmptyPlacementSmufl] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    half_muted: list[EmptyPlacementSmufl] = field(
        default_factory=list,
        metadata={
            "name": "half-muted",
            "type": "Element",
        },
    )
    harmon_mute: list[HarmonMute] = field(
        default_factory=list,
        metadata={
            "name": "harmon-mute",
            "type": "Element",
        },
    )
    golpe: list[EmptyPlacement] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    other_technical: list[OtherPlacementText] = field(
        default_factory=list,
        metadata={
            "name": "other-technical",
            "type": "Element",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Tuplet(BaseModel):
    class Meta:
        name = "tuplet"

    model_config = ConfigDict(defer_build=True)
    tuplet_actual: TupletPortion | None = field(
        default=None,
        metadata={
            "name": "tuplet-actual",
            "type": "Element",
        },
    )
    tuplet_normal: TupletPortion | None = field(
        default=None,
        metadata={
            "name": "tuplet-normal",
            "type": "Element",
        },
    )
    type_value: StartStop = field(
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        }
    )
    number: int | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 1,
            "max_inclusive": 16,
        },
    )
    bracket: YesNo | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    show_number: ShowTuplet | None = field(
        default=None,
        metadata={
            "name": "show-number",
            "type": "Attribute",
        },
    )
    show_type: ShowTuplet | None = field(
        default=None,
        metadata={
            "name": "show-type",
            "type": "Attribute",
        },
    )
    line_shape: LineShape | None = field(
        default=None,
        metadata={
            "name": "line-shape",
            "type": "Attribute",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    placement: AboveBelow | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Attributes(BaseModel):
    class Meta:
        name = "attributes"

    model_config = ConfigDict(defer_build=True)
    footnote: FormattedText | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    level: Level | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    divisions: Decimal | None = field(
        default=None,
        metadata={
            "type": "Element",
            "min_exclusive": Decimal("0"),
        },
    )
    key: list[Key] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    time: list[Time] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    staves: int | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    part_symbol: PartSymbol | None = field(
        default=None,
        metadata={
            "name": "part-symbol",
            "type": "Element",
        },
    )
    instruments: int | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    clef: list[Clef] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    staff_details: list[StaffDetails] = field(
        default_factory=list,
        metadata={
            "name": "staff-details",
            "type": "Element",
        },
    )
    transpose: list[Transpose] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    for_part: list[ForPart] = field(
        default_factory=list,
        metadata={
            "name": "for-part",
            "type": "Element",
        },
    )
    directive: list["Attributes.Directive"] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    measure_style: list[MeasureStyle] = field(
        default_factory=list,
        metadata={
            "name": "measure-style",
            "type": "Element",
        },
    )

    class Directive(BaseModel):
        model_config = ConfigDict(defer_build=True)
        value: str = field(
            default="",
            metadata={
                "required": True,
            },
        )
        default_x: Decimal | None = field(
            default=None,
            metadata={
                "name": "default-x",
                "type": "Attribute",
            },
        )
        default_y: Decimal | None = field(
            default=None,
            metadata={
                "name": "default-y",
                "type": "Attribute",
            },
        )
        relative_x: Decimal | None = field(
            default=None,
            metadata={
                "name": "relative-x",
                "type": "Attribute",
            },
        )
        relative_y: Decimal | None = field(
            default=None,
            metadata={
                "name": "relative-y",
                "type": "Attribute",
            },
        )
        font_family: str | None = field(
            default=None,
            metadata={
                "name": "font-family",
                "type": "Attribute",
                "pattern": r"[^,]+(, ?[^,]+)*",
            },
        )
        font_style: FontStyle | None = field(
            default=None,
            metadata={
                "name": "font-style",
                "type": "Attribute",
            },
        )
        font_size: Decimal | CssFontSize | None = field(
            default=None,
            metadata={
                "name": "font-size",
                "type": "Attribute",
            },
        )
        font_weight: FontWeight | None = field(
            default=None,
            metadata={
                "name": "font-weight",
                "type": "Attribute",
            },
        )
        color: str | None = field(
            default=None,
            metadata={
                "type": "Attribute",
                "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
            },
        )
        lang: str | LangValue | None = field(
            default=None,
            metadata={
                "type": "Attribute",
                "namespace": XML_NS,
            },
        )


class Defaults(BaseModel):
    class Meta:
        name = "defaults"

    model_config = ConfigDict(defer_build=True)
    scaling: Scaling | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    concert_score: Empty | None = field(
        default=None,
        metadata={
            "name": "concert-score",
            "type": "Element",
        },
    )
    page_layout: PageLayout | None = field(
        default=None,
        metadata={
            "name": "page-layout",
            "type": "Element",
        },
    )
    system_layout: SystemLayout | None = field(
        default=None,
        metadata={
            "name": "system-layout",
            "type": "Element",
        },
    )
    staff_layout: list[StaffLayout] = field(
        default_factory=list,
        metadata={
            "name": "staff-layout",
            "type": "Element",
        },
    )
    appearance: Appearance | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    music_font: EmptyFont | None = field(
        default=None,
        metadata={
            "name": "music-font",
            "type": "Element",
        },
    )
    word_font: EmptyFont | None = field(
        default=None,
        metadata={
            "name": "word-font",
            "type": "Element",
        },
    )
    lyric_font: list[LyricFont] = field(
        default_factory=list,
        metadata={
            "name": "lyric-font",
            "type": "Element",
        },
    )
    lyric_language: list[LyricLanguage] = field(
        default_factory=list,
        metadata={
            "name": "lyric-language",
            "type": "Element",
        },
    )


class Harmony(BaseModel):
    class Meta:
        name = "harmony"

    model_config = ConfigDict(defer_build=True)
    root: list[Root] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    numeral: list[Numeral] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    function: list[StyleText] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    kind: list[Kind] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )
    inversion: list[Inversion] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    bass: list[Bass] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    degree: list[Degree] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    frame: Frame | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    offset: Offset | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    footnote: FormattedText | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    level: Level | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    staff: int | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    type_value: HarmonyType | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
        },
    )
    print_object: YesNo | None = field(
        default=None,
        metadata={
            "name": "print-object",
            "type": "Attribute",
        },
    )
    print_frame: YesNo | None = field(
        default=None,
        metadata={
            "name": "print-frame",
            "type": "Attribute",
        },
    )
    arrangement: HarmonyArrangement | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    placement: AboveBelow | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    system: SystemRelation | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Metronome(BaseModel):
    class Meta:
        name = "metronome"

    model_config = ConfigDict(defer_build=True)
    beat_unit: list[NoteTypeValue] = field(
        default_factory=list,
        metadata={
            "name": "beat-unit",
            "type": "Element",
            "max_occurs": 2,
        },
    )
    beat_unit_dot: list[Empty] = field(
        default_factory=list,
        metadata={
            "name": "beat-unit-dot",
            "type": "Element",
        },
    )
    beat_unit_tied: list[BeatUnitTied] = field(
        default_factory=list,
        metadata={
            "name": "beat-unit-tied",
            "type": "Element",
        },
    )
    per_minute: PerMinute | None = field(
        default=None,
        metadata={
            "name": "per-minute",
            "type": "Element",
        },
    )
    metronome_arrows: Empty | None = field(
        default=None,
        metadata={
            "name": "metronome-arrows",
            "type": "Element",
        },
    )
    metronome_note: list[MetronomeNote] = field(
        default_factory=list,
        metadata={
            "name": "metronome-note",
            "type": "Element",
        },
    )
    metronome_relation: str | None = field(
        default=None,
        metadata={
            "name": "metronome-relation",
            "type": "Element",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    halign: LeftCenterRight | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    valign: Valign | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    print_object: YesNo | None = field(
        default=None,
        metadata={
            "name": "print-object",
            "type": "Attribute",
        },
    )
    justify: LeftCenterRight | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    parentheses: YesNo | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Notations(BaseModel):
    class Meta:
        name = "notations"

    model_config = ConfigDict(defer_build=True)
    footnote: FormattedText | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    level: Level | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    tied: list[Tied] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    slur: list[Slur] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    tuplet: list[Tuplet] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    glissando: list[Glissando] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    slide: list[Slide] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    ornaments: list[Ornaments] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    technical: list[Technical] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    articulations: list[Articulations] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    dynamics: list[Dynamics] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    fermata: list[Fermata] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    arpeggiate: list[Arpeggiate] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    non_arpeggiate: list[NonArpeggiate] = field(
        default_factory=list,
        metadata={
            "name": "non-arpeggiate",
            "type": "Element",
        },
    )
    accidental_mark: list[AccidentalMark] = field(
        default_factory=list,
        metadata={
            "name": "accidental-mark",
            "type": "Element",
        },
    )
    other_notation: list[OtherNotation] = field(
        default_factory=list,
        metadata={
            "name": "other-notation",
            "type": "Element",
        },
    )
    print_object: YesNo | None = field(
        default=None,
        metadata={
            "name": "print-object",
            "type": "Attribute",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Print(BaseModel):
    class Meta:
        name = "print"

    model_config = ConfigDict(defer_build=True)
    page_layout: PageLayout | None = field(
        default=None,
        metadata={
            "name": "page-layout",
            "type": "Element",
        },
    )
    system_layout: SystemLayout | None = field(
        default=None,
        metadata={
            "name": "system-layout",
            "type": "Element",
        },
    )
    staff_layout: list[StaffLayout] = field(
        default_factory=list,
        metadata={
            "name": "staff-layout",
            "type": "Element",
        },
    )
    measure_layout: MeasureLayout | None = field(
        default=None,
        metadata={
            "name": "measure-layout",
            "type": "Element",
        },
    )
    measure_numbering: MeasureNumbering | None = field(
        default=None,
        metadata={
            "name": "measure-numbering",
            "type": "Element",
        },
    )
    part_name_display: NameDisplay | None = field(
        default=None,
        metadata={
            "name": "part-name-display",
            "type": "Element",
        },
    )
    part_abbreviation_display: NameDisplay | None = field(
        default=None,
        metadata={
            "name": "part-abbreviation-display",
            "type": "Element",
        },
    )
    staff_spacing: Decimal | None = field(
        default=None,
        metadata={
            "name": "staff-spacing",
            "type": "Attribute",
        },
    )
    new_system: YesNo | None = field(
        default=None,
        metadata={
            "name": "new-system",
            "type": "Attribute",
        },
    )
    new_page: YesNo | None = field(
        default=None,
        metadata={
            "name": "new-page",
            "type": "Attribute",
        },
    )
    blank_page: int | None = field(
        default=None,
        metadata={
            "name": "blank-page",
            "type": "Attribute",
        },
    )
    page_number: str | None = field(
        default=None,
        metadata={
            "name": "page-number",
            "type": "Attribute",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class ScorePart(BaseModel):
    class Meta:
        name = "score-part"

    model_config = ConfigDict(defer_build=True)
    identification: Identification | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    part_link: list[PartLink] = field(
        default_factory=list,
        metadata={
            "name": "part-link",
            "type": "Element",
        },
    )
    part_name: PartName = field(
        default_factory=PartName,
        metadata={
            "name": "part-name",
            "type": "Element",
            "required": True,
        },
    )
    part_name_display: NameDisplay | None = field(
        default=None,
        metadata={
            "name": "part-name-display",
            "type": "Element",
        },
    )
    part_abbreviation: PartName | None = field(
        default=None,
        metadata={
            "name": "part-abbreviation",
            "type": "Element",
        },
    )
    part_abbreviation_display: NameDisplay | None = field(
        default=None,
        metadata={
            "name": "part-abbreviation-display",
            "type": "Element",
        },
    )
    group: list[str] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    score_instrument: list[ScoreInstrument] = field(
        default_factory=list,
        metadata={
            "name": "score-instrument",
            "type": "Element",
        },
    )
    player: list[Player] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    midi_device: list[MidiDevice] = field(
        default_factory=list,
        metadata={
            "name": "midi-device",
            "type": "Element",
        },
    )
    midi_instrument: list[MidiInstrument] = field(
        default_factory=list,
        metadata={
            "name": "midi-instrument",
            "type": "Element",
        },
    )
    id: str = field(
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )


class DirectionType(BaseModel):
    class Meta:
        name = "direction-type"

    model_config = ConfigDict(defer_build=True)
    rehearsal: list[FormattedTextId] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    segno: list[Segno] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    coda: list[Coda] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    words: list[FormattedTextId] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    symbol: list[FormattedSymbolId] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    wedge: Wedge | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    dynamics: list[Dynamics] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    dashes: Dashes | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    bracket: Bracket | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    pedal: Pedal | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    metronome: Metronome | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    octave_shift: OctaveShift | None = field(
        default=None,
        metadata={
            "name": "octave-shift",
            "type": "Element",
        },
    )
    harp_pedals: HarpPedals | None = field(
        default=None,
        metadata={
            "name": "harp-pedals",
            "type": "Element",
        },
    )
    damp: EmptyPrintStyleAlignId | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    damp_all: EmptyPrintStyleAlignId | None = field(
        default=None,
        metadata={
            "name": "damp-all",
            "type": "Element",
        },
    )
    eyeglasses: EmptyPrintStyleAlignId | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    string_mute: StringMute | None = field(
        default=None,
        metadata={
            "name": "string-mute",
            "type": "Element",
        },
    )
    scordatura: Scordatura | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    image: Image | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    principal_voice: PrincipalVoice | None = field(
        default=None,
        metadata={
            "name": "principal-voice",
            "type": "Element",
        },
    )
    percussion: list[Percussion] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    accordion_registration: AccordionRegistration | None = field(
        default=None,
        metadata={
            "name": "accordion-registration",
            "type": "Element",
        },
    )
    staff_divide: StaffDivide | None = field(
        default=None,
        metadata={
            "name": "staff-divide",
            "type": "Element",
        },
    )
    other_direction: OtherDirection | None = field(
        default=None,
        metadata={
            "name": "other-direction",
            "type": "Element",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Note(BaseModel):
    class Meta:
        name = "note"

    model_config = ConfigDict(defer_build=True)
    grace: Grace | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    chord: list[Empty] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "max_occurs": 4,
        },
    )
    pitch: list[Pitch] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "max_occurs": 4,
        },
    )
    unpitched: list[Unpitched] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "max_occurs": 4,
        },
    )
    rest: list[Rest] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "max_occurs": 4,
        },
    )
    tie: list[Tie] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "max_occurs": 4,
        },
    )
    cue: list[Empty] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "max_occurs": 2,
        },
    )
    duration: list[Decimal] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "max_occurs": 2,
            "min_exclusive": Decimal("0"),
        },
    )
    instrument: list[Instrument] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    footnote: FormattedText | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    level: Level | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    voice: str | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    type_value: NoteType | None = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Element",
        },
    )
    dot: list[EmptyPlacement] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    accidental: Accidental | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    time_modification: TimeModification | None = field(
        default=None,
        metadata={
            "name": "time-modification",
            "type": "Element",
        },
    )
    stem: Stem | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    notehead: Notehead | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    notehead_text: NoteheadText | None = field(
        default=None,
        metadata={
            "name": "notehead-text",
            "type": "Element",
        },
    )
    staff: int | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    beam: list[Beam] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "max_occurs": 8,
        },
    )
    notations: list[Notations] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    lyric: list[Lyric] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    play: Play | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    listen: Listen | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    default_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Decimal | None = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: str | None = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: FontStyle | None = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Decimal | CssFontSize | None = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: FontWeight | None = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    print_object: YesNo | None = field(
        default=None,
        metadata={
            "name": "print-object",
            "type": "Attribute",
        },
    )
    print_dot: YesNo | None = field(
        default=None,
        metadata={
            "name": "print-dot",
            "type": "Attribute",
        },
    )
    print_spacing: YesNo | None = field(
        default=None,
        metadata={
            "name": "print-spacing",
            "type": "Attribute",
        },
    )
    print_lyric: YesNo | None = field(
        default=None,
        metadata={
            "name": "print-lyric",
            "type": "Attribute",
        },
    )
    print_leger: YesNo | None = field(
        default=None,
        metadata={
            "name": "print-leger",
            "type": "Attribute",
        },
    )
    dynamics: Decimal | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": Decimal("0"),
        },
    )
    end_dynamics: Decimal | None = field(
        default=None,
        metadata={
            "name": "end-dynamics",
            "type": "Attribute",
            "min_inclusive": Decimal("0"),
        },
    )
    attack: Decimal | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    release: Decimal | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    time_only: str | None = field(
        default=None,
        metadata={
            "name": "time-only",
            "type": "Attribute",
            "pattern": r"[1-9][0-9]*(, ?[1-9][0-9]*)*",
        },
    )
    pizzicato: YesNo | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class PartList(BaseModel):
    class Meta:
        name = "part-list"

    model_config = ConfigDict(defer_build=True)
    part_group: list[PartGroup] = field(
        default_factory=list,
        metadata={
            "name": "part-group",
            "type": "Element",
        },
    )
    score_part: list[ScorePart] = field(
        default_factory=list,
        metadata={
            "name": "score-part",
            "type": "Element",
            "min_occurs": 1,
        },
    )


class Direction(BaseModel):
    class Meta:
        name = "direction"

    model_config = ConfigDict(defer_build=True)
    direction_type: list[DirectionType] = field(
        default_factory=list,
        metadata={
            "name": "direction-type",
            "type": "Element",
            "min_occurs": 1,
        },
    )
    offset: Offset | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    footnote: FormattedText | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    level: Level | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    voice: str | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    staff: int | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    sound: Sound | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    listening: Listening | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    placement: AboveBelow | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    directive: YesNo | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    system: SystemRelation | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    id: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class ScorePartwise(BaseModel):
    class Meta:
        name = "score-partwise"

    model_config = ConfigDict(defer_build=True)
    work: Work | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    movement_number: str | None = field(
        default=None,
        metadata={
            "name": "movement-number",
            "type": "Element",
        },
    )
    movement_title: str | None = field(
        default=None,
        metadata={
            "name": "movement-title",
            "type": "Element",
        },
    )
    identification: Identification | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    defaults: Defaults | None = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    credit: list[Credit] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    part_list: PartList = field(
        default_factory=PartList,
        metadata={
            "name": "part-list",
            "type": "Element",
            "required": True,
        },
    )
    part: list["ScorePartwise.Part"] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )
    version: str = field(
        default="4.0",
        metadata={
            "type": "Attribute",
        },
    )

    class Part(BaseModel):
        model_config = ConfigDict(defer_build=True)
        measure: list["ScorePartwise.Part.Measure"] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "min_occurs": 1,
            },
        )
        id: str = field(
            metadata={
                "type": "Attribute",
                "required": True,
            }
        )

        class Measure(BaseModel):
            model_config = ConfigDict(defer_build=True)
            note: list[Note] = field(
                default_factory=list,
                metadata={
                    "type": "Element",
                },
            )
            backup: list[Backup] = field(
                default_factory=list,
                metadata={
                    "type": "Element",
                },
            )
            forward: list[Forward] = field(
                default_factory=list,
                metadata={
                    "type": "Element",
                },
            )
            direction: list[Direction] = field(
                default_factory=list,
                metadata={
                    "type": "Element",
                },
            )
            attributes: list[Attributes] = field(
                default_factory=list,
                metadata={
                    "type": "Element",
                },
            )
            harmony: list[Harmony] = field(
                default_factory=list,
                metadata={
                    "type": "Element",
                },
            )
            figured_bass: list[FiguredBass] = field(
                default_factory=list,
                metadata={
                    "name": "figured-bass",
                    "type": "Element",
                },
            )
            print: list[Print] = field(
                default_factory=list,
                metadata={
                    "type": "Element",
                },
            )
            sound: list[Sound] = field(
                default_factory=list,
                metadata={
                    "type": "Element",
                },
            )
            listening: list[Listening] = field(
                default_factory=list,
                metadata={
                    "type": "Element",
                },
            )
            barline: list[Barline] = field(
                default_factory=list,
                metadata={
                    "type": "Element",
                },
            )
            grouping: list[Grouping] = field(
                default_factory=list,
                metadata={
                    "type": "Element",
                },
            )
            link: list[Link] = field(
                default_factory=list,
                metadata={
                    "type": "Element",
                },
            )
            bookmark: list[Bookmark] = field(
                default_factory=list,
                metadata={
                    "type": "Element",
                },
            )
            number: str = field(
                metadata={
                    "type": "Attribute",
                    "required": True,
                }
            )
            text: str | None = field(
                default=None,
                metadata={
                    "type": "Attribute",
                    "min_length": 1,
                },
            )
            implicit: YesNo | None = field(
                default=None,
                metadata={
                    "type": "Attribute",
                },
            )
            non_controlling: YesNo | None = field(
                default=None,
                metadata={
                    "name": "non-controlling",
                    "type": "Attribute",
                },
            )
            width: Decimal | None = field(
                default=None,
                metadata={
                    "type": "Attribute",
                },
            )
            id: str | None = field(
                default=None,
                metadata={
                    "type": "Attribute",
                },
            )
