from enum import Enum


class ActuateValue(Enum):
    ON_REQUEST = "onRequest"
    ON_LOAD = "onLoad"
    OTHER = "other"
    NONE = "none"


class ShowValue(Enum):
    NEW = "new"
    REPLACE = "replace"
    EMBED = "embed"
    OTHER = "other"
    NONE = "none"


class TypeValue(Enum):
    SIMPLE = "simple"


class LangValue(Enum):
    VALUE = ""


class SpaceValue(Enum):
    DEFAULT = "default"
    PRESERVE = "preserve"


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
    The quarter- and three-quarters- accidentals are Tartini-style
    quarter-tone accidentals. The -down and -up accidentals are quarter-
    tone accidentals that include arrows pointing down or up. The slash-
    accidentals are used in Turkish classical music. The numbered sharp
    and flat accidentals are superscripted versions of the accidental
    signs, used in Turkish folk music. The sori and koron accidentals
    are microtonal sharp and flat accidentals used in Iranian and
    Persian music. The other accidental covers accidentals other than
    those listed here. It is usually used in combination with the smufl
    attribute to specify a particular SMuFL accidental. The smufl
    attribute may be used with any accidental value to help specify the
    appearance of symbols that share the same MusicXML semantics.
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
    SHARP_DOWN = "sharp-down"
    SHARP_UP = "sharp-up"
    NATURAL_DOWN = "natural-down"
    NATURAL_UP = "natural-up"
    FLAT_DOWN = "flat-down"
    FLAT_UP = "flat-up"
    DOUBLE_SHARP_DOWN = "double-sharp-down"
    DOUBLE_SHARP_UP = "double-sharp-up"
    FLAT_FLAT_DOWN = "flat-flat-down"
    FLAT_FLAT_UP = "flat-flat-up"
    ARROW_DOWN = "arrow-down"
    ARROW_UP = "arrow-up"
    TRIPLE_SHARP = "triple-sharp"
    TRIPLE_FLAT = "triple-flat"
    SLASH_QUARTER_SHARP = "slash-quarter-sharp"
    SLASH_SHARP = "slash-sharp"
    SLASH_FLAT = "slash-flat"
    DOUBLE_SLASH_FLAT = "double-slash-flat"
    SHARP_1 = "sharp-1"
    SHARP_2 = "sharp-2"
    SHARP_3 = "sharp-3"
    SHARP_5 = "sharp-5"
    FLAT_1 = "flat-1"
    FLAT_2 = "flat-2"
    FLAT_3 = "flat-3"
    FLAT_4 = "flat-4"
    SORI = "sori"
    KORON = "koron"
    OTHER = "other"


class ArrowDirection(Enum):
    """
    The arrow-direction type represents the direction in which an arrow points,
    using Unicode arrow terminology.
    """

    LEFT = "left"
    UP = "up"
    RIGHT = "right"
    DOWN = "down"
    NORTHWEST = "northwest"
    NORTHEAST = "northeast"
    SOUTHEAST = "southeast"
    SOUTHWEST = "southwest"
    LEFT_RIGHT = "left right"
    UP_DOWN = "up down"
    NORTHWEST_SOUTHEAST = "northwest southeast"
    NORTHEAST_SOUTHWEST = "northeast southwest"
    OTHER = "other"


class ArrowStyle(Enum):
    """The arrow-style type represents the style of an arrow, using Unicode arrow
    terminology.

    Filled and hollow arrows indicate polygonal single arrows. Paired
    arrows are duplicate single arrows in the same direction. Combined
    arrows apply to double direction arrows like left right, indicating
    that an arrow in one direction should be combined with an arrow in
    the other direction.
    """

    SINGLE = "single"
    DOUBLE = "double"
    FILLED = "filled"
    HOLLOW = "hollow"
    PAIRED = "paired"
    COMBINED = "combined"
    OTHER = "other"


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
    The beam-value type represents the type of beam associated with each of 8 beam
    levels (up to 1024th notes) available for each note.
    """

    BEGIN = "begin"
    CONTINUE = "continue"
    END = "end"
    FORWARD_HOOK = "forward hook"
    BACKWARD_HOOK = "backward hook"


class BeaterValue(Enum):
    """The beater-value type represents pictograms for beaters, mallets, and sticks
    that do not have different materials represented in the pictogram.

    The finger and hammer values are in addition to Stone's list.
    """

    BOW = "bow"
    CHIME_HAMMER = "chime hammer"
    COIN = "coin"
    DRUM_STICK = "drum stick"
    FINGER = "finger"
    FINGERNAIL = "fingernail"
    FIST = "fist"
    GUIRO_SCRAPER = "guiro scraper"
    HAMMER = "hammer"
    HAND = "hand"
    JAZZ_STICK = "jazz stick"
    KNITTING_NEEDLE = "knitting needle"
    METAL_HAMMER = "metal hammer"
    SLIDE_BRUSH_ON_GONG = "slide brush on gong"
    SNARE_STICK = "snare stick"
    SPOON_MALLET = "spoon mallet"
    SUPERBALL = "superball"
    TRIANGLE_BEATER = "triangle beater"
    TRIANGLE_BEATER_PLAIN = "triangle beater plain"
    WIRE_BRUSH = "wire brush"


class BendShape(Enum):
    """
    The bend-shape type distinguishes between the angled bend symbols commonly used
    in standard notation and the curved bend symbols commonly used in both
    tablature and standard notation.
    """

    ANGLED = "angled"
    CURVED = "curved"


class BreathMarkValue(Enum):
    """
    The breath-mark-value type represents the symbol used for a breath mark.
    """

    VALUE = ""
    COMMA = "comma"
    TICK = "tick"
    UPBOW = "upbow"
    SALZEDO = "salzedo"


class CaesuraValue(Enum):
    """
    The caesura-value type represents the shape of the caesura sign.
    """

    NORMAL = "normal"
    THICK = "thick"
    SHORT = "short"
    CURVED = "curved"
    SINGLE = "single"
    VALUE = ""


class CancelLocation(Enum):
    """The cancel-location type is used to indicate where a key signature cancellation appears relative to a new key signature: to the left, to the right, or before the barline and to the left. It is left by default. For mid-measure key elements, a cancel-location of before-barline should be treated like a cancel-location of left."""

    LEFT = "left"
    RIGHT = "right"
    BEFORE_BARLINE = "before-barline"


class CircularArrow(Enum):
    """
    The circular-arrow type represents the direction in which a circular arrow
    points, using Unicode arrow terminology.
    """

    CLOCKWISE = "clockwise"
    ANTICLOCKWISE = "anticlockwise"


class ClefSign(Enum):
    """The clef-sign type represents the different clef symbols.

    The jianpu sign indicates that the music that follows should be in
    jianpu numbered notation, just as the TAB sign indicates that the
    music that follows should be in tablature notation. Unlike TAB, a
    jianpu sign does not correspond to a visual clef notation. The none
    sign is deprecated as of MusicXML 4.0. Use the clef element's print-
    object attribute instead. When the none sign is used, notes should
    be displayed as if in treble clef.
    """

    G = "G"
    F = "F"
    C = "C"
    PERCUSSION = "percussion"
    TAB = "TAB"
    JIANPU = "jianpu"
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


class DegreeSymbolValue(Enum):
    """
    The degree-symbol-value type indicates which symbol should be used in
    specifying a degree.
    """

    MAJOR = "major"
    MINOR = "minor"
    AUGMENTED = "augmented"
    DIMINISHED = "diminished"
    HALF_DIMINISHED = "half-diminished"


class DegreeTypeValue(Enum):
    """
    The degree-type-value type indicates whether the current degree element is an
    addition, alteration, or subtraction to the kind of the current chord in the
    harmony element.
    """

    ADD = "add"
    ALTER = "alter"
    SUBTRACT = "subtract"


class EffectValue(Enum):
    """The effect-value type represents pictograms for sound effect percussion
    instruments.

    The cannon, lotus flute, and megaphone values are in addition to
    Stone's list.
    """

    ANVIL = "anvil"
    AUTO_HORN = "auto horn"
    BIRD_WHISTLE = "bird whistle"
    CANNON = "cannon"
    DUCK_CALL = "duck call"
    GUN_SHOT = "gun shot"
    KLAXON_HORN = "klaxon horn"
    LIONS_ROAR = "lions roar"
    LOTUS_FLUTE = "lotus flute"
    MEGAPHONE = "megaphone"
    POLICE_WHISTLE = "police whistle"
    SIREN = "siren"
    SLIDE_WHISTLE = "slide whistle"
    THUNDER_SHEET = "thunder sheet"
    WIND_MACHINE = "wind machine"
    WIND_WHISTLE = "wind whistle"


class EnclosureShape(Enum):
    """The enclosure-shape type describes the shape and presence / absence of an
    enclosure around text or symbols.

    A bracket enclosure is similar to a rectangle with the bottom line
    missing, as is common in jazz notation. An inverted-bracket
    enclosure is similar to a rectangle with the top line missing.
    """

    RECTANGLE = "rectangle"
    SQUARE = "square"
    OVAL = "oval"
    CIRCLE = "circle"
    BRACKET = "bracket"
    INVERTED_BRACKET = "inverted-bracket"
    TRIANGLE = "triangle"
    DIAMOND = "diamond"
    PENTAGON = "pentagon"
    HEXAGON = "hexagon"
    HEPTAGON = "heptagon"
    OCTAGON = "octagon"
    NONAGON = "nonagon"
    DECAGON = "decagon"
    NONE = "none"


class Fan(Enum):
    """
    The fan type represents the type of beam fanning present on a note, used to
    represent accelerandos and ritardandos.
    """

    ACCEL = "accel"
    RIT = "rit"
    NONE = "none"


class FermataShape(Enum):
    """The fermata-shape type represents the shape of the fermata sign.

    The empty value is equivalent to the normal value.
    """

    NORMAL = "normal"
    ANGLED = "angled"
    SQUARE = "square"
    DOUBLE_ANGLED = "double-angled"
    DOUBLE_SQUARE = "double-square"
    DOUBLE_DOT = "double-dot"
    HALF_CURVE = "half-curve"
    CURLEW = "curlew"
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


class GlassValue(Enum):
    """
    The glass-value type represents pictograms for glass percussion instruments.
    """

    GLASS_HARMONICA = "glass harmonica"
    GLASS_HARP = "glass harp"
    WIND_CHIMES = "wind chimes"


class GroupBarlineValue(Enum):
    """
    The group-barline-value type indicates if the group should have common
    barlines.
    """

    YES = "yes"
    NO = "no"
    MENSURSTRICH = "Mensurstrich"


class GroupSymbolValue(Enum):
    """
    The group-symbol-value type indicates how the symbol for a group or multi-staff
    part is indicated in the score.
    """

    NONE = "none"
    BRACE = "brace"
    LINE = "line"
    BRACKET = "bracket"
    SQUARE = "square"


class HandbellValue(Enum):
    """
    The handbell-value type represents the type of handbell technique being
    notated.
    """

    BELLTREE = "belltree"
    DAMP = "damp"
    ECHO = "echo"
    GYRO = "gyro"
    HAND_MARTELLATO = "hand martellato"
    MALLET_LIFT = "mallet lift"
    MALLET_TABLE = "mallet table"
    MARTELLATO = "martellato"
    MARTELLATO_LIFT = "martellato lift"
    MUTED_MARTELLATO = "muted martellato"
    PLUCK_LIFT = "pluck lift"
    SWING = "swing"


class HarmonClosedLocation(Enum):
    """
    The harmon-closed-location type indicates which portion of the symbol is filled
    in when the corresponding harmon-closed-value is half.
    """

    RIGHT = "right"
    BOTTOM = "bottom"
    LEFT = "left"
    TOP = "top"


class HarmonClosedValue(Enum):
    """
    The harmon-closed-value type represents whether the harmon mute is closed,
    open, or half-open.
    """

    YES = "yes"
    NO = "no"
    HALF = "half"


class HarmonyArrangement(Enum):
    """The harmony-arrangement type indicates how stacked chords and bass notes are
    displayed within a harmony element.

    The vertical value specifies that the second element appears below
    the first. The horizontal value specifies that the second element
    appears to the right of the first. The diagonal value specifies that
    the second element appears both below and to the right of the first.
    """

    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"
    DIAGONAL = "diagonal"


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


class HoleClosedLocation(Enum):
    """
    The hole-closed-location type indicates which portion of the hole is filled in
    when the corresponding hole-closed-value is half.
    """

    RIGHT = "right"
    BOTTOM = "bottom"
    LEFT = "left"
    TOP = "top"


class HoleClosedValue(Enum):
    """
    The hole-closed-value type represents whether the hole is closed, open, or
    half-open.
    """

    YES = "yes"
    NO = "no"
    HALF = "half"


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
    The "other" kind is used when the harmony is entirely composed of add elements.
    The "none" kind is used to explicitly encode absence of chords or functional harmony. In this case, the root, numeral, or function element has no meaning. When using the root or numeral element, the root-step or numeral-step text attribute should be set to the empty string to keep the root or numeral from being displayed.
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


class LineLength(Enum):
    """
    The line-length type distinguishes between different line lengths for doit,
    falloff, plop, and scoop articulations.
    """

    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"


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


class MarginType(Enum):
    """
    The margin-type type specifies whether margins apply to even page, odd pages,
    or both.
    """

    ODD = "odd"
    EVEN = "even"
    BOTH = "both"


class MeasureNumberingValue(Enum):
    """The measure-numbering-value type describes how measure numbers are displayed on this part: no numbers, numbers every measure, or numbers every system."""

    NONE = "none"
    MEASURE = "measure"
    SYSTEM = "system"


class MembraneValue(Enum):
    """
    The membrane-value type represents pictograms for membrane percussion
    instruments.
    """

    BASS_DRUM = "bass drum"
    BASS_DRUM_ON_SIDE = "bass drum on side"
    BONGOS = "bongos"
    CHINESE_TOMTOM = "Chinese tomtom"
    CONGA_DRUM = "conga drum"
    CUICA = "cuica"
    GOBLET_DRUM = "goblet drum"
    INDO_AMERICAN_TOMTOM = "Indo-American tomtom"
    JAPANESE_TOMTOM = "Japanese tomtom"
    MILITARY_DRUM = "military drum"
    SNARE_DRUM = "snare drum"
    SNARE_DRUM_SNARES_OFF = "snare drum snares off"
    TABLA = "tabla"
    TAMBOURINE = "tambourine"
    TENOR_DRUM = "tenor drum"
    TIMBALES = "timbales"
    TOMTOM = "tomtom"


class MetalValue(Enum):
    """The metal-value type represents pictograms for metal percussion instruments.

    The hi-hat value refers to a pictogram like Stone's high-hat cymbals
    but without the long vertical line at the bottom.
    """

    AGOGO = "agogo"
    ALMGLOCKEN = "almglocken"
    BELL = "bell"
    BELL_PLATE = "bell plate"
    BELL_TREE = "bell tree"
    BRAKE_DRUM = "brake drum"
    CENCERRO = "cencerro"
    CHAIN_RATTLE = "chain rattle"
    CHINESE_CYMBAL = "Chinese cymbal"
    COWBELL = "cowbell"
    CRASH_CYMBALS = "crash cymbals"
    CROTALE = "crotale"
    CYMBAL_TONGS = "cymbal tongs"
    DOMED_GONG = "domed gong"
    FINGER_CYMBALS = "finger cymbals"
    FLEXATONE = "flexatone"
    GONG = "gong"
    HI_HAT = "hi-hat"
    HIGH_HAT_CYMBALS = "high-hat cymbals"
    HANDBELL = "handbell"
    JAW_HARP = "jaw harp"
    JINGLE_BELLS = "jingle bells"
    MUSICAL_SAW = "musical saw"
    SHELL_BELLS = "shell bells"
    SISTRUM = "sistrum"
    SIZZLE_CYMBAL = "sizzle cymbal"
    SLEIGH_BELLS = "sleigh bells"
    SUSPENDED_CYMBAL = "suspended cymbal"
    TAM_TAM = "tam tam"
    TAM_TAM_WITH_BEATER = "tam tam with beater"
    TRIANGLE = "triangle"
    VIETNAMESE_HAT = "Vietnamese hat"


class Mute(Enum):
    """The mute type represents muting for different instruments, including brass,
    winds, and strings.

    The on and off values are used for undifferentiated mutes. The
    remaining values represent specific mutes.
    """

    ON = "on"
    OFF = "off"
    STRAIGHT = "straight"
    CUP = "cup"
    HARMON_NO_STEM = "harmon-no-stem"
    HARMON_STEM = "harmon-stem"
    BUCKET = "bucket"
    PLUNGER = "plunger"
    HAT = "hat"
    SOLOTONE = "solotone"
    PRACTICE = "practice"
    STOP_MUTE = "stop-mute"
    STOP_HAND = "stop-hand"
    ECHO = "echo"
    PALM = "palm"


class NoteSizeType(Enum):
    """The note-size-type type indicates the type of note being defined by a note-
    size element.

    The grace-cue type is used for notes of grace-cue size. The grace
    type is used for notes of cue size that include a grace element. The
    cue type is used for all other notes with cue size, whether defined
    explicitly or implicitly via a cue element. The large type is used
    for notes of large size.
    """

    CUE = "cue"
    GRACE = "grace"
    GRACE_CUE = "grace-cue"
    LARGE = "large"


class NoteTypeValue(Enum):
    """
    The note-type-value type is used for the MusicXML type element and represents
    the graphic note type, from 1024th (shortest) to maxima (longest).
    """

    VALUE_1024TH = "1024th"
    VALUE_512TH = "512th"
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
    MAXIMA = "maxima"


class NoteheadValue(Enum):
    """The notehead-value type indicates shapes other than the open and closed
    ovals associated with note durations.

    The values do, re, mi, fa, fa up, so, la, and ti correspond to
    Aikin's 7-shape system.  The fa up shape is typically used with
    upstems; the fa shape is typically used with downstems or no stems.
    The arrow shapes differ from triangle and inverted triangle by being
    centered on the stem. Slashed and back slashed notes include both
    the normal notehead and a slash. The triangle shape has the tip of
    the triangle pointing up; the inverted triangle shape has the tip of
    the triangle pointing down. The left triangle shape is a right
    triangle with the hypotenuse facing up and to the left. The other
    notehead covers noteheads other than those listed here. It is
    usually used in combination with the smufl attribute to specify a
    particular SMuFL notehead. The smufl attribute may be used with any
    notehead value to help specify the appearance of symbols that share
    the same MusicXML semantics. Noteheads in the SMuFL Note name
    noteheads and Note name noteheads supplement ranges (U+E150-U+E1AF
    and U+EEE0-U+EEFF) should not use the smufl attribute or the "other"
    value, but instead use the notehead-text element.
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
    CIRCLED = "circled"
    SLASHED = "slashed"
    BACK_SLASHED = "back slashed"
    NORMAL = "normal"
    CLUSTER = "cluster"
    CIRCLE_DOT = "circle dot"
    LEFT_TRIANGLE = "left triangle"
    RECTANGLE = "rectangle"
    NONE = "none"
    DO = "do"
    RE = "re"
    MI = "mi"
    FA = "fa"
    FA_UP = "fa up"
    SO = "so"
    LA = "la"
    TI = "ti"
    OTHER = "other"


class NumberOrNormalValue(Enum):
    NORMAL = "normal"


class NumeralMode(Enum):
    """The numeral-mode type specifies the mode similar to the mode type, but with
    a restricted set of values.

    The different minor values are used to interpret numeral-root values
    of 6 and 7 when present in a minor key. The harmonic minor value
    sharpens the 7 and the melodic minor value sharpens both 6 and 7. If
    a minor mode is used without qualification, either in the mode or
    numeral-mode elements, natural minor is used.
    """

    MAJOR = "major"
    MINOR = "minor"
    NATURAL_MINOR = "natural minor"
    MELODIC_MINOR = "melodic minor"
    HARMONIC_MINOR = "harmonic minor"


class OnOff(Enum):
    """
    The on-off type is used for notation elements such as string mutes.
    """

    ON = "on"
    OFF = "off"


class OverUnder(Enum):
    """
    The over-under type is used to indicate whether the tips of curved lines such
    as slurs and ties are overhand (tips down) or underhand (tips up).
    """

    OVER = "over"
    UNDER = "under"


class PedalType(Enum):
    """The pedal-type simple type is used to distinguish types of pedal directions.

    The start value indicates the start of a damper pedal, while the
    sostenuto value indicates the start of a sostenuto pedal. The other
    values can be used with either the damper or sostenuto pedal. The
    soft pedal is not included here because there is no special symbol
    or graphic used for it beyond what can be specified with words and
    bracket elements. The change, continue, discontinue, and resume
    types are used when the line attribute is yes. The change type
    indicates a pedal lift and retake indicated with an inverted V
    marking. The continue type allows more precise formatting across
    system breaks and for more complex pedaling lines. The discontinue
    type indicates the end of a pedal line that does not include the
    explicit lift represented by the stop type. The resume type
    indicates the start of a pedal line that does not include the
    downstroke represented by the start type. It can be used when a line
    resumes after being discontinued, or to start a pedal line that is
    preceded by a text or symbol representation of the pedal.
    """

    START = "start"
    STOP = "stop"
    SOSTENUTO = "sostenuto"
    CHANGE = "change"
    CONTINUE = "continue"
    DISCONTINUE = "discontinue"
    RESUME = "resume"


class PitchedValue(Enum):
    """The pitched-value type represents pictograms for pitched percussion
    instruments.

    The chimes and tubular chimes values distinguish the single-line and
    double-line versions of the pictogram.
    """

    CELESTA = "celesta"
    CHIMES = "chimes"
    GLOCKENSPIEL = "glockenspiel"
    LITHOPHONE = "lithophone"
    MALLET = "mallet"
    MARIMBA = "marimba"
    STEEL_DRUMS = "steel drums"
    TUBAPHONE = "tubaphone"
    TUBULAR_CHIMES = "tubular chimes"
    VIBRAPHONE = "vibraphone"
    XYLOPHONE = "xylophone"


class PositiveIntegerOrEmptyValue(Enum):
    VALUE = ""


class PrincipalVoiceSymbol(Enum):
    """The principal-voice-symbol type represents the type of symbol used to
    indicate a principal or secondary voice.

    The "plain" value represents a plain square bracket. The value of
    "none" is used for analysis markup when the principal-voice element
    does not have a corresponding appearance in the score.
    """

    HAUPTSTIMME = "Hauptstimme"
    NEBENSTIMME = "Nebenstimme"
    PLAIN = "plain"
    NONE = "none"


class RightLeftMiddle(Enum):
    """
    The right-left-middle type is used to specify barline location.
    """

    RIGHT = "right"
    LEFT = "left"
    MIDDLE = "middle"


class SemiPitched(Enum):
    """
    The semi-pitched type represents categories of indefinite pitch for percussion
    instruments.
    """

    HIGH = "high"
    MEDIUM_HIGH = "medium-high"
    MEDIUM = "medium"
    MEDIUM_LOW = "medium-low"
    LOW = "low"
    VERY_LOW = "very-low"


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


class StaffDivideSymbol(Enum):
    """The staff-divide-symbol type is used for staff division symbols.

    The down, up, and up-down values correspond to SMuFL code points
    U+E00B, U+E00C, and U+E00D respectively.
    """

    DOWN = "down"
    UP = "up"
    UP_DOWN = "up-down"


class StaffType(Enum):
    """The staff-type value can be ossia, editorial, cue, alternate, or regular.

    An ossia staff represents music that can be played instead of what
    appears on the regular staff. An editorial staff also represents
    musical alternatives, but is created by an editor rather than the
    composer. It can be used for suggested interpretations or
    alternatives from other sources. A cue staff represents music from
    another part. An alternate staff shares the same music as the prior
    staff, but displayed differently (e.g., treble and bass clef,
    standard notation and tablature). It is not included in playback. An
    alternate staff provides more information to an application reading
    a file than encoding the same music in separate parts, so its use is
    preferred in this situation if feasible. A regular staff is the
    standard default staff-type.
    """

    OSSIA = "ossia"
    EDITORIAL = "editorial"
    CUE = "cue"
    ALTERNATE = "alternate"
    REGULAR = "regular"


class StartNote(Enum):
    """
    The start-note type describes the starting note of trills and mordents for
    playback, relative to the current note.
    """

    UPPER = "upper"
    MAIN = "main"
    BELOW = "below"


class StartStop(Enum):
    """The start-stop type is used for an attribute of musical elements that can
    either start or stop, such as tuplets.

    The values of start and stop refer to how an element appears in
    musical score order, not in MusicXML document order. An element with
    a stop attribute may precede the corresponding element with a start
    attribute within a MusicXML document. This is particularly common in
    multi-staff music. For example, the stopping point for a tuplet may
    appear in staff 1 before the starting point for the tuplet appears
    in staff 2 later in the document. When multiple elements with the
    same tag are used within the same note, their order within the
    MusicXML document should match the musical score order.
    """

    START = "start"
    STOP = "stop"


class StartStopContinue(Enum):
    """The start-stop-continue type is used for an attribute of musical elements
    that can either start or stop, but also need to refer to an intermediate point
    in the symbol, as for complex slurs or for formatting of symbols across system
    breaks.

    The values of start, stop, and continue refer to how an element
    appears in musical score order, not in MusicXML document order. An
    element with a stop attribute may precede the corresponding element
    with a start attribute within a MusicXML document. This is
    particularly common in multi-staff music. For example, the stopping
    point for a slur may appear in staff 1 before the starting point for
    the slur appears in staff 2 later in the document. When multiple
    elements with the same tag are used within the same note, their
    order within the MusicXML document should match the musical score
    order. For example, a note that marks both the end of one slur and
    the start of a new slur should have the incoming slur element with a
    type of stop precede the outgoing slur element with a type of start.
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
    """The start-stop-single type is used for an attribute of musical elements that
    can be used for either multi-note or single-note musical elements, as for
    groupings.

    When multiple elements with the same tag are used within the same
    note, their order within the MusicXML document should match the
    musical score order.
    """

    START = "start"
    STOP = "stop"
    SINGLE = "single"


class StemValue(Enum):
    """
    The stem-value type represents the notated stem direction.
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


class StickLocation(Enum):
    """
    The stick-location type represents pictograms for the location of sticks,
    beaters, or mallets on cymbals, gongs, drums, and other instruments.
    """

    CENTER = "center"
    RIM = "rim"
    CYMBAL_BELL = "cymbal bell"
    CYMBAL_EDGE = "cymbal edge"


class StickMaterial(Enum):
    """
    The stick-material type represents the material being displayed in a stick
    pictogram.
    """

    SOFT = "soft"
    MEDIUM = "medium"
    HARD = "hard"
    SHADED = "shaded"
    X = "x"


class StickType(Enum):
    """
    The stick-type type represents the shape of pictograms where the material in
    the stick, mallet, or beater is represented in the pictogram.
    """

    BASS_DRUM = "bass drum"
    DOUBLE_BASS_DRUM = "double bass drum"
    GLOCKENSPIEL = "glockenspiel"
    GUM = "gum"
    HAMMER = "hammer"
    SUPERBALL = "superball"
    TIMPANI = "timpani"
    WOUND = "wound"
    XYLOPHONE = "xylophone"
    YARN = "yarn"


class SwingTypeValue(Enum):
    """
    The swing-type-value type specifies the note type, either eighth or 16th, to
    which the ratio defined in the swing element is applied.
    """

    VALUE_16TH = "16th"
    EIGHTH = "eighth"


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
    """
    The symbol-size type is used to distinguish between full, cue sized, grace cue
    sized, and oversized symbols.
    """

    FULL = "full"
    CUE = "cue"
    GRACE_CUE = "grace-cue"
    LARGE = "large"


class SyncType(Enum):
    """The sync-type type specifies the style that a score following application
    should use to synchronize an accompaniment with a performer.

    The none type indicates no synchronization to the performer. The
    tempo type indicates synchronization based on the performer tempo
    rather than individual events in the score. The event type indicates
    synchronization by following the performance of individual events in
    the score rather than the performer tempo. The mostly-tempo and
    mostly-event types combine these two approaches, with mostly-tempo
    giving more weight to tempo and mostly-event giving more weight to
    performed events. The always-event type provides the strictest
    synchronization by not being forgiving of missing performed events.
    """

    NONE = "none"
    TEMPO = "tempo"
    MOSTLY_TEMPO = "mostly-tempo"
    MOSTLY_EVENT = "mostly-event"
    EVENT = "event"
    ALWAYS_EVENT = "always-event"


class SystemRelation(Enum):
    """The system-relation type distinguishes elements that are associated with a
    system rather than the particular part where the element appears.

    A value of only-top indicates that the element should appear only on
    the top part of the current system. A value of also-top indicates
    that the element should appear on both the current part and the top
    part of the current system. If this value appears in a score, when
    parts are created the element should only appear once in this part,
    not twice. A value of none indicates that the element is associated
    only with the current part, not with the system.
    """

    ONLY_TOP = "only-top"
    ALSO_TOP = "also-top"
    NONE = "none"


class SystemRelationNumber(Enum):
    """The system-relation-number type distinguishes measure numbers that are
    associated with a system rather than the particular part where the element
    appears.

    A value of only-top or only-bottom indicates that the number should
    appear only on the top or bottom part of the current system,
    respectively. A value of also-top or also-bottom indicates that the
    number should appear on both the current part and the top or bottom
    part of the current system, respectively. If these values appear in
    a score, when parts are created the number should only appear once
    in this part, not twice. A value of none indicates that the number
    is associated only with the current part, not with the system.
    """

    ONLY_TOP = "only-top"
    ONLY_BOTTOM = "only-bottom"
    ALSO_TOP = "also-top"
    ALSO_BOTTOM = "also-bottom"
    NONE = "none"


class TapHand(Enum):
    """The tap-hand type represents the symbol to use for a tap element.

    The left and right values refer to the SMuFL guitarLeftHandTapping
    and guitarRightHandTapping glyphs respectively.
    """

    LEFT = "left"
    RIGHT = "right"


class TextDirection(Enum):
    """The text-direction type is used to adjust and override the Unicode
    bidirectional text algorithm, similar to the Directionality data category in
    the W3C Internationalization Tag Set recommendation.

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


class TiedType(Enum):
    """The tied-type type is used as an attribute of the tied element to specify
    where the visual representation of a tie begins and ends.

    A tied element which joins two notes of the same pitch can be
    specified with tied-type start on the first note and tied-type stop
    on the second note. To indicate a note should be undamped, use a
    single tied element with tied-type let-ring. For other ties that are
    visually attached to a single note, such as a tie leading into or
    out of a repeated section or coda, use two tied elements on the same
    note, one start and one stop. In start-stop cases, ties can add more
    elements using a continue type. This is typically used to specify
    the formatting of cross-system ties. When multiple elements with the
    same tag are used within the same note, their order within the
    MusicXML document should match the musical score order. For example,
    a note with a tie at the end of a first ending should have the tied
    element with a type of start precede the tied element with a type of
    stop.
    """

    START = "start"
    STOP = "stop"
    CONTINUE = "continue"
    LET_RING = "let-ring"


class TimeRelation(Enum):
    """
    The time-relation type indicates the symbol used to represent the
    interchangeable aspect of dual time signatures.
    """

    PARENTHESES = "parentheses"
    BRACKET = "bracket"
    EQUALS = "equals"
    SLASH = "slash"
    SPACE = "space"
    HYPHEN = "hyphen"


class TimeSeparator(Enum):
    """The time-separator type indicates how to display the arrangement between the
    beats and beat-type values in a time signature.

    The default value is none. The horizontal, diagonal, and vertical
    values represent horizontal, diagonal lower-left to upper-right, and
    vertical lines respectively. For these values, the beats and beat-
    type values are arranged on either side of the separator line. The
    none value represents no separator with the beats and beat-type
    arranged vertically. The adjacent value represents no separator with
    the beats and beat-type arranged horizontally.
    """

    NONE = "none"
    HORIZONTAL = "horizontal"
    DIAGONAL = "diagonal"
    VERTICAL = "vertical"
    ADJACENT = "adjacent"


class TimeSymbol(Enum):
    """The time-symbol type indicates how to display a time signature.

    The normal value is the usual fractional display, and is the implied
    symbol type if none is specified. Other options are the common and
    cut time symbols, as well as a single number with an implied
    denominator. The note symbol indicates that the beat-type should be
    represented with the corresponding downstem note rather than a
    number. The dotted-note symbol indicates that the beat-type should
    be represented with a dotted downstem note that corresponds to three
    times the beat-type value, and a numerator that is one third the
    beats value.
    """

    COMMON = "common"
    CUT = "cut"
    SINGLE_NUMBER = "single-number"
    NOTE = "note"
    DOTTED_NOTE = "dotted-note"
    NORMAL = "normal"


class TipDirection(Enum):
    """
    The tip-direction type represents the direction in which the tip of a stick or
    beater points, using Unicode arrow terminology.
    """

    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    NORTHWEST = "northwest"
    NORTHEAST = "northeast"
    SOUTHEAST = "southeast"
    SOUTHWEST = "southwest"


class TopBottom(Enum):
    """
    The top-bottom type is used to indicate the top or bottom part of a vertical
    shape like non-arpeggiate.
    """

    TOP = "top"
    BOTTOM = "bottom"


class TremoloType(Enum):
    """
    The tremolo-type is used to distinguish double-note, single-note, and
    unmeasured tremolos.
    """

    START = "start"
    STOP = "stop"
    SINGLE = "single"
    UNMEASURED = "unmeasured"


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


class UpDown(Enum):
    """
    The up-down type is used for the direction of arrows and other pointed symbols
    like vertical accents, indicating which way the tip is pointing.
    """

    UP = "up"
    DOWN = "down"


class UpDownStopContinue(Enum):
    """
    The up-down-stop-continue type is used for octave-shift elements, indicating
    the direction of the shift from their true pitched values because of printing
    difficulty.
    """

    UP = "up"
    DOWN = "down"
    STOP = "stop"
    CONTINUE = "continue"


class UprightInverted(Enum):
    """The upright-inverted type describes the appearance of a fermata element.

    The value is upright if not specified.
    """

    UPRIGHT = "upright"
    INVERTED = "inverted"


class Valign(Enum):
    """The valign type is used to indicate vertical alignment to the top, middle,
    bottom, or baseline of the text.

    If the text is on multiple lines, baseline alignment refers to the
    baseline of the lowest line of text. Defaults are implementation-
    dependent.
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
    """The wedge type is crescendo for the start of a wedge that is closed at the
    left side, diminuendo for the start of a wedge that is closed on the right
    side, and stop for the end of a wedge.

    The continue type is used for formatting wedges over a system break,
    or for other situations where a single wedge is divided into
    multiple segments.
    """

    CRESCENDO = "crescendo"
    DIMINUENDO = "diminuendo"
    STOP = "stop"
    CONTINUE = "continue"


class Winged(Enum):
    """The winged attribute indicates whether the repeat has winged extensions that
    appear above and below the barline.

    The straight and curved values represent single wings, while the
    double-straight and double-curved values represent double wings. The
    none value indicates no wings and is the default.
    """

    NONE = "none"
    STRAIGHT = "straight"
    CURVED = "curved"
    DOUBLE_STRAIGHT = "double-straight"
    DOUBLE_CURVED = "double-curved"


class WoodValue(Enum):
    """The wood-value type represents pictograms for wood percussion instruments.

    The maraca and maracas values distinguish the one- and two-maraca
    versions of the pictogram.
    """

    BAMBOO_SCRAPER = "bamboo scraper"
    BOARD_CLAPPER = "board clapper"
    CABASA = "cabasa"
    CASTANETS = "castanets"
    CASTANETS_WITH_HANDLE = "castanets with handle"
    CLAVES = "claves"
    FOOTBALL_RATTLE = "football rattle"
    GUIRO = "guiro"
    LOG_DRUM = "log drum"
    MARACA = "maraca"
    MARACAS = "maracas"
    QUIJADA = "quijada"
    RAINSTICK = "rainstick"
    RATCHET = "ratchet"
    RECO_RECO = "reco-reco"
    SANDPAPER_BLOCKS = "sandpaper blocks"
    SLIT_DRUM = "slit drum"
    TEMPLE_BLOCK = "temple block"
    VIBRASLAP = "vibraslap"
    WHIP = "whip"
    WOOD_BLOCK = "wood block"


class YesNo(Enum):
    """The yes-no type is used for boolean-like attributes.

    We cannot use W3C XML Schema booleans due to their restrictions on
    expression of boolean values.
    """

    YES = "yes"
    NO = "no"
