from decimal import Decimal
from enum import Enum
from typing import Optional, Union

from xsdata_pydantic.fields import field

from libresvip.model.base import BaseModel

from .xlink import XLINK_NS, ActuateValue, ShowValue, TypeValue
from .xml import XML_NS, LangValue


class AboveBelow(Enum):
    """
    The above-below type is used to indicate whether one element appears above or
    below another element.
    """

    ABOVE = "above"
    BELOW = "below"


class AccidentalValue(Enum):
    """The accidental-value type represents notated accidentals supported by
    MusicXML.

    In the MusicXML 2.0 DTD this was a string with values that could be
    included. The XSD strengthens the data typing to an enumerated list.
    """

    SHARP = "sharp"
    NATURAL = "natural"
    FLAT = "flat"
    DOUBLE_SHARP = "double-sharp"
    SHARP_SHARP = "sharp-sharp"
    FLAT_FLAT = "flat-flat"
    NATURAL_SHARP = "natural-sharp"
    NATURAL_FLAT = "natural-flat"
    QUARTER_FLAT = "quarter-flat"
    QUARTER_SHARP = "quarter-sharp"
    THREE_QUARTERS_FLAT = "three-quarters-flat"
    THREE_QUARTERS_SHARP = "three-quarters-sharp"


class BackwardForward(Enum):
    """The backward-forward type is used to specify repeat directions.

    The start of the repeat has a forward direction while the end of the
    repeat has a backward direction.
    """

    BACKWARD = "backward"
    FORWARD = "forward"


class BarStyle(Enum):
    """The bar-style type represents barline style information.

    Choices are regular, dotted, dashed, heavy, light-light, light-
    heavy, heavy-light, heavy-heavy, tick (a short stroke through the
    top line), short (a partial barline between the 2nd and 4th lines),
    and none.
    """

    REGULAR = "regular"
    DOTTED = "dotted"
    DASHED = "dashed"
    HEAVY = "heavy"
    LIGHT_LIGHT = "light-light"
    LIGHT_HEAVY = "light-heavy"
    HEAVY_LIGHT = "heavy-light"
    HEAVY_HEAVY = "heavy-heavy"
    TICK = "tick"
    SHORT = "short"
    NONE = "none"


class BeamValue(Enum):
    """
    The beam-value type represents the type of beam associated with each of 6 beam
    levels (up to 256th notes) available for each note.
    """

    BEGIN = "begin"
    CONTINUE = "continue"
    END = "end"
    FORWARD_HOOK = "forward hook"
    BACKWARD_HOOK = "backward hook"


class Bookmark(BaseModel):
    """
    The bookmark type serves as a well-defined target for an incoming simple XLink.
    """

    class Meta:
        name = "bookmark"

    bookmark_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "id",
            "type": "Attribute",
            "required": True,
        },
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    element: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    position: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class ClefSign(Enum):
    """
    The clef-sign element represents the different clef symbols.
    """

    G = "G"
    F = "F"
    C = "C"
    PERCUSSION = "percussion"
    TAB = "TAB"
    NONE = "none"


class CssFontSize(Enum):
    """
    The css-font-size type includes the CSS font sizes used as an alternative to a
    numeric point size.
    """

    XX_SMALL = "xx-small"
    X_SMALL = "x-small"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    X_LARGE = "x-large"
    XX_LARGE = "xx-large"


class DegreeTypeValue(Enum):
    """
    The degree-type-value type indicates whether the current degree element is an
    addition, alteration, or subtraction to the kind of the current chord in the
    harmony element.
    """

    ADD = "add"
    ALTER = "alter"
    SUBTRACT = "subtract"


class Empty(BaseModel):
    """
    The empty type represents an empty element with no attributes.
    """

    class Meta:
        name = "empty"


class Enclosure(Enum):
    """
    The enclosure type describes the shape and presence / absence of an enclosure
    around text.
    """

    RECTANGLE = "rectangle"
    OVAL = "oval"
    NONE = "none"


class Fan(Enum):
    """
    The fan type represents the type of beam fanning present on a note, used to
    represent accelerandos and ritardandos.
    """

    ACCEL = "accel"
    RIT = "rit"
    NONE = "none"


class Feature(BaseModel):
    """The feature type is a part of the grouping element used for musical
    analysis.

    The type attribute represents the type of the feature and the
    element content represents its value. This type is flexible to allow
    for different analyses.
    """

    class Meta:
        name = "feature"

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    type_value: Optional[str] = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
        },
    )


class FermataShape(Enum):
    """The fermata-shape type represents the shape of the fermata sign.

    The empty value is equivalent to the normal value.
    """

    NORMAL = "normal"
    ANGLED = "angled"
    SQUARE = "square"
    VALUE = ""


class FontStyle(Enum):
    """
    The font-style type represents a simplified version of the CSS font-style
    property.
    """

    NORMAL = "normal"
    ITALIC = "italic"


class FontWeight(Enum):
    """
    The font-weight type represents a simplified version of the CSS font-weight
    property.
    """

    NORMAL = "normal"
    BOLD = "bold"


class GroupBarlineValue(Enum):
    """
    The group-barline-value type indicates if the group should have common
    barlines.
    """

    YES = "yes"
    NO = "no"
    MENSURSTRICH = "Mensurstrich"


class GroupSymbolValue(Enum):
    """The group-symbol-value type indicates how the symbol for a group is
    indicated in the score.

    The default value is none.
    """

    NONE = "none"
    BRACE = "brace"
    LINE = "line"
    BRACKET = "bracket"


class HarmonyType(Enum):
    """The harmony-type type differentiates different types of harmonies when
    alternate harmonies are possible.

    Explicit harmonies have all note present in the music; implied have
    some notes missing but implied; alternate represents alternate
    analyses.
    """

    EXPLICIT = "explicit"
    IMPLIED = "implied"
    ALTERNATE = "alternate"


class Instrument(BaseModel):
    """The instrument type distinguishes between score-instrument elements in a
    score-part.

    The id attribute is an IDREF back to the score-instrument ID. If
    multiple score-instruments are specified on a score-part, there
    should be an instrument element for each note in the part.
    """

    class Meta:
        name = "instrument"

    instrument_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "id",
            "type": "Attribute",
            "required": True,
        },
    )


class KindValue(Enum):
    """A kind-value indicates the type of chord.

    Degree elements can then add, subtract, or alter from these starting points. Values include:
    Triads:
    major (major third, perfect fifth)
    minor (minor third, perfect fifth)
    augmented (major third, augmented fifth)
    diminished (minor third, diminished fifth)
    Sevenths:
    dominant (major triad, minor seventh)
    major-seventh (major triad, major seventh)
    minor-seventh (minor triad, minor seventh)
    diminished-seventh (diminished triad, diminished seventh)
    augmented-seventh (augmented triad, minor seventh)
    half-diminished (diminished triad, minor seventh)
    major-minor (minor triad, major seventh)
    Sixths:
    major-sixth (major triad, added sixth)
    minor-sixth (minor triad, added sixth)
    Ninths:
    dominant-ninth (dominant-seventh, major ninth)
    major-ninth (major-seventh, major ninth)
    minor-ninth (minor-seventh, major ninth)
    11ths (usually as the basis for alteration):
    dominant-11th (dominant-ninth, perfect 11th)
    major-11th (major-ninth, perfect 11th)
    minor-11th (minor-ninth, perfect 11th)
    13ths (usually as the basis for alteration):
    dominant-13th (dominant-11th, major 13th)
    major-13th (major-11th, major 13th)
    minor-13th (minor-11th, major 13th)
    Suspended:
    suspended-second (major second, perfect fifth)
    suspended-fourth (perfect fourth, perfect fifth)
    Functional sixths:
    Neapolitan
    Italian
    French
    German
    Other:
    pedal (pedal-point bass)
    power (perfect fifth)
    Tristan
    The "other" kind is used when the harmony is entirely composed of add elements. The "none" kind is used to explicitly encode absence of chords or functional harmony.
    """

    MAJOR = "major"
    MINOR = "minor"
    AUGMENTED = "augmented"
    DIMINISHED = "diminished"
    DOMINANT = "dominant"
    MAJOR_SEVENTH = "major-seventh"
    MINOR_SEVENTH = "minor-seventh"
    DIMINISHED_SEVENTH = "diminished-seventh"
    AUGMENTED_SEVENTH = "augmented-seventh"
    HALF_DIMINISHED = "half-diminished"
    MAJOR_MINOR = "major-minor"
    MAJOR_SIXTH = "major-sixth"
    MINOR_SIXTH = "minor-sixth"
    DOMINANT_NINTH = "dominant-ninth"
    MAJOR_NINTH = "major-ninth"
    MINOR_NINTH = "minor-ninth"
    DOMINANT_11TH = "dominant-11th"
    MAJOR_11TH = "major-11th"
    MINOR_11TH = "minor-11th"
    DOMINANT_13TH = "dominant-13th"
    MAJOR_13TH = "major-13th"
    MINOR_13TH = "minor-13th"
    SUSPENDED_SECOND = "suspended-second"
    SUSPENDED_FOURTH = "suspended-fourth"
    NEAPOLITAN = "Neapolitan"
    ITALIAN = "Italian"
    FRENCH = "French"
    GERMAN = "German"
    PEDAL = "pedal"
    POWER = "power"
    TRISTAN = "Tristan"
    OTHER = "other"
    NONE = "none"


class LeftCenterRight(Enum):
    """
    The left-center-right type is used to define horizontal alignment and text
    justification.
    """

    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class LeftRight(Enum):
    """
    The left-right type is used to indicate whether one element appears to the left
    or the right of another element.
    """

    LEFT = "left"
    RIGHT = "right"


class LineEnd(Enum):
    """
    The line-end type specifies if there is a jog up or down (or both), an arrow,
    or nothing at the start or end of a bracket.
    """

    UP = "up"
    DOWN = "down"
    BOTH = "both"
    ARROW = "arrow"
    NONE = "none"


class LineShape(Enum):
    """
    The line-shape type distinguishes between straight and curved lines.
    """

    STRAIGHT = "straight"
    CURVED = "curved"


class LineType(Enum):
    """
    The line-type type distinguishes between solid, dashed, dotted, and wavy lines.
    """

    SOLID = "solid"
    DASHED = "dashed"
    DOTTED = "dotted"
    WAVY = "wavy"


class LineWidth(BaseModel):
    """The line-width type indicates the width of a line type in tenths.

    The type attribute defines what type of line is being defined.
    Values include beam, bracket, dashes, enclosure, ending, extend,
    heavy barline, leger, light barline, octave shift, pedal, slur
    middle, slur tip, staff, stem, tie middle, tie tip, tuplet bracket,
    and wedge. The text content is expressed in tenths.
    """

    class Meta:
        name = "line-width"

    value: Optional[Decimal] = field(
        default=None,
        metadata={
            "required": True,
        },
    )
    type_value: Optional[str] = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )


class MarginType(Enum):
    """
    The margin-type type specifies whether margins apply to even page, odd pages,
    or both.
    """

    ODD = "odd"
    EVEN = "even"
    BOTH = "both"


class MeasureLayout(BaseModel):
    """
    The measure-layout type includes the horizontal distance from the previous
    measure.

    :ivar measure_distance: The measure-distance element specifies the
        horizontal distance from the previous measure. This value is
        only used for systems where there is horizontal whitespace in
        the middle of a system, as in systems with codas. To specify the
        measure width, use the width attribute of the measure element.
    """

    class Meta:
        name = "measure-layout"

    measure_distance: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "measure-distance",
            "type": "Element",
        },
    )


class MeasureNumberingValue(Enum):
    """The measure-numbering-value type describes how measure numbers are displayed on this part: no numbers, numbers every measure, or numbers every system."""

    NONE = "none"
    MEASURE = "measure"
    SYSTEM = "system"


class MidiDevice(BaseModel):
    """The midi-device type corresponds to the DeviceName meta event in Standard
    MIDI Files.

    The optional port attribute is a number from 1 to 16 that can be
    used with the unofficial MIDI port (or cable) meta event.
    """

    class Meta:
        name = "midi-device"

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    port: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 1,
            "max_inclusive": 16,
        },
    )


class MidiInstrument(BaseModel):
    """The midi-instrument type defines MIDI 1.0 instrument playback.

    The midi-instrument element can be a part of either the score-
    instrument element at the start of a part, or the sound element
    within a part. The id attribute refers to the score-instrument
    affected by the change.

    :ivar midi_channel: The midi-channel element specifies a MIDI 1.0
        channel numbers ranging from 1 to 16.
    :ivar midi_name: The midi-name element corresponds to a ProgramName
        meta-event within a Standard MIDI File.
    :ivar midi_bank: The midi-bank element specified a MIDI 1.0 bank
        number ranging from 1 to 16,384.
    :ivar midi_program: The midi-program element specifies a MIDI 1.0
        program number ranging from 1 to 128.
    :ivar midi_unpitched: For unpitched instruments, the midi-unpitched
        element specifies a MIDI 1.0 note number ranging from 1 to 128.
        It is usually used with MIDI banks for percussion.
    :ivar volume: The volume element value is a percentage of the
        maximum ranging from 0 to 100, with decimal values allowed. This
        corresponds to a scaling value for the MIDI 1.0 channel volume
        controller.
    :ivar pan: The pan and elevation elements allow placing of sound in
        a 3-D space relative to the listener. Both are expressed in
        degrees ranging from -180 to 180. For pan, 0 is straight ahead,
        -90 is hard left, 90 is hard right, and -180 and 180 are
        directly behind the listener.
    :ivar elevation: The elevation and pan elements allow placing of
        sound in a 3-D space relative to the listener. Both are
        expressed in degrees ranging from -180 to 180. For elevation, 0
        is level with the listener, 90 is directly above, and -90 is
        directly below.
    :ivar id:
    """

    class Meta:
        name = "midi-instrument"

    midi_channel: Optional[int] = field(
        default=None,
        metadata={
            "name": "midi-channel",
            "type": "Element",
            "min_inclusive": 1,
            "max_inclusive": 16,
        },
    )
    midi_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "midi-name",
            "type": "Element",
        },
    )
    midi_bank: Optional[int] = field(
        default=None,
        metadata={
            "name": "midi-bank",
            "type": "Element",
            "min_inclusive": 1,
            "max_inclusive": 16384,
        },
    )
    midi_program: Optional[int] = field(
        default=None,
        metadata={
            "name": "midi-program",
            "type": "Element",
            "min_inclusive": 1,
            "max_inclusive": 128,
        },
    )
    midi_unpitched: Optional[int] = field(
        default=None,
        metadata={
            "name": "midi-unpitched",
            "type": "Element",
            "min_inclusive": 1,
            "max_inclusive": 128,
        },
    )
    volume: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "min_inclusive": Decimal("0"),
            "max_inclusive": Decimal("100"),
        },
    )
    pan: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "min_inclusive": Decimal("-180"),
            "max_inclusive": Decimal("180"),
        },
    )
    elevation: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "min_inclusive": Decimal("-180"),
            "max_inclusive": Decimal("180"),
        },
    )
    midi_instrument_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "id",
            "type": "Attribute",
            "required": True,
        },
    )


class MiscellaneousField(BaseModel):
    """If a program has other metadata not yet supported in the MusicXML format,
    each type of metadata can go in a miscellaneous-field element.

    The required name attribute indicates the type of metadata the
    element content represents.
    """

    class Meta:
        name = "miscellaneous-field"

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )


class NoteSizeType(Enum):
    """The note-size-type type indicates the type of note being defined by a note-
    size element.

    The grace type is used for notes of cue size that that include a
    grace element. The cue type is used for all other notes with cue
    size, whether defined explicitly or implicitly via a cue element.
    The large type is used for notes of large size.
    """

    CUE = "cue"
    GRACE = "grace"
    LARGE = "large"


class NoteTypeValue(Enum):
    """
    The note-type type is used for the MusicXML type element and represents the
    graphic note type, from 256th (shortest) to long (longest).
    """

    VALUE_256TH = "256th"
    VALUE_128TH = "128th"
    VALUE_64TH = "64th"
    VALUE_32ND = "32nd"
    VALUE_16TH = "16th"
    EIGHTH = "eighth"
    QUARTER = "quarter"
    HALF = "half"
    WHOLE = "whole"
    BREVE = "breve"
    LONG = "long"


class NoteheadValue(Enum):
    """The notehead type indicates shapes other than the open and closed ovals
    associated with note durations.

    The values do, re, mi, fa, so, la, and ti correspond to Aikin's
    7-shape system. The arrow shapes differ from triangle and inverted
    triangle by being centered on the stem. Slashed and back slashed
    notes include both the normal notehead and a slash. The triangle
    shape has the tip of the triangle pointing up; the inverted triangle
    shape has the tip of the triangle pointing down.
    """

    SLASH = "slash"
    TRIANGLE = "triangle"
    DIAMOND = "diamond"
    SQUARE = "square"
    CROSS = "cross"
    X = "x"
    CIRCLE_X = "circle-x"
    INVERTED_TRIANGLE = "inverted triangle"
    ARROW_DOWN = "arrow down"
    ARROW_UP = "arrow up"
    SLASHED = "slashed"
    BACK_SLASHED = "back slashed"
    NORMAL = "normal"
    CLUSTER = "cluster"
    NONE = "none"
    DO = "do"
    RE = "re"
    MI = "mi"
    FA = "fa"
    SO = "so"
    LA = "la"
    TI = "ti"


class NumberOrNormalValue(Enum):
    NORMAL = "normal"


class OtherAppearance(BaseModel):
    """The other-appearance type is used to define any graphical settings not yet
    in the current version of the MusicXML format.

    This allows extended representation, though without application
    interoperability.
    """

    class Meta:
        name = "other-appearance"

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    type_value: Optional[str] = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )


class OverUnder(Enum):
    """
    The over-under type is used to indicate whether the tips of curved lines such
    as slurs and ties are overhand (tips down) or underhand (tips up).
    """

    OVER = "over"
    UNDER = "under"


class PositiveIntegerOrEmptyValue(Enum):
    VALUE = ""


class RehearsalEnclosure(Enum):
    """
    The rehearsal-enclosure type describes the shape and presence / absence of an
    enclosure around rehearsal text.
    """

    SQUARE = "square"
    CIRCLE = "circle"
    NONE = "none"


class RightLeftMiddle(Enum):
    """
    The right-left-middle type is used to specify barline location.
    """

    RIGHT = "right"
    LEFT = "left"
    MIDDLE = "middle"


class Scaling(BaseModel):
    """Margins, page sizes, and distances are all measured in tenths to keep
    MusicXML data in a consistent coordinate system as much as possible.

    The translation to absolute units is done with the scaling type,
    which specifies how many millimeters are equal to how many tenths.
    For a staff height of 7 mm, millimeters would be set to 7 while
    tenths is set to 40. The ability to set a formula rather than a
    single scaling factor helps avoid roundoff errors.
    """

    class Meta:
        name = "scaling"

    millimeters: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    tenths: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )


class ShowFrets(Enum):
    """The show-frets type indicates whether to show tablature frets as numbers (0,
    1, 2) or letters (a, b, c).

    The default choice is numbers.
    """

    NUMBERS = "numbers"
    LETTERS = "letters"


class ShowTuplet(Enum):
    """
    The show-tuplet type indicates whether to show a part of a tuplet relating to
    the tuplet-actual element, both the tuplet-actual and tuplet-normal elements,
    or neither.
    """

    ACTUAL = "actual"
    BOTH = "both"
    NONE = "none"


class StaffLayout(BaseModel):
    """Staff layout includes the vertical distance from the bottom line of the
    previous staff in this system to the top line of the staff specified by the
    number attribute.

    The optional number attribute refers to staff numbers within the
    part, from top to bottom on the system. A value of 1 is assumed if
    not present. When used in the defaults element, the values apply to
    all parts. This value is ignored for the first staff in a system.
    """

    class Meta:
        name = "staff-layout"

    staff_distance: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "staff-distance",
            "type": "Element",
        },
    )
    number: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class StaffType(Enum):
    """The staff-type value can be ossia, cue, editorial, regular, or alternate.

    An alternate staff indicates one that shares the same musical data
    as the prior staff, but displayed differently (e.g., treble and bass
    clef, standard notation and tab).
    """

    OSSIA = "ossia"
    CUE = "cue"
    EDITORIAL = "editorial"
    REGULAR = "regular"
    ALTERNATE = "alternate"


class StartNote(Enum):
    """
    The start-note type describes the starting note of trills and mordents for
    playback, relative to the current note.
    """

    UPPER = "upper"
    MAIN = "main"
    BELOW = "below"


class StartStop(Enum):
    """
    The start-stop type is used for an attribute of musical elements that can
    either start or stop, such as tuplets, wedges, and lines.
    """

    START = "start"
    STOP = "stop"


class StartStopChange(Enum):
    """
    The start-stop-change type is used to distinguish types of pedal directions.
    """

    START = "start"
    STOP = "stop"
    CHANGE = "change"


class StartStopContinue(Enum):
    """
    The start-stop-continue type is used for an attribute of musical elements that
    can either start or stop, but also need to refer to an intermediate point in
    the symbol, as for complex slurs.
    """

    START = "start"
    STOP = "stop"
    CONTINUE = "continue"


class StartStopDiscontinue(Enum):
    """The start-stop-discontinue type is used to specify ending types.

    Typically, the start type is associated with the left barline of the
    first measure in an ending. The stop and discontinue types are
    associated with the right barline of the last measure in an ending.
    Stop is used when the ending mark concludes with a downward jog, as
    is typical for first endings. Discontinue is used when there is no
    downward jog, as is typical for second endings that do not conclude
    a piece.
    """

    START = "start"
    STOP = "stop"
    DISCONTINUE = "discontinue"


class StartStopSingle(Enum):
    """
    The start-stop-single type is used for an attribute of musical elements that
    can be used for either multi-note or single-note musical elements, as for
    tremolos.
    """

    START = "start"
    STOP = "stop"
    SINGLE = "single"


class StemValue(Enum):
    """
    The stem type represents the notated stem direction.
    """

    DOWN = "down"
    UP = "up"
    DOUBLE = "double"
    NONE = "none"


class Step(Enum):
    """
    The step type represents a step of the diatonic scale, represented using the
    English letters A through G.
    """

    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"
    G = "G"


class Syllabic(Enum):
    """Lyric hyphenation is indicated by the syllabic type.

    The single, begin, end, and middle values represent single-syllable
    words, word-beginning syllables, word-ending syllables, and mid-word
    syllables, respectively.
    """

    SINGLE = "single"
    BEGIN = "begin"
    END = "end"
    MIDDLE = "middle"


class SymbolSize(Enum):
    """The symbol-size type is used to indicate full vs.

    cue-sized vs. oversized symbols. The large value for oversized
    symbols was added in version 1.1.
    """

    FULL = "full"
    CUE = "cue"
    LARGE = "large"


class SystemMargins(BaseModel):
    """System margins are relative to the page margins.

    Positive values indent and negative values reduce the margin size.
    """

    class Meta:
        name = "system-margins"

    left_margin: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "left-margin",
            "type": "Element",
            "required": True,
        },
    )
    right_margin: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "right-margin",
            "type": "Element",
            "required": True,
        },
    )


class TextDirection(Enum):
    """The text-direction type is used to adjust and override the Unicode
    bidirectional text algorithm, similar to the W3C Internationalization Tag Set
    recommendation.

    Values are ltr (left-to-right embed), rtl (right-to-left embed), lro
    (left-to-right bidi-override), and rlo (right-to-left bidi-
    override). The default value is ltr. This type is typically used by
    applications that store text in left-to-right visual order rather
    than logical order. Such applications can use the lro value to
    better communicate with other applications that more fully support
    bidirectional text.
    """

    LTR = "ltr"
    RTL = "rtl"
    LRO = "lro"
    RLO = "rlo"


class TimeSymbol(Enum):
    """The time-symbol type indicates how to display a time signature.

    The normal value is the usual fractional display, and is the implied
    symbol type if none is specified. Other options are the common and
    cut time symbols, as well as a single number with an implied
    denominator.
    """

    COMMON = "common"
    CUT = "cut"
    SINGLE_NUMBER = "single-number"
    NORMAL = "normal"


class TopBottom(Enum):
    """
    The top-bottom type is used to indicate the top or bottom part of a vertical
    shape like non-arpeggiate.
    """

    TOP = "top"
    BOTTOM = "bottom"


class TrillStep(Enum):
    """
    The trill-step type describes the alternating note of trills and mordents for
    playback, relative to the current note.
    """

    WHOLE = "whole"
    HALF = "half"
    UNISON = "unison"


class TwoNoteTurn(Enum):
    """
    The two-note-turn type describes the ending notes of trills and mordents for
    playback, relative to the current note.
    """

    WHOLE = "whole"
    HALF = "half"
    NONE = "none"


class TypedText(BaseModel):
    """
    The typed-text type represents a text element with a type attributes.
    """

    class Meta:
        name = "typed-text"

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    type_value: Optional[str] = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
        },
    )


class UpDown(Enum):
    """
    The up-down type is used for arrow direction, indicating which way the tip is
    pointing.
    """

    UP = "up"
    DOWN = "down"


class UpDownStop(Enum):
    """
    The up-down-stop type is used for octave-shift elements, indicating the
    direction of the shift from their true pitched values because of printing
    difficulty.
    """

    UP = "up"
    DOWN = "down"
    STOP = "stop"


class UprightInverted(Enum):
    """The upright-inverted type describes the appearance of a fermata element.

    The value is upright if not specified.
    """

    UPRIGHT = "upright"
    INVERTED = "inverted"


class Valign(Enum):
    """The valign type is used to indicate vertical alignment to the top, middle,
    bottom, or baseline of the text.

    Defaults are implementation-dependent.
    """

    TOP = "top"
    MIDDLE = "middle"
    BOTTOM = "bottom"
    BASELINE = "baseline"


class ValignImage(Enum):
    """The valign-image type is used to indicate vertical alignment for images and
    graphics, so it does not include a baseline value.

    Defaults are implementation-dependent.
    """

    TOP = "top"
    MIDDLE = "middle"
    BOTTOM = "bottom"


class WedgeType(Enum):
    """
    The wedge type is crescendo for the start of a wedge that is closed at the left
    side, diminuendo for the start of a wedge that is closed on the right side, and
    stop for the end of a wedge.
    """

    CRESCENDO = "crescendo"
    DIMINUENDO = "diminuendo"
    STOP = "stop"


class YesNo(Enum):
    """The yes-no type is used for boolean-like attributes.

    We cannot use W3C XML Schema booleans due to their restrictions on
    expression of boolean values.
    """

    YES = "yes"
    NO = "no"


class Accidental(BaseModel):
    """The accidental type represents actual notated accidentals.

    Editorial and cautionary indications are indicated by attributes.
    Values for these attributes are "no" if not present. Specific
    graphic display such as parentheses, brackets, and size are
    controlled by the level-display attribute group.
    """

    class Meta:
        name = "accidental"

    value: Optional[AccidentalValue] = field(
        default=None,
        metadata={
            "required": True,
        },
    )
    cautionary: Optional[YesNo] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    editorial: Optional[YesNo] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    parentheses: Optional[YesNo] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    bracket: Optional[YesNo] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    size: Optional[SymbolSize] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class AccidentalMark(BaseModel):
    """An accidental-mark can be used as a separate notation or as part of an
    ornament.

    When used in an ornament, position and placement are relative to the
    ornament, not relative to the note.
    """

    class Meta:
        name = "accidental-mark"

    value: Optional[AccidentalValue] = field(
        default=None,
        metadata={
            "required": True,
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    placement: Optional[AboveBelow] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class AccidentalText(BaseModel):
    """
    The accidental-text type represents an element with an accidental value and
    text-formatting attributes.
    """

    class Meta:
        name = "accidental-text"

    value: Optional[AccidentalValue] = field(
        default=None,
        metadata={
            "required": True,
        },
    )
    justify: Optional[LeftCenterRight] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    halign: Optional[LeftCenterRight] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    valign: Optional[Valign] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    underline: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 3,
        },
    )
    overline: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 3,
        },
    )
    line_through: Optional[int] = field(
        default=None,
        metadata={
            "name": "line-through",
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 3,
        },
    )
    rotation: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": Decimal("-180"),
            "max_inclusive": Decimal("180"),
        },
    )
    letter_spacing: Optional[Union[Decimal, NumberOrNormalValue]] = field(
        default=None,
        metadata={
            "name": "letter-spacing",
            "type": "Attribute",
        },
    )
    line_height: Optional[Union[Decimal, NumberOrNormalValue]] = field(
        default=None,
        metadata={
            "name": "line-height",
            "type": "Attribute",
        },
    )
    lang: Optional[Union[str, LangValue]] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "namespace": XML_NS,
        },
    )
    direction: Optional[TextDirection] = field(
        default=None,
        metadata={
            "name": "dir",
            "type": "Attribute",
        },
    )
    enclosure: Optional[Enclosure] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Accord(BaseModel):
    """The accord type represents the tuning of a single string in the scordatura
    element.

    It uses the same group of elements as the staff-tuning element.
    Strings are numbered from high to low.

    :ivar tuning_step: The tuning-step element is represented like the
        step element, with a different name to reflect is different
        function.
    :ivar tuning_alter: The tuning-alter element is represented like the
        alter element, with a different name to reflect is different
        function.
    :ivar tuning_octave: The tuning-octave element is represented like
        the octave element, with a different name to reflect is
        different function.
    :ivar string:
    """

    class Meta:
        name = "accord"

    tuning_step: Optional[Step] = field(
        default=None,
        metadata={
            "name": "tuning-step",
            "type": "Element",
            "required": True,
        },
    )
    tuning_alter: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "tuning-alter",
            "type": "Element",
        },
    )
    tuning_octave: Optional[int] = field(
        default=None,
        metadata={
            "name": "tuning-octave",
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 9,
        },
    )
    string: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class AccordionRegistration(BaseModel):
    """The accordion-registration type is use for accordion registration symbols.

    These are circular symbols divided horizontally into high, middle,
    and low sections that correspond to 4', 8', and 16' pipes. Each
    accordion-high, accordion-middle, and accordion-low element
    represents the presence of one or more dots in the registration
    diagram. An accordion-registration element needs to have at least
    one of the child elements present.

    :ivar accordion_high: The accordion-high element indicates the
        presence of a dot in the high (4') section of the registration
        symbol.
    :ivar accordion_middle: The accordion-middle element indicates the
        presence of 1 to 3 dots in the middle (8') section of the
        registration symbol.
    :ivar accordion_low: The accordion-low element indicates the
        presence of a dot in the low (16') section of the registration
        symbol.
    :ivar default_x:
    :ivar default_y:
    :ivar relative_x:
    :ivar relative_y:
    :ivar font_family:
    :ivar font_style:
    :ivar font_size:
    :ivar font_weight:
    :ivar color:
    """

    class Meta:
        name = "accordion-registration"

    accordion_high: Optional[Empty] = field(
        default=None,
        metadata={
            "name": "accordion-high",
            "type": "Element",
        },
    )
    accordion_middle: Optional[int] = field(
        default=None,
        metadata={
            "name": "accordion-middle",
            "type": "Element",
            "min_inclusive": 1,
            "max_inclusive": 3,
        },
    )
    accordion_low: Optional[Empty] = field(
        default=None,
        metadata={
            "name": "accordion-low",
            "type": "Element",
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class Arpeggiate(BaseModel):
    """The arpeggiate type indicates that this note is part of an arpeggiated
    chord.

    The number attribute can be used to distinguish between two
    simultaneous chords arpeggiated separately (different numbers) or
    together (same number). The up-down attribute is used if there is an
    arrow on the arpeggio sign. By default, arpeggios go from the lowest
    to highest note.
    """

    class Meta:
        name = "arpeggiate"

    number: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 1,
            "max_inclusive": 6,
        },
    )
    direction: Optional[UpDown] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    placement: Optional[AboveBelow] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class BarStyleColor(BaseModel):
    """
    The bar-style-color type contains barline style and color information.
    """

    class Meta:
        name = "bar-style-color"

    value: Optional[BarStyle] = field(
        default=None,
        metadata={
            "required": True,
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class Barre(BaseModel):
    """The barre element indicates placing a finger over multiple strings on a
    single fret.

    The type is "start" for the lowest pitched string (e.g., the string
    with the highest MusicXML number) and is "stop" for the highest
    pitched string.
    """

    class Meta:
        name = "barre"

    type_value: Optional[StartStop] = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class BassAlter(BaseModel):
    """The bass-alter type represents the chromatic alteration of the bass of the
    current chord within the harmony element.

    In some chord styles, the text for the bass-step element may include
    bass-alter information. In that case, the print-object attribute of
    the bass-alter element can be set to no. The location attribute
    indicates whether the alteration should appear to the left or the
    right of the bass-step; it is right by default.
    """

    class Meta:
        name = "bass-alter"

    value: Optional[Decimal] = field(
        default=None,
        metadata={
            "required": True,
        },
    )
    print_object: Optional[YesNo] = field(
        default=None,
        metadata={
            "name": "print-object",
            "type": "Attribute",
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    location: Optional[LeftRight] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class BassStep(BaseModel):
    """The bass-step type represents the pitch step of the bass of the current
    chord within the harmony element.

    The text attribute indicates how the bass should appear on the page
    if not using the element contents.
    """

    class Meta:
        name = "bass-step"

    value: Optional[Step] = field(
        default=None,
        metadata={
            "required": True,
        },
    )
    text: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class Beam(BaseModel):
    """Beam values include begin, continue, end, forward hook, and backward hook.

    Up to six concurrent beam levels are available to cover up to 256th
    notes. The repeater attribute, used for tremolos, needs to be
    specified with a "yes" value for each beam using it. Beams that have
    a begin value can also have a fan attribute to indicate accelerandos
    and ritardandos using fanned beams. The fan attribute may also be
    used with a continue value if the fanning direction changes on that
    note. The value is "none" if not specified. Note that the beam
    number does not distinguish sets of beams that overlap, as it does
    for slur and other elements. Beaming groups are distinguished by
    being in different voices and/or the presence or absence of grace
    and cue elements.
    """

    class Meta:
        name = "beam"

    value: Optional[BeamValue] = field(
        default=None,
        metadata={
            "required": True,
        },
    )
    number: int = field(
        default=1,
        metadata={
            "type": "Attribute",
            "min_inclusive": 1,
            "max_inclusive": 6,
        },
    )
    repeater: Optional[YesNo] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    fan: Optional[Fan] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class BeatRepeat(BaseModel):
    """The beat-repeat type is used to indicate that a single beat (but possibly
    many notes) is repeated.

    Both the start and stop of the beat being repeated should be
    specified. The slashes attribute specifies the number of slashes to
    use in the symbol. The use-dots attribute indicates whether or not
    to use dots as well (for instance, with mixed rhythm patterns). By
    default, the value for slashes is 1 and the value for use-dots is
    no. The beat-repeat element specifies a notation style for
    repetitions. The actual music being repeated needs to be repeated
    within the MusicXML file. This element specifies the notation that
    indicates the repeat.

    :ivar slash_type: The slash-type element indicates the graphical
        note type to use for the display of repetition marks.
    :ivar slash_dot: The slash-dot element is used to specify any
        augmentation dots in the note type used to display repetition
        marks.
    :ivar type_value:
    :ivar slashes:
    :ivar use_dots:
    """

    class Meta:
        name = "beat-repeat"

    slash_type: Optional[NoteTypeValue] = field(
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
    type_value: Optional[StartStop] = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )
    slashes: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    use_dots: Optional[YesNo] = field(
        default=None,
        metadata={
            "name": "use-dots",
            "type": "Attribute",
        },
    )


class Bracket(BaseModel):
    """Brackets are combined with words in a variety of modern directions.

    The line-end attribute specifies if there is a jog up or down (or
    both), an arrow, or nothing at the start or end of the bracket. If
    the line-end is up or down, the length of the jog can be specified
    using the end-length attribute. The line-type is solid by default.
    """

    class Meta:
        name = "bracket"

    type_value: Optional[StartStop] = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )
    number: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 1,
            "max_inclusive": 6,
        },
    )
    line_end: Optional[LineEnd] = field(
        default=None,
        metadata={
            "name": "line-end",
            "type": "Attribute",
            "required": True,
        },
    )
    end_length: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "end-length",
            "type": "Attribute",
        },
    )
    line_type: Optional[LineType] = field(
        default=None,
        metadata={
            "name": "line-type",
            "type": "Attribute",
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class Cancel(BaseModel):
    """A cancel element indicates that the old key signature should be cancelled
    before the new one appears.

    This will always happen when changing to C major or A minor and need
    not be specified then. The cancel value matches the fifths value of
    the cancelled key signature (e.g., a cancel of -2 will provide an
    explicit cancellation for changing from B flat major to F major).
    The optional location attribute indicates whether the cancellation
    appears to the left or the right of the new key signature. It is
    left by default.
    """

    class Meta:
        name = "cancel"

    value: Optional[int] = field(
        default=None,
        metadata={
            "required": True,
        },
    )
    location: Optional[LeftRight] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Clef(BaseModel):
    """Clefs are represented by a combination of sign, line, and clef-octave-change
    elements.

    The optional number attribute refers to staff numbers within the
    part. A value of 1 is assumed if not present. Sometimes clefs are
    added to the staff in non-standard line positions, either to
    indicate cue passages, or when there are multiple clefs present
    simultaneously on one staff. In this situation, the additional
    attribute is set to "yes" and the line value is ignored. The size
    attribute is used for clefs where the additional attribute is "yes".
    It is typically used to indicate cue clefs.

    :ivar sign: The sign element represents the clef symbol.
    :ivar line: Line numbers are counted from the bottom of the staff.
        Standard values are 2 for the G sign (treble clef), 4 for the F
        sign (bass clef), 3 for the C sign (alto clef) and 5 for TAB (on
        a 6-line staff).
    :ivar clef_octave_change: The clef-octave-change element is used for
        transposing clefs. A treble clef for tenors would have a value
        of -1.
    :ivar number:
    :ivar additional:
    :ivar size:
    :ivar default_x:
    :ivar default_y:
    :ivar relative_x:
    :ivar relative_y:
    :ivar font_family:
    :ivar font_style:
    :ivar font_size:
    :ivar font_weight:
    :ivar color:
    :ivar print_object:
    """

    class Meta:
        name = "clef"

    sign: Optional[ClefSign] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    line: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    clef_octave_change: Optional[int] = field(
        default=None,
        metadata={
            "name": "clef-octave-change",
            "type": "Element",
        },
    )
    number: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    additional: Optional[YesNo] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    size: Optional[SymbolSize] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    print_object: Optional[YesNo] = field(
        default=None,
        metadata={
            "name": "print-object",
            "type": "Attribute",
        },
    )


class Dashes(BaseModel):
    """The dashes type represents dashes, used for instance with cresc.

    and dim. marks.
    """

    class Meta:
        name = "dashes"

    type_value: Optional[StartStop] = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )
    number: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 1,
            "max_inclusive": 6,
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class DegreeAlter(BaseModel):
    """The degree-alter type represents the chromatic alteration for the current
    degree.

    If the degree-type value is alter or subtract, the degree-alter
    value is relative to the degree already in the chord based on its
    kind element. If the degree-type value is add, the degree-alter is
    relative to a dominant chord (major and perfect intervals except for
    a minor seventh). The plus-minus attribute is used to indicate if
    plus and minus symbols should be used instead of sharp and flat
    symbols to display the degree alteration; it is no by default.
    """

    class Meta:
        name = "degree-alter"

    value: Optional[Decimal] = field(
        default=None,
        metadata={
            "required": True,
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    plus_minus: Optional[YesNo] = field(
        default=None,
        metadata={
            "name": "plus-minus",
            "type": "Attribute",
        },
    )


class DegreeType(BaseModel):
    """The degree-type type indicates if this degree is an addition, alteration, or
    subtraction relative to the kind of the current chord.

    The value of the degree-type element affects the interpretation of
    the value of the degree-alter element. The text attribute specifies
    how the type of the degree should be displayed.
    """

    class Meta:
        name = "degree-type"

    value: Optional[DegreeTypeValue] = field(
        default=None,
        metadata={
            "required": True,
        },
    )
    text: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class DegreeValue(BaseModel):
    """The content of the degree-value type is a number indicating the degree of
    the chord (1 for the root, 3 for third, etc).

    The text attribute specifies how the type of the degree should be
    displayed.
    """

    class Meta:
        name = "degree-value"

    value: Optional[int] = field(
        default=None,
        metadata={
            "required": True,
        },
    )
    text: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class DisplayStepOctave(BaseModel):
    """The display-step-octave type contains the sequence of elements used by both
    the rest and unpitched elements.

    This group is used to place rests and unpitched elements on the
    staff without implying that these elements have pitch. Positioning
    follows the current clef. If percussion clef is used, the display-
    step and display-octave elements are interpreted as if in treble
    clef, with a G in octave 4 on line 2. If not present, the note is
    placed on the middle line of the staff, generally used for one-line
    staffs.
    """

    class Meta:
        name = "display-step-octave"

    display_step: Optional[Step] = field(
        default=None,
        metadata={
            "name": "display-step",
            "type": "Element",
        },
    )
    display_octave: Optional[int] = field(
        default=None,
        metadata={
            "name": "display-octave",
            "type": "Element",
            "min_inclusive": 0,
            "max_inclusive": 9,
        },
    )


class Dynamics(BaseModel):
    """Dynamics can be associated either with a note or a general musical
    direction.

    To avoid inconsistencies between and amongst the letter
    abbreviations for dynamics (what is sf vs. sfz, standing alone or
    with a trailing dynamic that is not always piano), we use the actual
    letters as the names of these dynamic elements. The other-dynamics
    element allows other dynamic marks that are not covered here, but
    many of those should perhaps be included in a more general musical
    direction element. Dynamics elements may also be combined to create
    marks not covered by a single element, such as sfmp. These letter
    dynamic symbols are separated from crescendo, decrescendo, and wedge
    indications. Dynamic representation is inconsistent in scores. Many
    things are assumed by the composer and left out, such as returns to
    original dynamics. Systematic representations are quite complex: for
    example, Humdrum has at least 3 representation formats related to
    dynamics. The MusicXML format captures what is in the score, but
    does not try to be optimal for analysis or synthesis of dynamics.
    """

    class Meta:
        name = "dynamics"

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
    other_dynamics: list[str] = field(
        default_factory=list,
        metadata={
            "name": "other-dynamics",
            "type": "Element",
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    placement: Optional[AboveBelow] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Elision(BaseModel):
    """In Version 2.0, the content of the elision type is used to specify the
    symbol used to display the elision.

    Common values are a no-break space (Unicode 00A0), an underscore
    (Unicode 005F), or an undertie (Unicode 203F).
    """

    class Meta:
        name = "elision"

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class EmptyFont(BaseModel):
    """
    The empty-font type represents an empty element with font attributes.
    """

    class Meta:
        name = "empty-font"

    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )


class EmptyLine(BaseModel):
    """
    The empty-line type represents an empty element with line-shape, line-type,
    print-style and placement attributes.
    """

    class Meta:
        name = "empty-line"

    line_shape: Optional[LineShape] = field(
        default=None,
        metadata={
            "name": "line-shape",
            "type": "Attribute",
        },
    )
    line_type: Optional[LineType] = field(
        default=None,
        metadata={
            "name": "line-type",
            "type": "Attribute",
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    placement: Optional[AboveBelow] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class EmptyPlacement(BaseModel):
    """
    The empty-placement type represents an empty element with print-style and
    placement attributes.
    """

    class Meta:
        name = "empty-placement"

    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    placement: Optional[AboveBelow] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class EmptyPrintStyle(BaseModel):
    """
    The empty-print-style type represents an empty element with print-style
    attributes.
    """

    class Meta:
        name = "empty-print-style"

    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class EmptyTrillSound(BaseModel):
    """
    The empty-trill-sound type represents an empty element with print-style,
    placement, and trill-sound attributes.
    """

    class Meta:
        name = "empty-trill-sound"

    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    placement: Optional[AboveBelow] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    start_note: Optional[StartNote] = field(
        default=None,
        metadata={
            "name": "start-note",
            "type": "Attribute",
        },
    )
    trill_step: Optional[TrillStep] = field(
        default=None,
        metadata={
            "name": "trill-step",
            "type": "Attribute",
        },
    )
    two_note_turn: Optional[TwoNoteTurn] = field(
        default=None,
        metadata={
            "name": "two-note-turn",
            "type": "Attribute",
        },
    )
    accelerate: Optional[YesNo] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    beats: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": Decimal("2"),
        },
    )
    second_beat: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "second-beat",
            "type": "Attribute",
            "min_inclusive": Decimal("0"),
            "max_inclusive": Decimal("100"),
        },
    )
    last_beat: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "last-beat",
            "type": "Attribute",
            "min_inclusive": Decimal("0"),
            "max_inclusive": Decimal("100"),
        },
    )


class Ending(BaseModel):
    """The ending type represents multiple (e.g. first and second) endings.

    Typically, the start type is associated with the left barline of the
    first measure in an ending. The stop and discontinue types are
    associated with the right barline of the last measure in an ending.
    Stop is used when the ending mark concludes with a downward jog, as
    is typical for first endings. Discontinue is used when there is no
    downward jog, as is typical for second endings that do not conclude
    a piece. The length of the jog can be specified using the end-length
    attribute. The text-x and text-y attributes are offsets that specify
    where the baseline of the start of the ending text appears, relative
    to the start of the ending line. The number attribute reflects the
    numeric values of what is under the ending line. Single endings such
    as "1" or comma-separated multiple endings such as "1,2" may be
    used. The ending element text is used when the text displayed in the
    ending is different than what appears in the number attribute. The
    print-object element is used to indicate when an ending is present
    but not printed, as is often the case for many parts in a full
    score.
    """

    class Meta:
        name = "ending"

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    number: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "pattern": r"([ ]*)|([1-9][0-9]*(, ?[1-9][0-9]*)*)",
        },
    )
    type_value: Optional[StartStopDiscontinue] = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )
    print_object: Optional[YesNo] = field(
        default=None,
        metadata={
            "name": "print-object",
            "type": "Attribute",
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    end_length: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "end-length",
            "type": "Attribute",
        },
    )
    text_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "text-x",
            "type": "Attribute",
        },
    )
    text_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "text-y",
            "type": "Attribute",
        },
    )


class Extend(BaseModel):
    """
    The extend type represents word extensions for lyrics.
    """

    class Meta:
        name = "extend"

    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class Fermata(BaseModel):
    """The fermata text content represents the shape of the fermata sign.

    An empty fermata element represents a normal fermata. The fermata
    type is upright if not specified.
    """

    class Meta:
        name = "fermata"

    value: Optional[FermataShape] = field(
        default=None,
        metadata={
            "required": True,
        },
    )
    type_value: Optional[UprightInverted] = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class Fingering(BaseModel):
    """Fingering is typically indicated 1,2,3,4,5.

    Multiple fingerings may be given, typically to substitute fingerings
    in the middle of a note. The substitution and alternate values are
    "no" if the attribute is not present. For guitar and other fretted
    instruments, the fingering element represents the fretting finger;
    the pluck element represents the plucking finger.
    """

    class Meta:
        name = "fingering"

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    substitution: Optional[YesNo] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    alternate: Optional[YesNo] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    placement: Optional[AboveBelow] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class FirstFret(BaseModel):
    """The first-fret type indicates which fret is shown in the top space of the
    frame; it is fret 1 if the element is not present.

    The optional text attribute indicates how this is represented in the
    fret diagram, while the location attribute indicates whether the
    text appears to the left or right of the frame.
    """

    class Meta:
        name = "first-fret"

    value: Optional[int] = field(
        default=None,
        metadata={
            "required": True,
        },
    )
    text: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    location: Optional[LeftRight] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class FormattedText(BaseModel):
    """
    The formatted-text type represents a text element with text-formatting
    attributes.
    """

    class Meta:
        name = "formatted-text"

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    justify: Optional[LeftCenterRight] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    halign: Optional[LeftCenterRight] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    valign: Optional[Valign] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    underline: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 3,
        },
    )
    overline: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 3,
        },
    )
    line_through: Optional[int] = field(
        default=None,
        metadata={
            "name": "line-through",
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 3,
        },
    )
    rotation: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": Decimal("-180"),
            "max_inclusive": Decimal("180"),
        },
    )
    letter_spacing: Optional[Union[Decimal, NumberOrNormalValue]] = field(
        default=None,
        metadata={
            "name": "letter-spacing",
            "type": "Attribute",
        },
    )
    line_height: Optional[Union[Decimal, NumberOrNormalValue]] = field(
        default=None,
        metadata={
            "name": "line-height",
            "type": "Attribute",
        },
    )
    lang: Optional[Union[str, LangValue]] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "namespace": XML_NS,
        },
    )
    direction: Optional[TextDirection] = field(
        default=None,
        metadata={
            "name": "dir",
            "type": "Attribute",
        },
    )
    enclosure: Optional[Enclosure] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Fret(BaseModel):
    """The fret element is used with tablature notation and chord diagrams.

    Fret numbers start with 0 for an open string and 1 for the first
    fret.
    """

    class Meta:
        name = "fret"

    value: Optional[int] = field(
        default=None,
        metadata={
            "required": True,
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class Glissando(BaseModel):
    """Glissando and slide types both indicate rapidly moving from one pitch to the
    other so that individual notes are not discerned.

    The distinction is similar to that between NIFF's glissando and
    portamento elements. A glissando sounds the half notes in between
    the slide and defaults to a wavy line. The optional text is printed
    alongside the line.
    """

    class Meta:
        name = "glissando"

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    type_value: Optional[StartStop] = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )
    number: int = field(
        default=1,
        metadata={
            "type": "Attribute",
            "min_inclusive": 1,
            "max_inclusive": 6,
        },
    )
    line_type: Optional[LineType] = field(
        default=None,
        metadata={
            "name": "line-type",
            "type": "Attribute",
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class Grace(BaseModel):
    """The grace type indicates the presence of a grace note.

    The slash attribute for a grace note is yes for slashed eighth
    notes. The other grace note attributes come from MuseData sound
    suggestions. Steal-time-previous indicates the percentage of time to
    steal from the previous note for the grace note. Steal-time-
    following indicates the percentage of time to steal from the
    following note for the grace note. Make-time indicates to make time,
    not steal time; the units are in real-time divisions for the grace
    note.
    """

    class Meta:
        name = "grace"

    steal_time_previous: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "steal-time-previous",
            "type": "Attribute",
            "min_inclusive": Decimal("0"),
            "max_inclusive": Decimal("100"),
        },
    )
    steal_time_following: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "steal-time-following",
            "type": "Attribute",
            "min_inclusive": Decimal("0"),
            "max_inclusive": Decimal("100"),
        },
    )
    make_time: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "make-time",
            "type": "Attribute",
        },
    )
    slash: Optional[YesNo] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class GroupBarline(BaseModel):
    """
    The group-barline type indicates if the group should have common barlines.
    """

    class Meta:
        name = "group-barline"

    value: Optional[GroupBarlineValue] = field(
        default=None,
        metadata={
            "required": True,
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class GroupName(BaseModel):
    """The group-name type describes the name or abbreviation of a part-group
    element.

    Formatting attributes in the group-name type are deprecated in
    Version 2.0 in favor of the new group-name-display and group-
    abbreviation-display elements.
    """

    class Meta:
        name = "group-name"

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    justify: Optional[LeftCenterRight] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class GroupSymbol(BaseModel):
    """
    The group-symbol type indicates how the symbol for a group is indicated in the
    score.
    """

    class Meta:
        name = "group-symbol"

    value: Optional[GroupSymbolValue] = field(
        default=None,
        metadata={
            "required": True,
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class Grouping(BaseModel):
    """The grouping type is used for musical analysis.

    When the type attribute is "start" or "single", it usually contains
    one or more feature elements. The number attribute is used for
    distinguishing between overlapping and hierarchical groupings. The
    member-of attribute allows for easy distinguishing of what grouping
    elements are in what hierarchy. Feature elements contained within a
    "stop" type of grouping may be ignored. This element is flexible to
    allow for different types of analyses. Future versions of the
    MusicXML format may add elements that can represent more
    standardized categories of analysis data, allowing for easier data
    sharing.
    """

    class Meta:
        name = "grouping"

    feature: list[Feature] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    type_value: Optional[StartStopSingle] = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )
    number: str = field(
        default="1",
        metadata={
            "type": "Attribute",
        },
    )
    member_of: Optional[str] = field(
        default=None,
        metadata={
            "name": "member-of",
            "type": "Attribute",
        },
    )


class HammerOnPullOff(BaseModel):
    """The hammer-on and pull-off elements are used in guitar and fretted
    instrument notation.

    Since a single slur can be marked over many notes, the hammer-on and
    pull-off elements are separate so the individual pair of notes can
    be specified. The element content can be used to specify how the
    hammer-on or pull-off should be notated. An empty element leaves
    this choice up to the application.
    """

    class Meta:
        name = "hammer-on-pull-off"

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    type_value: Optional[StartStop] = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )
    number: int = field(
        default=1,
        metadata={
            "type": "Attribute",
            "min_inclusive": 1,
            "max_inclusive": 6,
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    placement: Optional[AboveBelow] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Harmonic(BaseModel):
    """The harmonic type indicates natural and artificial harmonics.

    Allowing the type of pitch to be specified, combined with controls
    for appearance/playback differences, allows both the notation and
    the sound to be represented. Artificial harmonics can add a notated
    touching-pitch; artificial pinch harmonics will usually not notate a
    touching pitch. The attributes for the harmonic element refer to the
    use of the circular harmonic symbol, typically but not always used
    with natural harmonics.

    :ivar natural: The natural element indicates that this is a natural
        harmonic. These are usually notated at base pitch rather than
        sounding pitch.
    :ivar artificial: The artificial element indicates that this is an
        artificial harmonic.
    :ivar base_pitch: The base pitch is the pitch at which the string is
        played before touching to create the harmonic.
    :ivar touching_pitch: The touching-pitch is the pitch at which the
        string is touched lightly to produce the harmonic.
    :ivar sounding_pitch: The sounding-pitch is the pitch which is heard
        when playing the harmonic.
    :ivar print_object:
    :ivar default_x:
    :ivar default_y:
    :ivar relative_x:
    :ivar relative_y:
    :ivar font_family:
    :ivar font_style:
    :ivar font_size:
    :ivar font_weight:
    :ivar color:
    :ivar placement:
    """

    class Meta:
        name = "harmonic"

    natural: Optional[Empty] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    artificial: Optional[Empty] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    base_pitch: Optional[Empty] = field(
        default=None,
        metadata={
            "name": "base-pitch",
            "type": "Element",
        },
    )
    touching_pitch: Optional[Empty] = field(
        default=None,
        metadata={
            "name": "touching-pitch",
            "type": "Element",
        },
    )
    sounding_pitch: Optional[Empty] = field(
        default=None,
        metadata={
            "name": "sounding-pitch",
            "type": "Element",
        },
    )
    print_object: Optional[YesNo] = field(
        default=None,
        metadata={
            "name": "print-object",
            "type": "Attribute",
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    placement: Optional[AboveBelow] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Image(BaseModel):
    """
    The image type is used to include graphical images in a score.
    """

    class Meta:
        name = "image"

    source: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    type_value: Optional[str] = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    halign: Optional[LeftCenterRight] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    valign: Optional[ValignImage] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Inversion(BaseModel):
    """The inversion type represents harmony inversions.

    The value is a number indicating which inversion is used: 0 for root position, 1 for first inversion, etc.
    """

    class Meta:
        name = "inversion"

    value: Optional[int] = field(
        default=None,
        metadata={
            "required": True,
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class KeyOctave(BaseModel):
    """The key-octave element specifies in which octave an element of a key
    signature appears.

    The content specifies the octave value using the same values as the
    display-octave element. The number attribute is a positive integer
    that refers to the key signature element in left-to-right order. If
    the cancel attribute is set to yes, then this number refers to an
    element specified by the cancel element. It is no by default.
    """

    class Meta:
        name = "key-octave"

    value: Optional[int] = field(
        default=None,
        metadata={
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 9,
        },
    )
    number: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    cancel: Optional[YesNo] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Kind(BaseModel):
    """Kind indicates the type of chord.

    Degree elements can then add, subtract, or alter from these starting points
    The attributes are used to indicate the formatting of the symbol. Since the kind element is the constant in all the harmony-chord groups that can make up a polychord, many formatting attributes are here.
    The use-symbols attribute is yes if the kind should be represented when possible with harmony symbols rather than letters and numbers. These symbols include:
    major: a triangle, like Unicode 25B3
    minor: -, like Unicode 002D
    augmented: +, like Unicode 002B
    diminished: °, like Unicode 00B0
    half-diminished: ø, like Unicode 00F8
    The text attribute describes how the kind should be spelled if not using symbols; it is ignored if use-symbols is yes. The stack-degrees attribute is yes if the degree elements should be stacked above each other. The parentheses-degrees attribute is yes if all the degrees should be in parentheses. The bracket-degrees attribute is yes if all the degrees should be in a bracket. If not specified, these values are implementation-specific. The alignment attributes are for the entire harmony-chord group of which this kind element is a part.
    """

    class Meta:
        name = "kind"

    value: Optional[KindValue] = field(
        default=None,
        metadata={
            "required": True,
        },
    )
    use_symbols: Optional[YesNo] = field(
        default=None,
        metadata={
            "name": "use-symbols",
            "type": "Attribute",
        },
    )
    text: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    stack_degrees: Optional[YesNo] = field(
        default=None,
        metadata={
            "name": "stack-degrees",
            "type": "Attribute",
        },
    )
    parentheses_degrees: Optional[YesNo] = field(
        default=None,
        metadata={
            "name": "parentheses-degrees",
            "type": "Attribute",
        },
    )
    bracket_degrees: Optional[YesNo] = field(
        default=None,
        metadata={
            "name": "bracket-degrees",
            "type": "Attribute",
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    halign: Optional[LeftCenterRight] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    valign: Optional[Valign] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Level(BaseModel):
    """The level type is used to specify editorial information for different
    MusicXML elements.

    If the reference attribute for the level element is yes, this
    indicates editorial information that is for display only and should
    not affect playback. For instance, a modern edition of older music
    may set reference="yes" on the attributes containing the music's
    original clef, key, and time signature. It is no by default.
    """

    class Meta:
        name = "level"

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    reference: Optional[YesNo] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    parentheses: Optional[YesNo] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    bracket: Optional[YesNo] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    size: Optional[SymbolSize] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Link(BaseModel):
    """The link type serves as an outgoing simple XLink.

    It is also used to connect a MusicXML score with a MusicXML opus.
    """

    class Meta:
        name = "link"

    href: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "namespace": XLINK_NS,
            "required": True,
        },
    )
    type_value: TypeValue = field(
        init=False,
        default=TypeValue.SIMPLE,
        metadata={
            "name": "type",
            "type": "Attribute",
            "namespace": XLINK_NS,
        },
    )
    role: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "namespace": XLINK_NS,
        },
    )
    title: Optional[str] = field(
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
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    element: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    position: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )


class LyricFont(BaseModel):
    """
    The lyric-font type specifies the default font for a particular name and number
    of lyric.
    """

    class Meta:
        name = "lyric-font"

    number: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )


class LyricLanguage(BaseModel):
    """
    The lyric-language type specifies the default language for a particular name
    and number of lyric.
    """

    class Meta:
        name = "lyric-language"

    number: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    lang: Optional[Union[str, LangValue]] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "namespace": XML_NS,
            "required": True,
        },
    )


class MeasureNumbering(BaseModel):
    """The measure-numbering type describes how frequently measure numbers are
    displayed on this part.

    The number attribute from the measure element is used for printing.
    Measures with an implicit attribute set to "yes" never display a
    measure number, regardless of the measure-numbering setting.
    """

    class Meta:
        name = "measure-numbering"

    value: Optional[MeasureNumberingValue] = field(
        default=None,
        metadata={
            "required": True,
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class MeasureRepeat(BaseModel):
    """The measure-repeat type is used for both single and multiple measure
    repeats.

    The text of the element indicates the number of measures to be
    repeated in a single pattern. The slashes attribute specifies the
    number of slashes to use in the repeat sign. It is 1 if not
    specified. Both the start and the stop of the measure-repeat must be
    specified. The text of the element is ignored when the type is stop.
    The measure-repeat element specifies a notation style for
    repetitions. The actual music being repeated needs to be repeated
    within the MusicXML file. This element specifies the notation that
    indicates the repeat.
    """

    class Meta:
        name = "measure-repeat"

    value: Optional[Union[int, PositiveIntegerOrEmptyValue]] = field(default=None)
    type_value: Optional[StartStop] = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )
    slashes: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class MetronomeBeam(BaseModel):
    """
    The metronome-beam type works like the beam type in defining metric
    relationships, but does not include all the attributes available in the beam
    type.
    """

    class Meta:
        name = "metronome-beam"

    value: Optional[BeamValue] = field(
        default=None,
        metadata={
            "required": True,
        },
    )
    number: int = field(
        default=1,
        metadata={
            "type": "Attribute",
            "min_inclusive": 1,
            "max_inclusive": 6,
        },
    )


class Miscellaneous(BaseModel):
    """If a program has other metadata not yet supported in the MusicXML format, it
    can go in the miscellaneous element.

    The miscellaneous type puts each separate part of metadata into its
    own miscellaneous-field type.
    """

    class Meta:
        name = "miscellaneous"

    miscellaneous_field: list[MiscellaneousField] = field(
        default_factory=list,
        metadata={
            "name": "miscellaneous-field",
            "type": "Element",
        },
    )


class MultipleRest(BaseModel):
    """The text of the multiple-rest type indicates the number of measures in the
    multiple rest.

    Multiple rests may use the 1-bar / 2-bar / 4-bar rest symbols, or a
    single shape. The use-symbols attribute indicates which to use; it
    is no if not specified. The element text is ignored when the type is
    stop.
    """

    class Meta:
        name = "multiple-rest"

    value: Optional[Union[int, PositiveIntegerOrEmptyValue]] = field(default=None)
    use_symbols: Optional[YesNo] = field(
        default=None,
        metadata={
            "name": "use-symbols",
            "type": "Attribute",
        },
    )


class NonArpeggiate(BaseModel):
    """The non-arpeggiate type indicates that this note is at the top or bottom of
    a bracket indicating to not arpeggiate these notes.

    Since this does not involve playback, it is only used on the top or
    bottom notes, not on each note as for the arpeggiate type.
    """

    class Meta:
        name = "non-arpeggiate"

    type_value: Optional[TopBottom] = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )
    number: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 1,
            "max_inclusive": 6,
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    placement: Optional[AboveBelow] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class NoteSize(BaseModel):
    """The note-size type indicates the percentage of the regular note size to use
    for notes with a cue and large size as defined in the type element.

    The grace type is used for notes of cue size that that include a
    grace element. The cue type is used for all other notes with cue
    size, whether defined explicitly or implicitly via a cue element.
    The large type is used for notes of large size. The text content
    represent the numeric percentage. A value of 100 would be identical
    to the size of a regular note as defined by the music font.
    """

    class Meta:
        name = "note-size"

    value: Optional[Decimal] = field(
        default=None,
        metadata={
            "required": True,
            "min_inclusive": Decimal("0"),
        },
    )
    type_value: Optional[NoteSizeType] = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )


class NoteType(BaseModel):
    """The note-type type indicates the graphic note type.

    Values range from 256th to long. The size attribute indicates full,
    cue, or large size, with full the default for regular notes and cue
    the default for cue and grace notes.
    """

    class Meta:
        name = "note-type"

    value: Optional[NoteTypeValue] = field(
        default=None,
        metadata={
            "required": True,
        },
    )
    size: Optional[SymbolSize] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Notehead(BaseModel):
    """The notehead element indicates shapes other than the open and closed ovals
    associated with note durations.

    For the enclosed shapes, the default is to be hollow for half notes
    and longer, and filled otherwise. The filled attribute can be set to
    change this if needed. If the parentheses attribute is set to yes,
    the notehead is parenthesized. It is no by default.
    """

    class Meta:
        name = "notehead"

    value: Optional[NoteheadValue] = field(
        default=None,
        metadata={
            "required": True,
        },
    )
    filled: Optional[YesNo] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    parentheses: Optional[YesNo] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class OctaveShift(BaseModel):
    """The octave shift type indicates where notes are shifted up or down from
    their true pitched values because of printing difficulty.

    Thus a treble clef line noted with 8va will be indicated with an
    octave-shift down from the pitch data indicated in the notes. A size
    of 8 indicates one octave; a size of 15 indicates two octaves.
    """

    class Meta:
        name = "octave-shift"

    type_value: Optional[UpDownStop] = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )
    number: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 1,
            "max_inclusive": 6,
        },
    )
    size: int = field(
        default=8,
        metadata={
            "type": "Attribute",
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class Offset(BaseModel):
    """An offset is represented in terms of divisions, and indicates where the
    direction will appear relative to the current musical location.

    This affects the visual appearance of the direction. If the sound
    attribute is "yes", then the offset affects playback too. If the
    sound attribute is "no", then any sound associated with the
    direction takes effect at the current location. The sound attribute
    is "no" by default for compatibility with earlier versions of the
    MusicXML format. If an element within a direction includes a
    default-x attribute, the offset value will be ignored when
    determining the appearance of that element.
    """

    class Meta:
        name = "offset"

    value: Optional[Decimal] = field(
        default=None,
        metadata={
            "required": True,
        },
    )
    sound: Optional[YesNo] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Opus(BaseModel):
    """
    The opus type represents a link to a MusicXML opus document that composes
    multiple MusicXML scores into a collection.
    """

    class Meta:
        name = "opus"

    href: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "namespace": XLINK_NS,
            "required": True,
        },
    )
    type_value: TypeValue = field(
        init=False,
        default=TypeValue.SIMPLE,
        metadata={
            "name": "type",
            "type": "Attribute",
            "namespace": XLINK_NS,
        },
    )
    role: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "namespace": XLINK_NS,
        },
    )
    title: Optional[str] = field(
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
    """The other-direction type is used to define any direction symbols not yet in
    the current version of the MusicXML format.

    This allows extended representation, though without application
    interoperability.
    """

    class Meta:
        name = "other-direction"

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    print_object: Optional[YesNo] = field(
        default=None,
        metadata={
            "name": "print-object",
            "type": "Attribute",
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class OtherNotation(BaseModel):
    """The other-notation type is used to define any notations not yet in the
    MusicXML format.

    This allows extended representation, though without application
    interoperability. It handles notations where more specific extension
    elements such as other-dynamics and other-technical are not
    appropriate.
    """

    class Meta:
        name = "other-notation"

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    type_value: Optional[StartStopSingle] = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )
    number: int = field(
        default=1,
        metadata={
            "type": "Attribute",
            "min_inclusive": 1,
            "max_inclusive": 6,
        },
    )
    print_object: Optional[YesNo] = field(
        default=None,
        metadata={
            "name": "print-object",
            "type": "Attribute",
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    placement: Optional[AboveBelow] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class PageMargins(BaseModel):
    """Page margins are specified either for both even and odd pages, or via
    separate odd and even page number values.

    The type attribute is not needed when used as part of a print
    element. If omitted when the page-margins type is used in the
    defaults element, "both" is the default value.
    """

    class Meta:
        name = "page-margins"

    left_margin: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "left-margin",
            "type": "Element",
            "required": True,
        },
    )
    right_margin: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "right-margin",
            "type": "Element",
            "required": True,
        },
    )
    top_margin: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "top-margin",
            "type": "Element",
            "required": True,
        },
    )
    bottom_margin: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "bottom-margin",
            "type": "Element",
            "required": True,
        },
    )
    type_value: Optional[MarginType] = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
        },
    )


class PartName(BaseModel):
    """The part-name type describes the name or abbreviation of a score-part
    element.

    Formatting attributes for the part-name element are deprecated in
    Version 2.0 in favor of the new part-name-display and part-
    abbreviation-display elements.
    """

    class Meta:
        name = "part-name"

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    print_object: Optional[YesNo] = field(
        default=None,
        metadata={
            "name": "print-object",
            "type": "Attribute",
        },
    )
    justify: Optional[LeftCenterRight] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class PartSymbol(BaseModel):
    """The part-symbol element indicates how a symbol for a multi-staff part is
    indicated in the score.

    Values include none, brace, line, and bracket; brace is the default.
    The top-staff and bottom-staff elements are used when the brace does
    not extend across the entire part. For example, in a 3-staff organ
    part, the top-staff will typically be 1 for the right hand, while
    the bottom-staff will typically be 2 for the left hand. Staff 3 for
    the pedals is usually outside the brace.
    """

    class Meta:
        name = "part-symbol"

    value: Optional[GroupSymbolValue] = field(
        default=None,
        metadata={
            "required": True,
        },
    )
    top_staff: Optional[int] = field(
        default=None,
        metadata={
            "name": "top-staff",
            "type": "Attribute",
        },
    )
    bottom_staff: Optional[int] = field(
        default=None,
        metadata={
            "name": "bottom-staff",
            "type": "Attribute",
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class Pedal(BaseModel):
    """The pedal type represents piano pedal marks.

    The line attribute is yes if pedal lines are used, no if Ped and *
    signs are used. The change type is used with line set to yes.
    """

    class Meta:
        name = "pedal"

    type_value: Optional[StartStopChange] = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )
    line: Optional[YesNo] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class PedalTuning(BaseModel):
    """
    The pedal-tuning type specifies the tuning of a single harp pedal.

    :ivar pedal_step: The pedal-step element defines the pitch step for
        a single harp pedal.
    :ivar pedal_alter: The pedal-alter element defines the chromatic
        alteration for a single harp pedal.
    """

    class Meta:
        name = "pedal-tuning"

    pedal_step: Optional[Step] = field(
        default=None,
        metadata={
            "name": "pedal-step",
            "type": "Element",
            "required": True,
        },
    )
    pedal_alter: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "pedal-alter",
            "type": "Element",
            "required": True,
        },
    )


class PerMinute(BaseModel):
    """The per-minute type can be a number, or a text description including
    numbers.

    If a font is specified, it overrides the font specified for the
    overall metronome element. This allows separate specification of a
    music font for the beat-unit and a text font for the numeric value,
    in cases where a single metronome font is not used.
    """

    class Meta:
        name = "per-minute"

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )


class Pitch(BaseModel):
    """
    Pitch is represented as a combination of the step of the diatonic scale, the
    chromatic alteration, and the octave.
    """

    class Meta:
        name = "pitch"

    step: Optional[Step] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    alter: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    octave: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 9,
        },
    )


class PlacementText(BaseModel):
    """
    The placement-text type represents a text element with print-style and
    placement attribute groups.
    """

    class Meta:
        name = "placement-text"

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    placement: Optional[AboveBelow] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Rehearsal(BaseModel):
    """The rehearsal type specifies a rehearsal mark.

    Language is Italian ("it") by default. Enclosure is square by
    default.
    """

    class Meta:
        name = "rehearsal"

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    underline: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 3,
        },
    )
    overline: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 3,
        },
    )
    line_through: Optional[int] = field(
        default=None,
        metadata={
            "name": "line-through",
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 3,
        },
    )
    lang: Optional[Union[str, LangValue]] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "namespace": XML_NS,
        },
    )
    direction: Optional[TextDirection] = field(
        default=None,
        metadata={
            "name": "dir",
            "type": "Attribute",
        },
    )
    rotation: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": Decimal("-180"),
            "max_inclusive": Decimal("180"),
        },
    )
    enclosure: Optional[RehearsalEnclosure] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Repeat(BaseModel):
    """The repeat type represents repeat marks.

    The start of the repeat has a forward direction while the end of the
    repeat has a backward direction. Backward repeats that are not part
    of an ending can use the times attribute to indicate the number of
    times the repeated section is played.
    """

    class Meta:
        name = "repeat"

    direction: Optional[BackwardForward] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    times: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class RootAlter(BaseModel):
    """The root-alter type represents the chromatic alteration of the root of the
    current chord within the harmony element.

    In some chord styles, the text for the root-step element may include
    root-alter information. In that case, the print-object attribute of
    the root-alter element can be set to no. The location attribute
    indicates whether the alteration should appear to the left or the
    right of the root-step; it is right by default.
    """

    class Meta:
        name = "root-alter"

    value: Optional[Decimal] = field(
        default=None,
        metadata={
            "required": True,
        },
    )
    print_object: Optional[YesNo] = field(
        default=None,
        metadata={
            "name": "print-object",
            "type": "Attribute",
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    location: Optional[LeftRight] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class RootStep(BaseModel):
    """The root-step type represents the pitch step of the root of the current
    chord within the harmony element.

    The text attribute indicates how the root should appear on the page
    if not using the element contents.
    """

    class Meta:
        name = "root-step"

    value: Optional[Step] = field(
        default=None,
        metadata={
            "required": True,
        },
    )
    text: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class ScoreInstrument(BaseModel):
    """The score-instrument type represents a single instrument within a score-
    part.

    As with the score-part type, each score-instrument has a required ID
    attribute, a name, and an optional abbreviation. A score-instrument
    type is also required if the score specifies MIDI 1.0 channels,
    banks, or programs. An initial midi-instrument assignment can also
    be made here. MusicXML software should be able to automatically
    assign reasonable channels and instruments without these elements in
    simple cases, such as where part names match General MIDI instrument
    names.

    :ivar instrument_name: The instrument-name element is typically used
        within a software application, rather than appearing on the
        printed page of a score.
    :ivar instrument_abbreviation: The optional instrument-abbreviation
        element is typically used within a software application, rather
        than appearing on the printed page of a score.
    :ivar solo: The solo element was added in Version 2.0. It is present
        if performance is intended by a solo instrument.
    :ivar ensemble: The ensemble element was added in Version 2.0. It is
        present if performance is intended by an ensemble such as an
        orchestral section. The text of the ensemble element contains
        the size of the section, or is empty if the ensemble size is not
        specified.
    :ivar id:
    """

    class Meta:
        name = "score-instrument"

    instrument_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "instrument-name",
            "type": "Element",
            "required": True,
        },
    )
    instrument_abbreviation: Optional[str] = field(
        default=None,
        metadata={
            "name": "instrument-abbreviation",
            "type": "Element",
        },
    )
    solo: Optional[Empty] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    ensemble: Optional[Union[int, PositiveIntegerOrEmptyValue]] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    score_instrument_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "id",
            "type": "Attribute",
            "required": True,
        },
    )


class Slash(BaseModel):
    """The slash type is used to indicate that slash notation is to be used.

    If the slash is on every beat, use-stems is no (the default). To
    indicate rhythms but not pitches, use-stems is set to yes. The type
    attribute indicates whether this is the start or stop of a slash
    notation style. The use-dots attribute works as for the beat-repeat
    element, and only has effect if use-stems is no.

    :ivar slash_type: The slash-type element indicates the graphical
        note type to use for the display of repetition marks.
    :ivar slash_dot: The slash-dot element is used to specify any
        augmentation dots in the note type used to display repetition
        marks.
    :ivar type_value:
    :ivar use_dots:
    :ivar use_stems:
    """

    class Meta:
        name = "slash"

    slash_type: Optional[NoteTypeValue] = field(
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
    type_value: Optional[StartStop] = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )
    use_dots: Optional[YesNo] = field(
        default=None,
        metadata={
            "name": "use-dots",
            "type": "Attribute",
        },
    )
    use_stems: Optional[YesNo] = field(
        default=None,
        metadata={
            "name": "use-stems",
            "type": "Attribute",
        },
    )


class Slide(BaseModel):
    """Glissando and slide types both indicate rapidly moving from one pitch to the
    other so that individual notes are not discerned.

    The distinction is similar to that between NIFF's glissando and
    portamento elements. A slide is continuous between two notes and
    defaults to a solid line. The optional text for a is printed
    alongside the line.
    """

    class Meta:
        name = "slide"

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    type_value: Optional[StartStop] = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )
    number: int = field(
        default=1,
        metadata={
            "type": "Attribute",
            "min_inclusive": 1,
            "max_inclusive": 6,
        },
    )
    line_type: Optional[LineType] = field(
        default=None,
        metadata={
            "name": "line-type",
            "type": "Attribute",
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    accelerate: Optional[YesNo] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    beats: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": Decimal("2"),
        },
    )
    first_beat: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "first-beat",
            "type": "Attribute",
            "min_inclusive": Decimal("0"),
            "max_inclusive": Decimal("100"),
        },
    )
    last_beat: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "last-beat",
            "type": "Attribute",
            "min_inclusive": Decimal("0"),
            "max_inclusive": Decimal("100"),
        },
    )


class Slur(BaseModel):
    """Slur types are empty.

    Most slurs are represented with two elements: one with a start type, and one with a stop type. Slurs can add more elements using a continue type. This is typically used to specify the formatting of cross-system slurs, or to specify the shape of very complex slurs.
    """

    class Meta:
        name = "slur"

    type_value: Optional[StartStopContinue] = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )
    number: int = field(
        default=1,
        metadata={
            "type": "Attribute",
            "min_inclusive": 1,
            "max_inclusive": 6,
        },
    )
    line_type: Optional[LineType] = field(
        default=None,
        metadata={
            "name": "line-type",
            "type": "Attribute",
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    placement: Optional[AboveBelow] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    orientation: Optional[OverUnder] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    bezier_offset: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "bezier-offset",
            "type": "Attribute",
        },
    )
    bezier_offset2: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "bezier-offset2",
            "type": "Attribute",
        },
    )
    bezier_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "bezier-x",
            "type": "Attribute",
        },
    )
    bezier_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "bezier-y",
            "type": "Attribute",
        },
    )
    bezier_x2: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "bezier-x2",
            "type": "Attribute",
        },
    )
    bezier_y2: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "bezier-y2",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class StaffTuning(BaseModel):
    """
    The staff-tuning type specifies the open, non-capo tuning of the lines on a
    tablature staff.

    :ivar tuning_step: The tuning-step element is represented like the
        step element, with a different name to reflect is different
        function.
    :ivar tuning_alter: The tuning-alter element is represented like the
        alter element, with a different name to reflect is different
        function.
    :ivar tuning_octave: The tuning-octave element is represented like
        the octave element, with a different name to reflect is
        different function.
    :ivar line:
    """

    class Meta:
        name = "staff-tuning"

    tuning_step: Optional[Step] = field(
        default=None,
        metadata={
            "name": "tuning-step",
            "type": "Element",
            "required": True,
        },
    )
    tuning_alter: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "tuning-alter",
            "type": "Element",
        },
    )
    tuning_octave: Optional[int] = field(
        default=None,
        metadata={
            "name": "tuning-octave",
            "type": "Element",
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 9,
        },
    )
    line: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Stem(BaseModel):
    """Stems can be down, up, none, or double.

    For down and up stems, the position attributes can be used to
    specify stem length. The relative values specify the end of the stem
    relative to the program default. Default values specify an absolute
    end stem position. Negative values of relative-y that would flip a
    stem instead of shortening it are ignored.
    """

    class Meta:
        name = "stem"

    value: Optional[StemValue] = field(
        default=None,
        metadata={
            "required": True,
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class String(BaseModel):
    """The string type is used with tablature notation, regular notation (where it
    is often circled), and chord diagrams.

    String numbers start with 1 for the highest string.
    """

    class Meta:
        name = "string"

    value: Optional[int] = field(
        default=None,
        metadata={
            "required": True,
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    placement: Optional[AboveBelow] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class StyleText(BaseModel):
    """
    The style-text type represents a text element with a print-style attribute
    group.
    """

    class Meta:
        name = "style-text"

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class Supports(BaseModel):
    """The supports type indicates if a MusicXML encoding supports a particular
    MusicXML element.

    This is recommended for elements like beam, stem, and accidental,
    where the absence of an element is ambiguous if you do not know if
    the encoding supports that element. For Version 2.0, the supports
    element is expanded to allow programs to indicate support for
    particular attributes or particular values. This lets applications
    communicate, for example, that all system and/or page breaks are
    contained in the MusicXML file.
    """

    class Meta:
        name = "supports"

    type_value: Optional[YesNo] = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )
    element: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    attribute: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    value: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class SystemLayout(BaseModel):
    """System layout includes left and right margins and the vertical distance from
    the previous system.

    The system distance is measured from the bottom line of the previous
    system to the top line of the current system. It is ignored for the
    first system on a page. The top system distance is measured from the
    page's top margin to the top line of the first system. It is ignored
    for all but the first system on a page. Sometimes the sum of measure
    widths in a system may not equal the system width specified by the
    layout elements due to roundoff or other errors. The behavior when
    reading MusicXML files in these cases is application-dependent. For
    instance, applications may find that the system layout data is more
    reliable than the sum of the measure widths, and adjust the measure
    widths accordingly.
    """

    class Meta:
        name = "system-layout"

    system_margins: Optional[SystemMargins] = field(
        default=None,
        metadata={
            "name": "system-margins",
            "type": "Element",
        },
    )
    system_distance: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "system-distance",
            "type": "Element",
        },
    )
    top_system_distance: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "top-system-distance",
            "type": "Element",
        },
    )


class TextElementData(BaseModel):
    """The text-element-data type represents a syllable or portion of a syllable
    for lyric text underlay.

    A hyphen in the string content should only be used for an actual
    hyphenated word. Language names for text elements come from ISO 639,
    with optional country subcodes from ISO 3166.
    """

    class Meta:
        name = "text-element-data"

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    underline: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 3,
        },
    )
    overline: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 3,
        },
    )
    line_through: Optional[int] = field(
        default=None,
        metadata={
            "name": "line-through",
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 3,
        },
    )
    rotation: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": Decimal("-180"),
            "max_inclusive": Decimal("180"),
        },
    )
    letter_spacing: Optional[Union[Decimal, NumberOrNormalValue]] = field(
        default=None,
        metadata={
            "name": "letter-spacing",
            "type": "Attribute",
        },
    )
    lang: Optional[Union[str, LangValue]] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "namespace": XML_NS,
        },
    )
    direction: Optional[TextDirection] = field(
        default=None,
        metadata={
            "name": "dir",
            "type": "Attribute",
        },
    )


class Tie(BaseModel):
    """The tie element indicates that a tie begins or ends with this note.

    The tie element indicates sound; the tied element indicates
    notation.
    """

    class Meta:
        name = "tie"

    type_value: Optional[StartStop] = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )


class Tied(BaseModel):
    """The tied type represents the notated tie.

    The tie element represents the tie sound.
    """

    class Meta:
        name = "tied"

    type_value: Optional[StartStop] = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )
    number: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 1,
            "max_inclusive": 6,
        },
    )
    line_type: Optional[LineType] = field(
        default=None,
        metadata={
            "name": "line-type",
            "type": "Attribute",
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    placement: Optional[AboveBelow] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    orientation: Optional[OverUnder] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    bezier_offset: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "bezier-offset",
            "type": "Attribute",
        },
    )
    bezier_offset2: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "bezier-offset2",
            "type": "Attribute",
        },
    )
    bezier_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "bezier-x",
            "type": "Attribute",
        },
    )
    bezier_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "bezier-y",
            "type": "Attribute",
        },
    )
    bezier_x2: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "bezier-x2",
            "type": "Attribute",
        },
    )
    bezier_y2: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "bezier-y2",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class Time(BaseModel):
    """Time signatures are represented by the beats element for the numerator and
    the beat-type element for the denominator.

    The symbol attribute is used indicate common and cut time symbols as
    well as a single number display. Multiple pairs of beat and beat-
    type elements are used for composite time signatures with multiple
    denominators, such as 2/4 + 3/8. A composite such as 3+2/8 requires
    only one beat/beat-type pair. The print-object attribute allows a
    time signature to be specified but not printed, as is the case for
    excerpts from the middle of a score. The value is "yes" if not
    present. The optional number attribute refers to staff numbers
    within the part. If absent, the time signature applies to all staves
    in the part.

    :ivar beats: The beats element indicates the number of beats, as
        found in the numerator of a time signature.
    :ivar beat_type: The beat-type element indicates the beat unit, as
        found in the denominator of a time signature.
    :ivar senza_misura: A senza-misura element explicitly indicates that
        no time signature is present.
    :ivar number:
    :ivar symbol:
    :ivar default_x:
    :ivar default_y:
    :ivar relative_x:
    :ivar relative_y:
    :ivar font_family:
    :ivar font_style:
    :ivar font_size:
    :ivar font_weight:
    :ivar color:
    :ivar print_object:
    """

    class Meta:
        name = "time"

    beats: list[str] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "sequence": 1,
        },
    )
    beat_type: list[str] = field(
        default_factory=list,
        metadata={
            "name": "beat-type",
            "type": "Element",
            "sequence": 1,
        },
    )
    senza_misura: Optional[Empty] = field(
        default=None,
        metadata={
            "name": "senza-misura",
            "type": "Element",
        },
    )
    number: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    symbol: Optional[TimeSymbol] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    print_object: Optional[YesNo] = field(
        default=None,
        metadata={
            "name": "print-object",
            "type": "Attribute",
        },
    )


class TimeModification(BaseModel):
    """
    The time-modification type represents tuplets and other durational changes.

    :ivar actual_notes: The actual-notes element describes how many
        notes are played in the time usually occupied by the number in
        the normal-notes element.
    :ivar normal_notes: The normal-notes element describes how many
        notes are usually played in the time occupied by the number in
        the actual-notes element.
    :ivar normal_type: If the type associated with the number in the
        normal-notes element is different than the current note type
        (e.g., a quarter note within an eighth note triplet), then the
        normal-notes type (e.g. eighth) is specified in the normal-type
        and normal-dot elements.
    :ivar normal_dot: The normal-dot element is used to specify dotted
        normal tuplet types.
    """

    class Meta:
        name = "time-modification"

    actual_notes: Optional[int] = field(
        default=None,
        metadata={
            "name": "actual-notes",
            "type": "Element",
            "required": True,
        },
    )
    normal_notes: Optional[int] = field(
        default=None,
        metadata={
            "name": "normal-notes",
            "type": "Element",
            "required": True,
        },
    )
    normal_type: Optional[NoteTypeValue] = field(
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


class Transpose(BaseModel):
    """
    The transpose type represents what must be added to a written pitch to get a
    correct sounding pitch.

    :ivar diatonic: The diatonic element specifies the number of pitch
        steps needed to go from written to sounding pitch. This allows
        for correct spelling of enharmonic transpositions.
    :ivar chromatic: The chromatic element represents the number of
        semitones needed to get from written to sounding pitch. This
        value does not include octave-change values; the values for both
        elements need to be added to the written pitch to get the
        correct sounding pitch.
    :ivar octave_change: The octave-change element indicates how many
        octaves to add to get from written pitch to sounding pitch.
    :ivar double: If the double element is present, it indicates that
        the music is doubled one octave down from what is currently
        written (as is the case for mixed cello / bass parts in
        orchestral literature).
    """

    class Meta:
        name = "transpose"

    diatonic: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    chromatic: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    octave_change: Optional[int] = field(
        default=None,
        metadata={
            "name": "octave-change",
            "type": "Element",
        },
    )
    double: Optional[Empty] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )


class Tremolo(BaseModel):
    """While using repeater beams was the original method for indicating tremolos,
    often playback and display are not well-enough integrated in an application to
    make that feasible.

    The tremolo ornament can be used to indicate either single-note or
    double-note tremolos. Single-note tremolos use the single type,
    while double-note tremolos use the start and stop types. The default
    is "single" for compatibility with Version 1.1. The text of the
    element indicates the number of tremolo marks and is an integer from
    0 to 6. Note that the number of attached beams is not included in
    this value, but is represented separately using the beam element.
    """

    class Meta:
        name = "tremolo"

    value: Optional[int] = field(
        default=None,
        metadata={
            "required": True,
            "min_inclusive": 0,
            "max_inclusive": 6,
        },
    )
    type_value: StartStopSingle = field(
        default=StartStopSingle.SINGLE,
        metadata={
            "name": "type",
            "type": "Attribute",
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    placement: Optional[AboveBelow] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class TupletDot(BaseModel):
    """
    The tuplet-dot type is used to specify dotted normal tuplet types.
    """

    class Meta:
        name = "tuplet-dot"

    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class TupletNumber(BaseModel):
    """
    The tuplet-number type indicates the number of notes for this portion of the
    tuplet.
    """

    class Meta:
        name = "tuplet-number"

    value: Optional[int] = field(
        default=None,
        metadata={
            "required": True,
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class TupletType(BaseModel):
    """
    The tuplet-type type indicates the graphical note type of the notes for this
    portion of the tuplet.
    """

    class Meta:
        name = "tuplet-type"

    value: Optional[NoteTypeValue] = field(
        default=None,
        metadata={
            "required": True,
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class WavyLine(BaseModel):
    """Wavy lines are one way to indicate trills.

    When used with a measure element, they should always have
    type="continue" set.
    """

    class Meta:
        name = "wavy-line"

    type_value: Optional[StartStopContinue] = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )
    number: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 1,
            "max_inclusive": 6,
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    placement: Optional[AboveBelow] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    start_note: Optional[StartNote] = field(
        default=None,
        metadata={
            "name": "start-note",
            "type": "Attribute",
        },
    )
    trill_step: Optional[TrillStep] = field(
        default=None,
        metadata={
            "name": "trill-step",
            "type": "Attribute",
        },
    )
    two_note_turn: Optional[TwoNoteTurn] = field(
        default=None,
        metadata={
            "name": "two-note-turn",
            "type": "Attribute",
        },
    )
    accelerate: Optional[YesNo] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    beats: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": Decimal("2"),
        },
    )
    second_beat: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "second-beat",
            "type": "Attribute",
            "min_inclusive": Decimal("0"),
            "max_inclusive": Decimal("100"),
        },
    )
    last_beat: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "last-beat",
            "type": "Attribute",
            "min_inclusive": Decimal("0"),
            "max_inclusive": Decimal("100"),
        },
    )


class Wedge(BaseModel):
    """The wedge type represents crescendo and diminuendo wedge symbols.

    The type attribute is crescendo for the start of a wedge that is
    closed at the left side, and diminuendo for the start of a wedge
    that is closed on the right side. Spread values are measured in
    tenths; those at the start of a crescendo wedge or end of a
    diminuendo wedge are ignored.
    """

    class Meta:
        name = "wedge"

    type_value: Optional[WedgeType] = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )
    number: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 1,
            "max_inclusive": 6,
        },
    )
    spread: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class Appearance(BaseModel):
    """The appearance type controls general graphical settings for the music's
    final form appearance on a printed page of display.

    Currently this includes support for line widths and definitions for
    note sizes, plus an extension element for other aspects of
    appearance.
    """

    class Meta:
        name = "appearance"

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
    other_appearance: list[OtherAppearance] = field(
        default_factory=list,
        metadata={
            "name": "other-appearance",
            "type": "Element",
        },
    )


class Backup(BaseModel):
    """The backup and forward elements are required to coordinate multiple voices
    in one part, including music on multiple staves.

    The backup type is generally used to move between voices and staves.
    Thus the backup element does not include voice or staff elements.
    Duration values should always be positive, and should not cross
    measure boundaries.

    :ivar duration: Duration is a positive number specified in division
        units. This is the intended duration vs. notated duration (for
        instance, swing eighths vs. even eighths, or differences in
        dotted notes in Baroque-era music). Differences in duration
        specific to an interpretation or performance should use the note
        element's attack and release attributes.
    :ivar footnote:
    :ivar level:
    """

    class Meta:
        name = "backup"

    duration: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
            "min_exclusive": Decimal("0"),
        },
    )
    footnote: Optional[FormattedText] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    level: Optional[Level] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )


class Barline(BaseModel):
    """If a barline is other than a normal single barline, it should be represented
    by a barline type that describes it.

    This includes information about repeats and multiple endings, as well as line style. Barline data is on the same level as the other musical data in a score - a child of a measure in a partwise score, or a part in a timewise score. This allows for barlines within measures, as in dotted barlines that subdivide measures in complex meters. The two fermata elements allow for fermatas on both sides of the barline (the lower one inverted).
    Barlines have a location attribute to make it easier to process barlines independently of the other musical data in a score. It is often easier to set up measures separately from entering notes. The location attribute must match where the barline element occurs within the rest of the musical data in the score. If location is left, it should be the first element in the measure, aside from the print, bookmark, and link elements. If location is right, it should be the last element, again with the possible exception of the print, bookmark, and link elements. If no location is specified, the right barline is the default. The segno, coda, and divisions attributes work the same way as in the sound element. They are used for playback when barline elements contain segno or coda child elements.
    """

    class Meta:
        name = "barline"

    bar_style: Optional[BarStyleColor] = field(
        default=None,
        metadata={
            "name": "bar-style",
            "type": "Element",
        },
    )
    footnote: Optional[FormattedText] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    level: Optional[Level] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    wavy_line: Optional[WavyLine] = field(
        default=None,
        metadata={
            "name": "wavy-line",
            "type": "Element",
        },
    )
    segno: Optional[EmptyPrintStyle] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    coda: Optional[EmptyPrintStyle] = field(
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
    ending: Optional[Ending] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    repeat: Optional[Repeat] = field(
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
    segno_attribute: Optional[str] = field(
        default=None,
        metadata={
            "name": "segno",
            "type": "Attribute",
        },
    )
    coda_attribute: Optional[str] = field(
        default=None,
        metadata={
            "name": "coda",
            "type": "Attribute",
        },
    )
    divisions: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Bass(BaseModel):
    """The bass type is used to indicate a bass note in popular music chord
    symbols, e.g. G/C.

    It is generally not used in functional harmony, as inversion is
    generally not used in pop chord symbols. As with root, it is divided
    into step and alter elements, similar to pitches.
    """

    class Meta:
        name = "bass"

    bass_step: Optional[BassStep] = field(
        default=None,
        metadata={
            "name": "bass-step",
            "type": "Element",
            "required": True,
        },
    )
    bass_alter: Optional[BassAlter] = field(
        default=None,
        metadata={
            "name": "bass-alter",
            "type": "Element",
        },
    )


class Bend(BaseModel):
    """The bend type is used in guitar and tablature.

    The bend-alter element indicates the number of steps in the bend,
    similar to the alter element. As with the alter element, numbers
    like 0.5 can be used to indicate microtones. Negative numbers
    indicate pre-bends or releases; the pre-bend and release elements
    are used to distinguish what is intended. A with-bar element
    indicates that the bend is to be done at the bridge with a whammy or
    vibrato bar. The content of the element indicates how this should be
    notated.

    :ivar bend_alter: The bend-alter element indicates the number of
        steps in the bend, similar to the alter element. As with the
        alter element, numbers like 0.5 can be used to indicate
        microtones. Negative numbers indicate pre-bends or releases; the
        pre-bend and release elements are used to distinguish what is
        intended.
    :ivar pre_bend: The pre-bend element indicates that this is a pre-
        bend rather than a normal bend or a release.
    :ivar release: The release element indicates that this is a release
        rather than a normal bend or pre-bend.
    :ivar with_bar: The with-bar element indicates that the bend is to
        be done at the bridge with a whammy or vibrato bar. The content
        of the element indicates how this should be notated.
    :ivar default_x:
    :ivar default_y:
    :ivar relative_x:
    :ivar relative_y:
    :ivar font_family:
    :ivar font_style:
    :ivar font_size:
    :ivar font_weight:
    :ivar color:
    :ivar accelerate:
    :ivar beats:
    :ivar first_beat:
    :ivar last_beat:
    """

    class Meta:
        name = "bend"

    bend_alter: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "bend-alter",
            "type": "Element",
            "required": True,
        },
    )
    pre_bend: Optional[Empty] = field(
        default=None,
        metadata={
            "name": "pre-bend",
            "type": "Element",
        },
    )
    release: Optional[Empty] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    with_bar: Optional[PlacementText] = field(
        default=None,
        metadata={
            "name": "with-bar",
            "type": "Element",
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    accelerate: Optional[YesNo] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    beats: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": Decimal("2"),
        },
    )
    first_beat: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "first-beat",
            "type": "Attribute",
            "min_inclusive": Decimal("0"),
            "max_inclusive": Decimal("100"),
        },
    )
    last_beat: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "last-beat",
            "type": "Attribute",
            "min_inclusive": Decimal("0"),
            "max_inclusive": Decimal("100"),
        },
    )


class Credit(BaseModel):
    """The credit type represents the appearance of the title, composer, arranger,
    lyricist, copyright, dedication, and other text and graphics that commonly
    appears on the first page of a score.

    The credit-words and credit-image elements are similar to the words
    and image elements for directions. However, since the credit is not
    part of a measure, the default-x and default-y attributes adjust the
    origin relative to the bottom left-hand corner of the first page.
    The enclosure for credit-words is none by default. By default, a
    series of credit-words elements within a single credit element
    follow one another in sequence visually. Non-positional formatting
    attributes are carried over from the previous element by default.
    The page attribute for the credit element, new in Version 2.0,
    specifies the page number where the credit should appear. This is an
    integer value that starts with 1 for the first page. Its value is 1
    by default. Since credits occur before the music, these page numbers
    do not refer to the page numbering specified by the print element's
    page-number attribute.
    """

    class Meta:
        name = "credit"

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
    credit_image: Optional[Image] = field(
        default=None,
        metadata={
            "name": "credit-image",
            "type": "Element",
        },
    )
    credit_words: list[FormattedText] = field(
        default_factory=list,
        metadata={
            "name": "credit-words",
            "type": "Element",
        },
    )
    page: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Degree(BaseModel):
    """The degree type is used to add, alter, or subtract individual notes in the
    chord.

    The print-object attribute can be used to keep the degree from
    printing separately when it has already taken into account in the
    text attribute of the kind element. The degree-value and degree-type
    text attributes specify how the value and type of the degree should
    be displayed. A harmony of kind "other" can be spelled explicitly by
    using a series of degree elements together with a root.
    """

    class Meta:
        name = "degree"

    degree_value: Optional[DegreeValue] = field(
        default=None,
        metadata={
            "name": "degree-value",
            "type": "Element",
            "required": True,
        },
    )
    degree_alter: Optional[DegreeAlter] = field(
        default=None,
        metadata={
            "name": "degree-alter",
            "type": "Element",
            "required": True,
        },
    )
    degree_type: Optional[DegreeType] = field(
        default=None,
        metadata={
            "name": "degree-type",
            "type": "Element",
            "required": True,
        },
    )
    print_object: Optional[YesNo] = field(
        default=None,
        metadata={
            "name": "print-object",
            "type": "Attribute",
        },
    )


class Encoding(BaseModel):
    """The encoding element contains information about who did the digital
    encoding, when, with what software, and in what aspects.

    Standard type values for the encoder element are music, words, and
    arrangement, but other types may be used. The type attribute is only
    needed when there are multiple encoder elements.
    """

    class Meta:
        name = "encoding"

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
    """
    The figure type represents a single figure within a figured-bass element.

    :ivar prefix: Values for the prefix element include the accidental
        values sharp, flat, natural, double-sharp, flat-flat, and sharp-
        sharp. The prefix element may contain additional values for
        symbols specific to particular figured bass styles.
    :ivar figure_number: A figure-number is a number. Overstrikes of the
        figure number are represented in the suffix element.
    :ivar suffix: Values for the suffix element include the accidental
        values sharp, flat, natural, double-sharp, flat-flat, and sharp-
        sharp. Suffixes include both symbols that come after the figure
        number and those that overstrike the figure number. The suffix
        value slash is used for slashed numbers indicating chromatic
        alteration. The orientation and display of the slash usually
        depends on the figure number. The suffix element may contain
        additional values for symbols specific to particular figured
        bass styles.
    :ivar extend:
    """

    class Meta:
        name = "figure"

    prefix: Optional[StyleText] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    figure_number: Optional[StyleText] = field(
        default=None,
        metadata={
            "name": "figure-number",
            "type": "Element",
        },
    )
    suffix: Optional[StyleText] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    extend: Optional[Extend] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )


class Forward(BaseModel):
    """The backup and forward elements are required to coordinate multiple voices
    in one part, including music on multiple staves.

    The forward element is generally used within voices and staves.
    Duration values should always be positive, and should not cross
    measure boundaries.

    :ivar duration: Duration is a positive number specified in division
        units. This is the intended duration vs. notated duration (for
        instance, swing eighths vs. even eighths, or differences in
        dotted notes in Baroque-era music). Differences in duration
        specific to an interpretation or performance should use the note
        element's attack and release attributes.
    :ivar footnote:
    :ivar level:
    :ivar voice:
    :ivar staff: Staff assignment is only needed for music notated on
        multiple staves. Used by both notes and directions. Staff values
        are numbers, with 1 referring to the top-most staff in a part.
    """

    class Meta:
        name = "forward"

    duration: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
            "min_exclusive": Decimal("0"),
        },
    )
    footnote: Optional[FormattedText] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    level: Optional[Level] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    voice: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    staff: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )


class FrameNote(BaseModel):
    """The frame-note type represents each note included in the frame.

    An open string will have a fret value of 0, while a muted string
    will not be associated with a frame-note element.
    """

    class Meta:
        name = "frame-note"

    string: Optional[String] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    fret: Optional[Fret] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    fingering: Optional[Fingering] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    barre: Optional[Barre] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )


class HarpPedals(BaseModel):
    """The harp-pedals type is used to create harp pedal diagrams.

    The pedal-step and pedal-alter elements use the same values as the
    step and alter elements. For easiest reading, the pedal-tuning
    elements should follow standard harp pedal order, with pedal-step
    values of D, C, B, E, F, G, and A.
    """

    class Meta:
        name = "harp-pedals"

    pedal_tuning: list[PedalTuning] = field(
        default_factory=list,
        metadata={
            "name": "pedal-tuning",
            "type": "Element",
            "min_occurs": 1,
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class HeelToe(EmptyPlacement):
    """The heel and toe elements are used with organ pedals.

    The substitution value is "no" if the attribute is not present.
    """

    class Meta:
        name = "heel-toe"

    substitution: Optional[YesNo] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Key(BaseModel):
    """The key type represents a key signature.

    Both traditional and non-traditional key signatures are supported.
    The optional number attribute refers to staff numbers. If absent,
    the key signature applies to all staves in the part.

    :ivar cancel:
    :ivar fifths:
    :ivar mode:
    :ivar key_step: Non-traditional key signatures can be represented
        using the Humdrum/Scot concept of a list of altered tones. The
        key-step element indicates the pitch step to be altered,
        represented using the same names as in the step element.
    :ivar key_alter: Non-traditional key signatures can be represented
        using the Humdrum/Scot concept of a list of altered tones. The
        key-alter element represents the alteration for a given pitch
        step, represented with semitones in the same manner as the alter
        element.
    :ivar key_octave: The optional list of key-octave elements is used
        to specify in which octave each element of the key signature
        appears.
    :ivar number:
    :ivar default_x:
    :ivar default_y:
    :ivar relative_x:
    :ivar relative_y:
    :ivar font_family:
    :ivar font_style:
    :ivar font_size:
    :ivar font_weight:
    :ivar color:
    :ivar print_object:
    """

    class Meta:
        name = "key"

    cancel: Optional[Cancel] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    fifths: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    mode: Optional[str] = field(
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
    key_octave: list[KeyOctave] = field(
        default_factory=list,
        metadata={
            "name": "key-octave",
            "type": "Element",
        },
    )
    number: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    print_object: Optional[YesNo] = field(
        default=None,
        metadata={
            "name": "print-object",
            "type": "Attribute",
        },
    )


class Lyric(BaseModel):
    """The lyric type represents text underlays for lyrics, based on Humdrum with
    support for other formats.

    Two text elements that are not separated by an elision element are
    part of the same syllable, but may have different text formatting.
    The MusicXML 2.0 XSD is more strict than the 2.0 DTD in enforcing
    this by disallowing a second syllabic element unless preceded by an
    elision element. The lyric number indicates multiple lines, though a
    name can be used as well (as in Finale's verse / chorus / section
    specification). Justification is center by default; placement is
    below by default.

    :ivar syllabic:
    :ivar text:
    :ivar elision:
    :ivar extend:
    :ivar laughing: The laughing element is taken from Humdrum.
    :ivar humming: The humming element is taken from Humdrum.
    :ivar end_line: The end-line element comes from RP-017 for Standard
        MIDI File Lyric meta-events. It facilitates lyric display for
        Karaoke and similar applications.
    :ivar end_paragraph: The end-paragraph element comes from RP-017 for
        Standard MIDI File Lyric meta-events. It facilitates lyric
        display for Karaoke and similar applications.
    :ivar footnote:
    :ivar level:
    :ivar number:
    :ivar name:
    :ivar justify:
    :ivar default_x:
    :ivar default_y:
    :ivar relative_x:
    :ivar relative_y:
    :ivar placement:
    :ivar color:
    """

    class Meta:
        name = "lyric"

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
    laughing: Optional[Empty] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    humming: Optional[Empty] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    end_line: Optional[Empty] = field(
        default=None,
        metadata={
            "name": "end-line",
            "type": "Element",
        },
    )
    end_paragraph: Optional[Empty] = field(
        default=None,
        metadata={
            "name": "end-paragraph",
            "type": "Element",
        },
    )
    footnote: Optional[FormattedText] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    level: Optional[Level] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    number: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    justify: Optional[LeftCenterRight] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    placement: Optional[AboveBelow] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class MeasureStyle(BaseModel):
    """A measure-style indicates a special way to print partial to multiple
    measures within a part.

    This includes multiple rests over several measures, repeats of
    beats, single, or multiple measures, and use of slash notation. The
    multiple-rest and measure-repeat symbols indicate the number of
    measures covered in the element content. The beat-repeat and slash
    elements can cover partial measures. All but the multiple-rest
    element use a type attribute to indicate starting and stopping the
    use of the style. The optional number attribute specifies the staff
    number from top to bottom on the system, as with clef.
    """

    class Meta:
        name = "measure-style"

    multiple_rest: Optional[MultipleRest] = field(
        default=None,
        metadata={
            "name": "multiple-rest",
            "type": "Element",
        },
    )
    measure_repeat: Optional[MeasureRepeat] = field(
        default=None,
        metadata={
            "name": "measure-repeat",
            "type": "Element",
        },
    )
    beat_repeat: Optional[BeatRepeat] = field(
        default=None,
        metadata={
            "name": "beat-repeat",
            "type": "Element",
        },
    )
    slash: Optional[Slash] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    number: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )


class MetronomeTuplet(TimeModification):
    """
    The metronome-tuplet type uses the same element structure as the time-
    modification element along with some attributes from the tuplet element.
    """

    class Meta:
        name = "metronome-tuplet"

    type_value: Optional[StartStop] = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )
    bracket: Optional[YesNo] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    show_number: Optional[ShowTuplet] = field(
        default=None,
        metadata={
            "name": "show-number",
            "type": "Attribute",
        },
    )


class Mordent(EmptyTrillSound):
    """The mordent type is used for both represents the mordent sign with the
    vertical line and the inverted-mordent sign without the line.

    The long attribute is "no" by default.
    """

    class Meta:
        name = "mordent"

    long: Optional[YesNo] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class NameDisplay(BaseModel):
    """The name-display type is used for exact formatting of multi-font text in
    part and group names to the left of the system.

    The print-object attribute can be used to determine what, if
    anything, is printed at the start of each system. Enclosure for the
    display-text element is none by default. Language for the display-
    text element is Italian ("it") by default.
    """

    class Meta:
        name = "name-display"

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
    print_object: Optional[YesNo] = field(
        default=None,
        metadata={
            "name": "print-object",
            "type": "Attribute",
        },
    )


class PageLayout(BaseModel):
    """Page layout can be defined both in score-wide defaults and in the print
    element.

    Page margins are specified either for both even and odd pages, or
    via separate odd and even page number values. The type is not needed
    when used as part of a print element. If omitted when used in the
    defaults element, "both" is the default.
    """

    class Meta:
        name = "page-layout"

    page_height: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "page-height",
            "type": "Element",
        },
    )
    page_width: Optional[Decimal] = field(
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


class Root(BaseModel):
    """The root type indicates a pitch like C, D, E vs.

    a function indication like I, II, III. It is used with chord symbols
    in popular music. The root element has a root-step and optional
    root-alter element similar to the step and alter elements, but
    renamed to distinguish the different musical meanings.
    """

    class Meta:
        name = "root"

    root_step: Optional[RootStep] = field(
        default=None,
        metadata={
            "name": "root-step",
            "type": "Element",
            "required": True,
        },
    )
    root_alter: Optional[RootAlter] = field(
        default=None,
        metadata={
            "name": "root-alter",
            "type": "Element",
        },
    )


class Scordatura(BaseModel):
    """Scordatura string tunings are represented by a series of accord elements,
    similar to the staff-tuning elements.

    Strings are numbered from high to low.
    """

    class Meta:
        name = "scordatura"

    accord: list[Accord] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )


class Sound(BaseModel):
    """The sound element contains general playback parameters.

    They can stand alone within a part/measure, or be a component
    element within a direction. Tempo is expressed in quarter notes per
    minute. If 0, the sound-generating program should prompt the user at
    the time of compiling a sound (MIDI) file. Dynamics (or MIDI
    velocity) are expressed as a percentage of the default forte value
    (90 for MIDI 1.0). Dacapo indicates to go back to the beginning of
    the movement. When used it always has the value "yes". Segno and
    dalsegno are used for backwards jumps to a segno sign; coda and
    tocoda are used for forward jumps to a coda sign. If there are
    multiple jumps, the value of these parameters can be used to name
    and distinguish them. If segno or coda is used, the divisions
    attribute can also be used to indicate the number of divisions per
    quarter note. Otherwise sound and MIDI generating programs may have
    to recompute this. By default, a dalsegno or dacapo attribute
    indicates that the jump should occur the first time through, while a
    tocoda attribute indicates the jump should occur the second time
    through. The time that jumps occur can be changed by using the time-
    only attribute. Forward-repeat is used when a forward repeat sign is
    implied, and usually follows a bar line. When used it always has the
    value of "yes". The fine attribute follows the final note or rest in
    a movement with a da capo or dal segno direction. If numeric, the
    value represents the actual duration of the final note or rest,
    which can be ambiguous in written notation and different among parts
    and voices. The value may also be "yes" to indicate no change to the
    final duration. If the sound element applies only one time through a
    repeat, the time-only attribute indicates which time to apply the
    sound element. Pizzicato in a sound element effects all following
    notes. Yes indicates pizzicato, no indicates arco. The pan and
    elevation attributes are deprecated in Version 2.0. The pan and
    elevation elements in the midi-instrument element should be used
    instead. The meaning of the pan and elevation attributes is the same
    as for the pan and elevation elements. If both are present, the mid-
    instrument elements take priority. The damper-pedal, soft-pedal, and
    sostenuto-pedal attributes effect playback of the three common piano
    pedals and their MIDI controller equivalents. The yes value
    indicates the pedal is depressed; no indicates the pedal is
    released. A numeric value from 0 to 100 may also be used for half
    pedaling. This value is the percentage that the pedal is depressed.
    A value of 0 is equivalent to no, and a value of 100 is equivalent
    to yes. MIDI instruments are changed using the midi-instrument
    element. The offset element is used to indicate that the sound takes
    place offset from the current score position. If the sound element
    is a child of a direction element, the sound offset element
    overrides the direction offset element if both elements are present.
    Note that the offset reflects the intended musical position for the
    change in sound. It should not be used to compensate for latency
    issues in particular hardware configurations.
    """

    class Meta:
        name = "sound"

    midi_instrument: list[MidiInstrument] = field(
        default_factory=list,
        metadata={
            "name": "midi-instrument",
            "type": "Element",
        },
    )
    offset: Optional[Offset] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    tempo: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": Decimal("0"),
        },
    )
    dynamics: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": Decimal("0"),
        },
    )
    dacapo: Optional[YesNo] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    segno: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    dalsegno: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    coda: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    tocoda: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    divisions: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    forward_repeat: Optional[YesNo] = field(
        default=None,
        metadata={
            "name": "forward-repeat",
            "type": "Attribute",
        },
    )
    fine: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    time_only: Optional[str] = field(
        default=None,
        metadata={
            "name": "time-only",
            "type": "Attribute",
        },
    )
    pizzicato: Optional[YesNo] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    pan: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": Decimal("-180"),
            "max_inclusive": Decimal("180"),
        },
    )
    elevation: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": Decimal("-180"),
            "max_inclusive": Decimal("180"),
        },
    )
    damper_pedal: Optional[Union[YesNo, Decimal]] = field(
        default=None,
        metadata={
            "name": "damper-pedal",
            "type": "Attribute",
        },
    )
    soft_pedal: Optional[Union[YesNo, Decimal]] = field(
        default=None,
        metadata={
            "name": "soft-pedal",
            "type": "Attribute",
        },
    )
    sostenuto_pedal: Optional[Union[YesNo, Decimal]] = field(
        default=None,
        metadata={
            "name": "sostenuto-pedal",
            "type": "Attribute",
        },
    )


class StaffDetails(BaseModel):
    """The staff-details element is used to indicate different types of staves.

    The optional number attribute specifies the staff number from top to
    bottom on the system, as with clef. The print-object attribute is
    used to indicate when a staff is not printed in a part, usually in
    large scores where empty parts are omitted. It is yes by default. If
    print-spacing is yes while print-object is no, the score is printed
    in cutaway format where vertical space is left for the empty part.

    :ivar staff_type:
    :ivar staff_lines: The staff-lines element specifies the number of
        lines for non 5-line staffs.
    :ivar staff_tuning:
    :ivar capo: The capo element indicates at which fret a capo should
        be placed on a fretted instrument. This changes the open tuning
        of the strings specified by staff-tuning by the specified number
        of half-steps.
    :ivar staff_size: The staff-size element indicates how large a staff
        space is on this staff, expressed as a percentage of the work's
        default scaling. Values less than 100 make the staff space
        smaller while values over 100 make the staff space larger. A
        staff-type of cue, ossia, or editorial implies a staff-size of
        less than 100, but the exact value is implementation-dependent
        unless specified here. Staff size affects staff height only, not
        the relationship of the staff to the left and right margins.
    :ivar number:
    :ivar show_frets:
    :ivar print_object:
    :ivar print_spacing:
    """

    class Meta:
        name = "staff-details"

    staff_type: Optional[StaffType] = field(
        default=None,
        metadata={
            "name": "staff-type",
            "type": "Element",
        },
    )
    staff_lines: Optional[int] = field(
        default=None,
        metadata={
            "name": "staff-lines",
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
    capo: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    staff_size: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "staff-size",
            "type": "Element",
            "min_inclusive": Decimal("0"),
        },
    )
    number: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    show_frets: Optional[ShowFrets] = field(
        default=None,
        metadata={
            "name": "show-frets",
            "type": "Attribute",
        },
    )
    print_object: Optional[YesNo] = field(
        default=None,
        metadata={
            "name": "print-object",
            "type": "Attribute",
        },
    )
    print_spacing: Optional[YesNo] = field(
        default=None,
        metadata={
            "name": "print-spacing",
            "type": "Attribute",
        },
    )


class StrongAccent(EmptyPlacement):
    """The strong-accent type indicates a vertical accent mark.

    The type attribute indicates if the point of the accent is down or
    up.
    """

    class Meta:
        name = "strong-accent"

    type_value: UpDown = field(
        default=UpDown.UP,
        metadata={
            "name": "type",
            "type": "Attribute",
        },
    )


class TupletPortion(BaseModel):
    """The tuplet-portion type provides optional full control over tuplet
    specifications.

    It allows the number and note type (including dots) to be set for
    the actual and normal portions of a single tuplet. If any of these
    elements are absent, their values are based on the time-modification
    element.
    """

    class Meta:
        name = "tuplet-portion"

    tuplet_number: Optional[TupletNumber] = field(
        default=None,
        metadata={
            "name": "tuplet-number",
            "type": "Element",
        },
    )
    tuplet_type: Optional[TupletType] = field(
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
    """Works are optionally identified by number and title.

    The work type also may indicate a link to the opus document that
    composes multiple scores into a collection.

    :ivar work_number: The work-number element specifies the number of a
        work, such as its opus number.
    :ivar work_title: The work-title element specifies the title of a
        work, not including its opus or other work number.
    :ivar opus:
    """

    class Meta:
        name = "work"

    work_number: Optional[str] = field(
        default=None,
        metadata={
            "name": "work-number",
            "type": "Element",
        },
    )
    work_title: Optional[str] = field(
        default=None,
        metadata={
            "name": "work-title",
            "type": "Element",
        },
    )
    opus: Optional[Opus] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )


class Articulations(BaseModel):
    """
    Articulations and accents are grouped together here.

    :ivar accent: The accent element indicates a regular horizontal
        accent mark.
    :ivar strong_accent: The strong-accent element indicates a vertical
        accent mark.
    :ivar staccato: The staccato element is used for a dot articulation,
        as opposed to a stroke or a wedge.
    :ivar tenuto: The tenuto element indicates a tenuto line symbol.
    :ivar detached_legato: The detached-legato element indicates the
        combination of a tenuto line and staccato dot symbol.
    :ivar staccatissimo: The staccatissimo element is used for a wedge
        articulation, as opposed to a dot or a stroke.
    :ivar spiccato: The spiccato element is used for a stroke
        articulation, as opposed to a dot or a wedge.
    :ivar scoop: The scoop element is an indeterminate slide attached to
        a single note. The scoop element appears before the main note
        and comes from below the main pitch.
    :ivar plop: The plop element is an indeterminate slide attached to a
        single note. The plop element appears before the main note and
        comes from above the main pitch.
    :ivar doit: The doit element is an indeterminate slide attached to a
        single note. The doit element appears after the main note and
        goes above the main pitch.
    :ivar falloff: The falloff element is an indeterminate slide
        attached to a single note. The falloff element appears before
        the main note and goes below the main pitch.
    :ivar breath_mark: The breath-mark element indicates a place to take
        a breath. It is typically notated with a comma / apostrophe
        symbol.
    :ivar caesura: The caesura element indicates a slight pause. It is
        notated using a "railroad tracks" symbol.
    :ivar stress: The stress element indicates a stressed note.
    :ivar unstress: The unstress element indicates an unstressed note.
        It is often notated using a u-shaped symbol.
    :ivar other_articulation: The other-articulation element is used to
        define any articulations not yet in the MusicXML format. This
        allows extended representation, though without application
        interoperability.
    """

    class Meta:
        name = "articulations"

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
    breath_mark: list[EmptyPlacement] = field(
        default_factory=list,
        metadata={
            "name": "breath-mark",
            "type": "Element",
        },
    )
    caesura: list[EmptyPlacement] = field(
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
    other_articulation: list[PlacementText] = field(
        default_factory=list,
        metadata={
            "name": "other-articulation",
            "type": "Element",
        },
    )


class Attributes(BaseModel):
    """The attributes element contains musical information that typically changes
    on measure boundaries.

    This includes key and time signatures, clefs, transpositions, and
    staving.

    :ivar footnote:
    :ivar level:
    :ivar divisions: Musical notation duration is commonly represented
        as fractions. The divisions element indicates how many divisions
        per quarter note are used to indicate a note's duration. For
        example, if duration = 1 and divisions = 2, this is an eighth
        note duration. Duration and divisions are used directly for
        generating sound output, so they must be chosen to take tuplets
        into account. Using a divisions element lets us use just one
        number to represent a duration for each note in the score, while
        retaining the full power of a fractional representation. If
        maximum compatibility with Standard MIDI 1.0 files is important,
        do not have the divisions value exceed 16383.
    :ivar key: The key element represents a key signature. Both
        traditional and non-traditional key signatures are supported.
        The optional number attribute refers to staff numbers. If
        absent, the key signature applies to all staves in the part.
    :ivar time: Time signatures are represented by the beats element for
        the numerator and the beat-type element for the denominator.
    :ivar staves: The staves element is used if there is more than one
        staff represented in the given part (e.g., 2 staves for typical
        piano parts). If absent, a value of 1 is assumed. Staves are
        ordered from top to bottom in a part in numerical order, with
        staff 1 above staff 2.
    :ivar part_symbol: The part-symbol element indicates how a symbol
        for a multi-staff part is indicated in the score.
    :ivar instruments: The instruments element is only used if more than
        one instrument is represented in the part (e.g., oboe I and II
        where they play together most of the time). If absent, a value
        of 1 is assumed.
    :ivar clef: Clefs are represented by a combination of sign, line,
        and clef-octave-change elements.
    :ivar staff_details: The staff-details element is used to indicate
        different types of staves.
    :ivar transpose: If the part is being encoded for a transposing
        instrument in written vs. concert pitch, the transposition must
        be encoded in the transpose element using the transpose type.
    :ivar directive: Directives are like directions, but can be grouped
        together with attributes for convenience. This is typically used
        for tempo markings at the beginning of a piece of music. This
        element has been deprecated in Version 2.0 in favor of the
        directive attribute for direction elements. Language names come
        from ISO 639, with optional country subcodes from ISO 3166.
    :ivar measure_style: A measure-style indicates a special way to
        print partial to multiple measures within a part. This includes
        multiple rests over several measures, repeats of beats, single,
        or multiple measures, and use of slash notation.
    """

    class Meta:
        name = "attributes"

    footnote: Optional[FormattedText] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    level: Optional[Level] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    divisions: Optional[Decimal] = field(
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
    staves: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    part_symbol: Optional[PartSymbol] = field(
        default=None,
        metadata={
            "name": "part-symbol",
            "type": "Element",
        },
    )
    instruments: Optional[int] = field(
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
    transpose: Optional[Transpose] = field(
        default=None,
        metadata={
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
        value: str = field(
            default="",
            metadata={
                "required": True,
            },
        )
        default_x: Optional[Decimal] = field(
            default=None,
            metadata={
                "name": "default-x",
                "type": "Attribute",
            },
        )
        default_y: Optional[Decimal] = field(
            default=None,
            metadata={
                "name": "default-y",
                "type": "Attribute",
            },
        )
        relative_x: Optional[Decimal] = field(
            default=None,
            metadata={
                "name": "relative-x",
                "type": "Attribute",
            },
        )
        relative_y: Optional[Decimal] = field(
            default=None,
            metadata={
                "name": "relative-y",
                "type": "Attribute",
            },
        )
        font_family: Optional[str] = field(
            default=None,
            metadata={
                "name": "font-family",
                "type": "Attribute",
                "pattern": r"[^,]+(, ?[^,]+)*",
            },
        )
        font_style: Optional[FontStyle] = field(
            default=None,
            metadata={
                "name": "font-style",
                "type": "Attribute",
            },
        )
        font_size: Optional[Union[Decimal, CssFontSize]] = field(
            default=None,
            metadata={
                "name": "font-size",
                "type": "Attribute",
            },
        )
        font_weight: Optional[FontWeight] = field(
            default=None,
            metadata={
                "name": "font-weight",
                "type": "Attribute",
            },
        )
        color: Optional[str] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
            },
        )
        lang: Optional[Union[str, LangValue]] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "namespace": XML_NS,
            },
        )


class Defaults(BaseModel):
    """
    The defaults type specifies score-wide defaults for scaling, layout, and
    appearance.
    """

    class Meta:
        name = "defaults"

    scaling: Optional[Scaling] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    page_layout: Optional[PageLayout] = field(
        default=None,
        metadata={
            "name": "page-layout",
            "type": "Element",
        },
    )
    system_layout: Optional[SystemLayout] = field(
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
    appearance: Optional[Appearance] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    music_font: Optional[EmptyFont] = field(
        default=None,
        metadata={
            "name": "music-font",
            "type": "Element",
        },
    )
    word_font: Optional[EmptyFont] = field(
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


class FiguredBass(BaseModel):
    """The figured-bass element represents figured bass notation.

    Figured bass elements take their position from the first regular
    note that follows. Figures are ordered from top to bottom. The value
    of parentheses is "no" if not present.

    :ivar figure:
    :ivar duration: Duration is a positive number specified in division
        units. This is the intended duration vs. notated duration (for
        instance, swing eighths vs. even eighths, or differences in
        dotted notes in Baroque-era music). Differences in duration
        specific to an interpretation or performance should use the note
        element's attack and release attributes.
    :ivar footnote:
    :ivar level:
    :ivar default_x:
    :ivar default_y:
    :ivar relative_x:
    :ivar relative_y:
    :ivar font_family:
    :ivar font_style:
    :ivar font_size:
    :ivar font_weight:
    :ivar color:
    :ivar print_object:
    :ivar print_dot:
    :ivar print_spacing:
    :ivar print_lyric:
    :ivar parentheses:
    """

    class Meta:
        name = "figured-bass"

    figure: list[Figure] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )
    duration: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Element",
            "min_exclusive": Decimal("0"),
        },
    )
    footnote: Optional[FormattedText] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    level: Optional[Level] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    print_object: Optional[YesNo] = field(
        default=None,
        metadata={
            "name": "print-object",
            "type": "Attribute",
        },
    )
    print_dot: Optional[YesNo] = field(
        default=None,
        metadata={
            "name": "print-dot",
            "type": "Attribute",
        },
    )
    print_spacing: Optional[YesNo] = field(
        default=None,
        metadata={
            "name": "print-spacing",
            "type": "Attribute",
        },
    )
    print_lyric: Optional[YesNo] = field(
        default=None,
        metadata={
            "name": "print-lyric",
            "type": "Attribute",
        },
    )
    parentheses: Optional[YesNo] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Frame(BaseModel):
    """The frame type represents a frame or fretboard diagram used together with a
    chord symbol.

    The representation is based on the NIFF guitar grid with additional
    information.

    :ivar frame_strings: The frame-strings element gives the overall
        size of the frame in vertical lines (strings).
    :ivar frame_frets: The frame-frets element gives the overall size of
        the frame in horizontal spaces (frets).
    :ivar first_fret:
    :ivar frame_note:
    :ivar default_x:
    :ivar default_y:
    :ivar relative_x:
    :ivar relative_y:
    :ivar color:
    :ivar halign:
    :ivar valign:
    :ivar height:
    :ivar width:
    """

    class Meta:
        name = "frame"

    frame_strings: Optional[int] = field(
        default=None,
        metadata={
            "name": "frame-strings",
            "type": "Element",
            "required": True,
        },
    )
    frame_frets: Optional[int] = field(
        default=None,
        metadata={
            "name": "frame-frets",
            "type": "Element",
            "required": True,
        },
    )
    first_fret: Optional[FirstFret] = field(
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
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    halign: Optional[LeftCenterRight] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    valign: Optional[Valign] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    height: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    width: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Identification(BaseModel):
    """Identification contains basic metadata about the score.

    It includes the information in MuseData headers that may apply at a
    score-wide, movement-wide, or part-wide level. The creator, rights,
    source, and relation elements are based on Dublin Core.

    :ivar creator: The creator element is borrowed from Dublin Core. It
        is used for the creators of the score. The type attribute is
        used to distinguish different creative contributions. Thus,
        there can be multiple creators within an identification.
        Standard type values are composer, lyricist, and arranger. Other
        type values may be used for different types of creative roles.
        The type attribute should usually be used even if there is just
        a single creator element. The MusicXML format does not use the
        creator / contributor distinction from Dublin Core.
    :ivar rights: The rights element is borrowed from Dublin Core. It
        contains copyright and other intellectual property notices.
        Words, music, and derivatives can have different types, so
        multiple rights tags with different type attributes are
        supported. Standard type values are music, words, and
        arrangement, but other types may be used. The type attribute is
        only needed when there are multiple rights elements.
    :ivar encoding:
    :ivar source: The source for the music that is encoded. This is
        similar to the Dublin Core source element.
    :ivar relation: A related resource for the music that is encoded.
        This is similar to the Dublin Core relation element. Standard
        type values are music, words, and arrangement, but other types
        may be used.
    :ivar miscellaneous:
    """

    class Meta:
        name = "identification"

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
    encoding: Optional[Encoding] = field(
        default_factory=Encoding,
        metadata={
            "type": "Element",
        },
    )
    source: Optional[str] = field(
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
    miscellaneous: Optional[Miscellaneous] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )


class MetronomeNote(BaseModel):
    """
    The metronome-note type defines the appearance of a note within a metric
    relationship mark.

    :ivar metronome_type: The metronome-type element works like the type
        element in defining metric relationships.
    :ivar metronome_dot: The metronome-dot element works like the dot
        element in defining metric relationships.
    :ivar metronome_beam:
    :ivar metronome_tuplet:
    """

    class Meta:
        name = "metronome-note"

    metronome_type: Optional[NoteTypeValue] = field(
        default=None,
        metadata={
            "name": "metronome-type",
            "type": "Element",
            "required": True,
        },
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
    metronome_tuplet: Optional[MetronomeTuplet] = field(
        default=None,
        metadata={
            "name": "metronome-tuplet",
            "type": "Element",
        },
    )


class Ornaments(BaseModel):
    """Ornaments can be any of several types, followed optionally by accidentals.

    The accidental-mark element's content is represented the same as an
    accidental element, but with a different name to reflect the
    different musical meaning.

    :ivar trill_mark: The trill-mark element represents the trill-mark
        symbol.
    :ivar turn: The turn element is the normal turn shape which goes up
        then down.
    :ivar delayed_turn: The delayed-turn element indicates a normal turn
        that is delayed until the end of the current note.
    :ivar inverted_turn: The inverted-turn element has the shape which
        goes down and then up.
    :ivar shake: The shake element has a similar appearance to an
        inverted-mordent element.
    :ivar wavy_line:
    :ivar mordent: The mordent element represents the sign with the
        vertical line. The long attribute is "no" by default.
    :ivar inverted_mordent: The inverted-mordent element represents the
        sign without the vertical line. The long attribute is "no" by
        default.
    :ivar schleifer: The name for this ornament is based on the German,
        to avoid confusion with the more common slide element defined
        earlier.
    :ivar tremolo: While using repeater beams was the original method
        for indicating tremolos, often playback and display are not
        well-enough integrated in an application to make that feasible.
        The tremolo ornament can be used to indicate either single-note
        or double-note tremolos.
    :ivar other_ornament: The other-ornament element is used to define
        any ornaments not yet in the MusicXML format. This allows
        extended representation, though without application
        interoperability.
    :ivar accidental_mark:
    """

    class Meta:
        name = "ornaments"

    trill_mark: list[EmptyTrillSound] = field(
        default_factory=list,
        metadata={
            "name": "trill-mark",
            "type": "Element",
            "sequence": 1,
        },
    )
    turn: list[EmptyTrillSound] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "sequence": 1,
        },
    )
    delayed_turn: list[EmptyTrillSound] = field(
        default_factory=list,
        metadata={
            "name": "delayed-turn",
            "type": "Element",
            "sequence": 1,
        },
    )
    inverted_turn: list[EmptyTrillSound] = field(
        default_factory=list,
        metadata={
            "name": "inverted-turn",
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
    other_ornament: list[PlacementText] = field(
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


class PartGroup(BaseModel):
    """The part-group element indicates groupings of parts in the score, usually
    indicated by braces and brackets.

    Braces that are used for multi-staff parts should be defined in the
    attributes element for that part. The part-group start element
    appears before the first score-part in the group. The part-group
    stop element appears after the last score-part in the group. The
    number attribute is used to distinguish overlapping and nested part-
    groups, not the sequence of groups. As with parts, groups can have a
    name and abbreviation. Values for the child elements are ignored at
    the stop of a group. A part-group element is not needed for a single
    multi-staff part. By default, multi-staff parts include a brace
    symbol and (if appropriate given the bar-style) common barlines. The
    symbol formatting for a multi-staff part can be more fully specified
    using the part-symbol element.

    :ivar group_name:
    :ivar group_name_display: Formatting specified in the group-name-
        display element overrides formatting specified in the group-name
        element.
    :ivar group_abbreviation:
    :ivar group_abbreviation_display: Formatting specified in the group-
        abbreviation-display element overrides formatting specified in
        the group-abbreviation element.
    :ivar group_symbol:
    :ivar group_barline:
    :ivar group_time: The group-time element indicates that the
        displayed time signatures should stretch across all parts and
        staves in the group.
    :ivar footnote:
    :ivar level:
    :ivar type_value:
    :ivar number:
    """

    class Meta:
        name = "part-group"

    group_name: Optional[GroupName] = field(
        default=None,
        metadata={
            "name": "group-name",
            "type": "Element",
        },
    )
    group_name_display: Optional[NameDisplay] = field(
        default=None,
        metadata={
            "name": "group-name-display",
            "type": "Element",
        },
    )
    group_abbreviation: Optional[GroupName] = field(
        default=None,
        metadata={
            "name": "group-abbreviation",
            "type": "Element",
        },
    )
    group_abbreviation_display: Optional[NameDisplay] = field(
        default=None,
        metadata={
            "name": "group-abbreviation-display",
            "type": "Element",
        },
    )
    group_symbol: Optional[GroupSymbol] = field(
        default=None,
        metadata={
            "name": "group-symbol",
            "type": "Element",
        },
    )
    group_barline: Optional[GroupBarline] = field(
        default=None,
        metadata={
            "name": "group-barline",
            "type": "Element",
        },
    )
    group_time: Optional[Empty] = field(
        default=None,
        metadata={
            "name": "group-time",
            "type": "Element",
        },
    )
    footnote: Optional[FormattedText] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    level: Optional[Level] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    type_value: Optional[StartStop] = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )
    number: str = field(
        default="1",
        metadata={
            "type": "Attribute",
        },
    )


class Print(BaseModel):
    """The print type contains general printing parameters, including the layout
    elements defined in the layout.mod file.

    The part-name-display and part-abbreviation-display elements used in
    the score.mod file may also be used here to change how a part name
    or abbreviation is displayed over the course of a piece. They take
    effect when the current measure or a succeeding measure starts a new
    system. Layout elements in a print statement only apply to the
    current page, system, staff, or measure. Music that follows
    continues to take the default values from the layout included in the
    defaults element.
    """

    class Meta:
        name = "print"

    page_layout: Optional[PageLayout] = field(
        default=None,
        metadata={
            "name": "page-layout",
            "type": "Element",
        },
    )
    system_layout: Optional[SystemLayout] = field(
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
    measure_layout: Optional[MeasureLayout] = field(
        default=None,
        metadata={
            "name": "measure-layout",
            "type": "Element",
        },
    )
    measure_numbering: Optional[MeasureNumbering] = field(
        default=None,
        metadata={
            "name": "measure-numbering",
            "type": "Element",
        },
    )
    part_name_display: Optional[NameDisplay] = field(
        default=None,
        metadata={
            "name": "part-name-display",
            "type": "Element",
        },
    )
    part_abbreviation_display: Optional[NameDisplay] = field(
        default=None,
        metadata={
            "name": "part-abbreviation-display",
            "type": "Element",
        },
    )
    staff_spacing: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "staff-spacing",
            "type": "Attribute",
        },
    )
    new_system: Optional[YesNo] = field(
        default=None,
        metadata={
            "name": "new-system",
            "type": "Attribute",
        },
    )
    new_page: Optional[YesNo] = field(
        default=None,
        metadata={
            "name": "new-page",
            "type": "Attribute",
        },
    )
    blank_page: Optional[int] = field(
        default=None,
        metadata={
            "name": "blank-page",
            "type": "Attribute",
        },
    )
    page_number: Optional[str] = field(
        default=None,
        metadata={
            "name": "page-number",
            "type": "Attribute",
        },
    )


class Technical(BaseModel):
    """
    Technical indications give performance information for individual instruments.

    :ivar up_bow: The up-bow element represent the symbol that is used
        both for up-bowing on bowed instruments, and up-stroke on
        plucked instruments.
    :ivar down_bow: The down-bow element represent the symbol that is
        used both for down-bowing on bowed instruments, and down-stroke
        on plucked instruments.
    :ivar harmonic:
    :ivar open_string: The open-string element represents the open
        string symbol.
    :ivar thumb_position: The thumb-position element represents the
        thumb position symbol.
    :ivar fingering:
    :ivar pluck: The pluck element is used to specify the plucking
        fingering on a fretted instrument, where the fingering element
        refers to the fretting fingering. Typical values are p, i, m, a
        for pulgar/thumb, indicio/index, medio/middle, and anular/ring
        fingers.
    :ivar double_tongue: The double-tongue element represents the double
        tongue symbol (two dots arranged horizontally).
    :ivar triple_tongue: The triple-tongue element represents the triple
        tongue symbol (three dots arranged horizontally).
    :ivar stopped: The stopped element represents the stopped symbol,
        which looks like a plus sign.
    :ivar snap_pizzicato: The snap-pizzicato element represents the snap
        pizzicato symbol (a circle with a line).
    :ivar fret:
    :ivar string:
    :ivar hammer_on:
    :ivar pull_off:
    :ivar bend:
    :ivar tap: The tap element indicates a tap on the fretboard. The
        element content allows specification of the notation; + and T
        are common choices. If empty, the display is application-
        specific.
    :ivar heel:
    :ivar toe:
    :ivar fingernails: The fingernails element is used in harp notation.
    :ivar other_technical: The other-technical element is used to define
        any technical indications not yet in the MusicXML format. This
        allows extended representation, though without application
        interoperability.
    """

    class Meta:
        name = "technical"

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
    stopped: list[EmptyPlacement] = field(
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
    tap: list[PlacementText] = field(
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
    other_technical: list[PlacementText] = field(
        default_factory=list,
        metadata={
            "name": "other-technical",
            "type": "Element",
        },
    )


class Tuplet(BaseModel):
    """A tuplet element is present when a tuplet is to be displayed graphically, in
    addition to the sound data provided by the time-modification elements.

    The number attribute is used to distinguish nested tuplets. The
    bracket attribute is used to indicate the presence of a bracket. If
    unspecified, the results are implementation-dependent. The line-
    shape attribute is used to specify whether the bracket is straight
    or in the older curved or slurred style. It is straight by default.
    Whereas a time-modification element shows how the cumulative,
    sounding effect of tuplets compare to the written note type, the
    tuplet element describes how each tuplet is displayed. The show-
    number attribute is used to display either the number of actual
    notes, the number of both actual and normal notes, or neither. It is
    actual by default. The show-type attribute is used to display either
    the actual type, both the actual and normal types, or neither. It is
    none by default.

    :ivar tuplet_actual: The tuplet-actual element provide optional full
        control over how the actual part of the tuplet is displayed,
        including number and note type (with dots). If any of these
        elements are absent, their values are based on the time-
        modification element.
    :ivar tuplet_normal: The tuplet-normal element provide optional full
        control over how the normal part of the tuplet is displayed,
        including number and note type (with dots). If any of these
        elements are absent, their values are based on the time-
        modification element.
    :ivar type_value:
    :ivar number:
    :ivar bracket:
    :ivar show_number:
    :ivar show_type:
    :ivar line_shape:
    :ivar default_x:
    :ivar default_y:
    :ivar relative_x:
    :ivar relative_y:
    :ivar placement:
    """

    class Meta:
        name = "tuplet"

    tuplet_actual: Optional[TupletPortion] = field(
        default=None,
        metadata={
            "name": "tuplet-actual",
            "type": "Element",
        },
    )
    tuplet_normal: Optional[TupletPortion] = field(
        default=None,
        metadata={
            "name": "tuplet-normal",
            "type": "Element",
        },
    )
    type_value: Optional[StartStop] = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
            "required": True,
        },
    )
    number: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 1,
            "max_inclusive": 6,
        },
    )
    bracket: Optional[YesNo] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    show_number: Optional[ShowTuplet] = field(
        default=None,
        metadata={
            "name": "show-number",
            "type": "Attribute",
        },
    )
    show_type: Optional[ShowTuplet] = field(
        default=None,
        metadata={
            "name": "show-type",
            "type": "Attribute",
        },
    )
    line_shape: Optional[LineShape] = field(
        default=None,
        metadata={
            "name": "line-shape",
            "type": "Attribute",
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    placement: Optional[AboveBelow] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Harmony(BaseModel):
    """The harmony type is based on Humdrum's **harm encoding, extended to support
    chord symbols in popular music as well as functional harmony analysis in
    classical music.

    If there are alternate harmonies possible, this can be specified
    using multiple harmony elements differentiated by type. Explicit
    harmonies have all note present in the music; implied have some
    notes missing but implied; alternate represents alternate analyses.
    The harmony object may be used for analysis or for chord symbols.
    The print-object attribute controls whether or not anything is
    printed due to the harmony element. The print-frame attribute
    controls printing of a frame or fretboard diagram. The print-style
    attribute group sets the default for the harmony, but individual
    elements can override this with their own print-style values.

    :ivar root:
    :ivar function: The function element is used to represent classical
        functional harmony with an indication like I, II, III rather
        than C, D, E. It is relative to the key that is specified in the
        MusicXML encoding.
    :ivar kind:
    :ivar inversion:
    :ivar bass:
    :ivar degree:
    :ivar frame:
    :ivar offset:
    :ivar footnote:
    :ivar level:
    :ivar staff: Staff assignment is only needed for music notated on
        multiple staves. Used by both notes and directions. Staff values
        are numbers, with 1 referring to the top-most staff in a part.
    :ivar type_value:
    :ivar print_object:
    :ivar print_frame:
    :ivar default_x:
    :ivar default_y:
    :ivar relative_x:
    :ivar relative_y:
    :ivar font_family:
    :ivar font_style:
    :ivar font_size:
    :ivar font_weight:
    :ivar color:
    :ivar placement:
    """

    class Meta:
        name = "harmony"

    root: list[Root] = field(
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
    frame: Optional[Frame] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    offset: Optional[Offset] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    footnote: Optional[FormattedText] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    level: Optional[Level] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    staff: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    type_value: Optional[HarmonyType] = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
        },
    )
    print_object: Optional[YesNo] = field(
        default=None,
        metadata={
            "name": "print-object",
            "type": "Attribute",
        },
    )
    print_frame: Optional[YesNo] = field(
        default=None,
        metadata={
            "name": "print-frame",
            "type": "Attribute",
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    placement: Optional[AboveBelow] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Metronome(BaseModel):
    """The metronome type represents metronome marks and other metric
    relationships.

    The beat-unit group and per-minute element specify regular metronome
    marks. The metronome-note and metronome-relation elements allow for
    the specification of more complicated metric relationships, such as
    swing tempo marks where two eighths are equated to a quarter note /
    eighth note triplet. The parentheses attribute indicates whether or
    not to put the metronome mark in parentheses; its value is no if not
    specified.

    :ivar beat_unit: The beat-unit element indicates the graphical note
        type to use in a metronome mark.
    :ivar beat_unit_dot: The beat-unit-dot element is used to specify
        any augmentation dots for a metronome mark note.
    :ivar per_minute:
    :ivar metronome_note:
    :ivar metronome_relation: The metronome-relation element describes
        the relationship symbol that goes between the two sets of
        metronome-note elements. The currently allowed value is equals,
        but this may expand in future versions. If the element is empty,
        the equals value is used.
    :ivar default_x:
    :ivar default_y:
    :ivar relative_x:
    :ivar relative_y:
    :ivar font_family:
    :ivar font_style:
    :ivar font_size:
    :ivar font_weight:
    :ivar color:
    :ivar parentheses:
    """

    class Meta:
        name = "metronome"

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
    per_minute: Optional[PerMinute] = field(
        default=None,
        metadata={
            "name": "per-minute",
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
    metronome_relation: Optional[str] = field(
        default=None,
        metadata={
            "name": "metronome-relation",
            "type": "Element",
        },
    )
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    parentheses: Optional[YesNo] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class Notations(BaseModel):
    """Notations refer to musical notations, not XML notations.

    Multiple notations are allowed in order to represent multiple
    editorial levels. The set of notations may be refined and expanded
    over time, especially to handle more instrument-specific technical
    notations.
    """

    class Meta:
        name = "notations"

    footnote: Optional[FormattedText] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    level: Optional[Level] = field(
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


class ScorePart(BaseModel):
    """Each MusicXML part corresponds to a track in a Standard MIDI Format 1 file.

    The score-instrument elements are used when there are multiple
    instruments per track. The midi-device element is used to make a
    MIDI device or port assignment for the given track. Initial midi-
    instrument assignments may be made here as well.

    :ivar identification:
    :ivar part_name:
    :ivar part_name_display:
    :ivar part_abbreviation:
    :ivar part_abbreviation_display:
    :ivar group: The group element allows the use of different versions
        of the part for different purposes. Typical values include
        score, parts, sound, and data. Ordering information that is
        directly encoded in MuseData can be derived from the ordering
        within a MusicXML score or opus.
    :ivar score_instrument:
    :ivar midi_device:
    :ivar midi_instrument:
    :ivar id:
    """

    class Meta:
        name = "score-part"

    identification: Optional[Identification] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    part_name: Optional[PartName] = field(
        default_factory=PartName,
        metadata={
            "name": "part-name",
            "type": "Element",
            "required": True,
        },
    )
    part_name_display: Optional[NameDisplay] = field(
        default=None,
        metadata={
            "name": "part-name-display",
            "type": "Element",
        },
    )
    part_abbreviation: Optional[PartName] = field(
        default=None,
        metadata={
            "name": "part-abbreviation",
            "type": "Element",
        },
    )
    part_abbreviation_display: Optional[NameDisplay] = field(
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
    midi_device: Optional[MidiDevice] = field(
        default=None,
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
    score_part_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "id",
            "type": "Attribute",
            "required": True,
        },
    )


class DirectionType(BaseModel):
    """Textual direction types may have more than 1 component due to multiple
    fonts.

    The dynamics element may also be used in the notations element.
    Attribute groups related to print suggestions apply to the
    individual direction-type, not to the overall direction.

    :ivar rehearsal:
    :ivar segno: The segno element is the visual indicator of a segno
        sign. A sound element is needed to guide playback applications
        reliably.
    :ivar words: The words element specifies a standard text direction.
        Left justification is assumed if not specified. Language is
        Italian ("it") by default. Enclosure is none by default.
    :ivar coda: The coda element is the visual indicator of a coda sign.
        A sound element is needed to guide playback applications
        reliably.
    :ivar wedge:
    :ivar dynamics:
    :ivar dashes:
    :ivar bracket:
    :ivar pedal:
    :ivar metronome:
    :ivar octave_shift:
    :ivar harp_pedals:
    :ivar damp: The damp element specifies a harp damping mark.
    :ivar damp_all: The damp-all element specifies a harp damping mark
        for all strings.
    :ivar eyeglasses: The eyeglasses element specifies the eyeglasses
        symbol, common in commercial music.
    :ivar scordatura:
    :ivar image:
    :ivar accordion_registration:
    :ivar other_direction:
    """

    class Meta:
        name = "direction-type"

    rehearsal: list[Rehearsal] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    segno: list[EmptyPrintStyle] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    words: list[FormattedText] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    coda: list[EmptyPrintStyle] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    wedge: Optional[Wedge] = field(
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
    dashes: Optional[Dashes] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    bracket: Optional[Bracket] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    pedal: Optional[Pedal] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    metronome: Optional[Metronome] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    octave_shift: Optional[OctaveShift] = field(
        default=None,
        metadata={
            "name": "octave-shift",
            "type": "Element",
        },
    )
    harp_pedals: Optional[HarpPedals] = field(
        default=None,
        metadata={
            "name": "harp-pedals",
            "type": "Element",
        },
    )
    damp: Optional[EmptyPrintStyle] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    damp_all: Optional[EmptyPrintStyle] = field(
        default=None,
        metadata={
            "name": "damp-all",
            "type": "Element",
        },
    )
    eyeglasses: Optional[EmptyPrintStyle] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    scordatura: Optional[Scordatura] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    image: Optional[Image] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    accordion_registration: Optional[AccordionRegistration] = field(
        default=None,
        metadata={
            "name": "accordion-registration",
            "type": "Element",
        },
    )
    other_direction: Optional[OtherDirection] = field(
        default=None,
        metadata={
            "name": "other-direction",
            "type": "Element",
        },
    )


class Note(BaseModel):
    """Notes are the most common type of MusicXML data.

    The MusicXML format keeps the MuseData distinction between elements used for sound information and elements used for notation information (e.g., tie is used for sound, tied for notation). Thus grace notes do not have a duration element. Cue notes have a duration element, as do forward elements, but no tie elements. Having these two types of information available can make interchange considerably easier, as some programs handle one type of information much more readily than the other.
    The dynamics and end-dynamics attributes correspond to MIDI 1.0's Note On and Note Off velocities, respectively. They are expressed in terms of percentages of the default forte value (90 for MIDI 1.0). The attack and release attributes are used to alter the staring and stopping time of the note from when it would otherwise occur based on the flow of durations - information that is specific to a performance. They are expressed in terms of divisions, either positive or negative. A note that starts a tie should not have a release attribute, and a note that stops a tie should not have an attack attribute. If a note is played only one time through a repeat, the time-only attribute shows which time to play the note. The pizzicato attribute is used when just this note is sounded pizzicato, vs. the pizzicato element which changes overall playback between pizzicato and arco.

    :ivar grace:
    :ivar chord: The chord element indicates that this note is an
        additional chord tone with the preceding note. The duration of
        this note can be no longer than the preceding note. In MuseData,
        a missing duration indicates the same length as the previous
        note, but the MusicXML format requires a duration for chord
        notes too.
    :ivar pitch:
    :ivar unpitched: The unpitched element indicates musical elements
        that are notated on the staff but lack definite pitch, such as
        unpitched percussion and speaking voice.
    :ivar rest: The rest element indicates notated rests or silences.
        Rest are usually empty, but placement on the staff can be
        specified using display-step and display-octave elements.
    :ivar tie:
    :ivar cue: The cue element indicates the presence of a cue note.
    :ivar duration: Duration is a positive number specified in division
        units. This is the intended duration vs. notated duration (for
        instance, swing eighths vs. even eighths, or differences in
        dotted notes in Baroque-era music). Differences in duration
        specific to an interpretation or performance should use the note
        element's attack and release attributes.
    :ivar instrument:
    :ivar footnote:
    :ivar level:
    :ivar voice:
    :ivar type_value:
    :ivar dot: One dot element is used for each dot of prolongation. The
        placement element is used to specify whether the dot should
        appear above or below the staff line. It is ignored for notes
        that appear on a staff space.
    :ivar accidental:
    :ivar time_modification:
    :ivar stem:
    :ivar notehead:
    :ivar staff: Staff assignment is only needed for music notated on
        multiple staves. Used by both notes and directions. Staff values
        are numbers, with 1 referring to the top-most staff in a part.
    :ivar beam:
    :ivar notations:
    :ivar lyric:
    :ivar default_x:
    :ivar default_y:
    :ivar relative_x:
    :ivar relative_y:
    :ivar font_family:
    :ivar font_style:
    :ivar font_size:
    :ivar font_weight:
    :ivar color:
    :ivar print_object:
    :ivar print_dot:
    :ivar print_spacing:
    :ivar print_lyric:
    :ivar dynamics:
    :ivar end_dynamics:
    :ivar attack:
    :ivar release:
    :ivar time_only:
    :ivar pizzicato:
    """

    class Meta:
        name = "note"

    grace: Optional[Grace] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        },
    )
    chord: list[Empty] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "max_occurs": 3,
        },
    )
    pitch: list[Pitch] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "max_occurs": 3,
        },
    )
    unpitched: list[DisplayStepOctave] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "max_occurs": 3,
        },
    )
    rest: list[DisplayStepOctave] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "max_occurs": 3,
        },
    )
    tie: list[Tie] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "max_occurs": 4,
        },
    )
    cue: Optional[Empty] = field(
        default=None,
        metadata={
            "type": "Element",
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
    instrument: Optional[Instrument] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    footnote: Optional[FormattedText] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    level: Optional[Level] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    voice: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    type_value: Optional[NoteType] = field(
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
    accidental: Optional[Accidental] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    time_modification: Optional[TimeModification] = field(
        default=None,
        metadata={
            "name": "time-modification",
            "type": "Element",
        },
    )
    stem: Optional[Stem] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    notehead: Optional[Notehead] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    staff: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    beam: list[Beam] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "max_occurs": 6,
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
    default_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-x",
            "type": "Attribute",
        },
    )
    default_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "default-y",
            "type": "Attribute",
        },
    )
    relative_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-x",
            "type": "Attribute",
        },
    )
    relative_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "relative-y",
            "type": "Attribute",
        },
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
            "pattern": r"[^,]+(, ?[^,]+)*",
        },
    )
    font_style: Optional[FontStyle] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        },
    )
    font_size: Optional[Union[Decimal, CssFontSize]] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        },
    )
    font_weight: Optional[FontWeight] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"#[\dA-F]{6}([\dA-F][\dA-F])?",
        },
    )
    print_object: Optional[YesNo] = field(
        default=None,
        metadata={
            "name": "print-object",
            "type": "Attribute",
        },
    )
    print_dot: Optional[YesNo] = field(
        default=None,
        metadata={
            "name": "print-dot",
            "type": "Attribute",
        },
    )
    print_spacing: Optional[YesNo] = field(
        default=None,
        metadata={
            "name": "print-spacing",
            "type": "Attribute",
        },
    )
    print_lyric: Optional[YesNo] = field(
        default=None,
        metadata={
            "name": "print-lyric",
            "type": "Attribute",
        },
    )
    dynamics: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": Decimal("0"),
        },
    )
    end_dynamics: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "end-dynamics",
            "type": "Attribute",
            "min_inclusive": Decimal("0"),
        },
    )
    attack: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    release: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    time_only: Optional[str] = field(
        default=None,
        metadata={
            "name": "time-only",
            "type": "Attribute",
        },
    )
    pizzicato: Optional[YesNo] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class PartList(BaseModel):
    """The part-list identifies the different musical parts in this movement.

    Each part has an ID that is used later within the musical data.
    Since parts may be encoded separately and combined later,
    identification elements are present at both the score and score-part
    levels. There must be at least one score-part, combined as desired
    with part-group elements that indicate braces and brackets. Parts
    are ordered from top to bottom in a score based on the order in
    which they appear in the part-list.

    :ivar part_group:
    :ivar score_part: Each MusicXML part corresponds to a track in a
        Standard MIDI Format 1 file. The score-instrument elements are
        used when there are multiple instruments per track. The midi-
        device element is used to make a MIDI device or port assignment
        for the given track. Initial midi-instrument assignments may be
        made here as well.
    """

    class Meta:
        name = "part-list"

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
    """A direction is a musical indication that is not attached to a specific note.

    Two or more may be combined to indicate starts and stops of wedges,
    dashes, etc. By default, a series of direction-type elements and a
    series of child elements of a direction-type within a single
    direction element follow one another in sequence visually. For a
    series of direction-type children, non-positional formatting
    attributes are carried over from the previous element by default.

    :ivar direction_type:
    :ivar offset:
    :ivar footnote:
    :ivar level:
    :ivar voice:
    :ivar staff: Staff assignment is only needed for music notated on
        multiple staves. Used by both notes and directions. Staff values
        are numbers, with 1 referring to the top-most staff in a part.
    :ivar sound:
    :ivar placement:
    :ivar directive:
    """

    class Meta:
        name = "direction"

    direction_type: list[DirectionType] = field(
        default_factory=list,
        metadata={
            "name": "direction-type",
            "type": "Element",
            "min_occurs": 1,
        },
    )
    offset: Optional[Offset] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    footnote: Optional[FormattedText] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    level: Optional[Level] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    voice: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    staff: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    sound: Optional[Sound] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    placement: Optional[AboveBelow] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    directive: Optional[YesNo] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


class ScorePartwise(BaseModel):
    """The score-partwise element is the root element for a partwise MusicXML
    score.

    It includes a score-header group followed by a series of parts with
    measures inside. The document-attributes attribute group includes
    the version attribute.

    :ivar work:
    :ivar movement_number: The movement-number element specifies the
        number of a movement.
    :ivar movement_title: The movement-title element specifies the title
        of a movement, not including its number.
    :ivar identification:
    :ivar defaults:
    :ivar credit:
    :ivar part_list:
    :ivar part:
    :ivar version:
    """

    class Meta:
        name = "score-partwise"

    work: Optional[Work] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    movement_number: Optional[str] = field(
        default=None,
        metadata={
            "name": "movement-number",
            "type": "Element",
        },
    )
    movement_title: Optional[str] = field(
        default=None,
        metadata={
            "name": "movement-title",
            "type": "Element",
        },
    )
    identification: Optional[Identification] = field(
        default_factory=Identification,
        metadata={
            "type": "Element",
        },
    )
    defaults: Optional[Defaults] = field(
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
        default="1.0",
        metadata={
            "type": "Attribute",
        },
    )

    class Part(BaseModel):
        measure: list["ScorePartwise.Part.Measure"] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "min_occurs": 1,
            },
        )
        part_id: Optional[str] = field(
            default=None,
            metadata={
                "name": "id",
                "type": "Attribute",
                "required": True,
            },
        )

        class Measure(BaseModel):
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
            print_settings: list[Print] = field(
                default_factory=list,
                metadata={
                    "name": "print",
                    "type": "Element",
                },
            )
            sound: list[Sound] = field(
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
            number: Optional[str] = field(
                default=None,
                metadata={
                    "type": "Attribute",
                    "required": True,
                },
            )
            implicit: Optional[YesNo] = field(
                default=None,
                metadata={
                    "type": "Attribute",
                },
            )
            non_controlling: Optional[YesNo] = field(
                default=None,
                metadata={
                    "name": "non-controlling",
                    "type": "Attribute",
                },
            )
            width: Optional[Decimal] = field(
                default=None,
                metadata={
                    "type": "Attribute",
                },
            )


class ScoreTimewise(BaseModel):
    """The score-timewise element is the root element for a timewise MusicXML
    score.

    It includes a score-header group followed by a series of measures
    with parts inside. The document-attributes attribute group includes
    the version attribute.

    :ivar work:
    :ivar movement_number: The movement-number element specifies the
        number of a movement.
    :ivar movement_title: The movement-title element specifies the title
        of a movement, not including its number.
    :ivar identification:
    :ivar defaults:
    :ivar credit:
    :ivar part_list:
    :ivar measure:
    :ivar version:
    """

    class Meta:
        name = "score-timewise"

    work: Optional[Work] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    movement_number: Optional[str] = field(
        default=None,
        metadata={
            "name": "movement-number",
            "type": "Element",
        },
    )
    movement_title: Optional[str] = field(
        default=None,
        metadata={
            "name": "movement-title",
            "type": "Element",
        },
    )
    identification: Optional[Identification] = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    defaults: Optional[Defaults] = field(
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
    part_list: Optional[PartList] = field(
        default=None,
        metadata={
            "name": "part-list",
            "type": "Element",
            "required": True,
        },
    )
    measure: list["ScoreTimewise.Measure"] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )
    version: str = field(
        default="1.0",
        metadata={
            "type": "Attribute",
        },
    )

    class Measure(BaseModel):
        part: list["ScoreTimewise.Measure.Part"] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "min_occurs": 1,
            },
        )
        number: Optional[str] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "required": True,
            },
        )
        implicit: Optional[YesNo] = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )
        non_controlling: Optional[YesNo] = field(
            default=None,
            metadata={
                "name": "non-controlling",
                "type": "Attribute",
            },
        )
        width: Optional[Decimal] = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )

        class Part(BaseModel):
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
            print_settings: list[Print] = field(
                default_factory=list,
                metadata={
                    "name": "print",
                    "type": "Element",
                },
            )
            sound: list[Sound] = field(
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
            part_id: Optional[str] = field(
                default=None,
                metadata={
                    "name": "id",
                    "type": "Attribute",
                    "required": True,
                },
            )
