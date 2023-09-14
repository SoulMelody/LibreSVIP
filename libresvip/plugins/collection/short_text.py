from textx import metamodel_from_str

grammar = """
PraatCollectionFile:
    'File type = "ooTextFile"'
    'Object class = "Collection"'
    size=INT
    items*=PraatRootItem
;

PraatString:
    parts*=STRING
;

PraatRootItem:
    TextGrid | Pitch | ThreeDimensional | Formant | PointProcess | PitchOrIntensityTier
;

TextGrid:
    item_type= '"TextGrid"'
    name=PraatString
    xmin=NUMBER
    xmax=NUMBER
    has_tiers?="<exists>"
    size=INT
    tiers*=IntervalOrTextTier
;

IntervalOrTextTier:
    IntervalTier | TextTier
;

IntervalTier:
    item_type= '"IntervalTier"'
    name=PraatString
    xmin=NUMBER
    xmax=NUMBER
    size=INT
    intervals*=Interval
;

TextTier:
    item_type= '"TextTier"'
    name=PraatString
    xmin=NUMBER
    xmax=NUMBER
    size=INT
    points*=TextPoint
;

TextPoint:
    number=FLOAT
    mark=PraatString
;

Interval:
    xmin=FLOAT
    xmax=FLOAT
    text=PraatString
;

Pitch:
    item_type= '"Pitch 1"'
    name=PraatString
    xmin=NUMBER
    xmax=NUMBER
    nx=INT
    dx=FLOAT
    x1=FLOAT
    ceiling=INT
    size=INT
    frames*=Frame
;

ThreeDimensional:
    item_type=/"Intensity 2"|"Harmonicity 2"|"Sound 2"/
    name=PraatString
    xmin=NUMBER
    xmax=NUMBER
    nx=INT
    dx=FLOAT
    x1=FLOAT
    ymin=FLOAT
    ymax=FLOAT
    ny=INT
    dy=FLOAT
    y1=FLOAT
    z=Z?
;

Z:
    y*=Y
;

Y:
    y=INT
    x*=X
;

X:
    value=FLOAT
;

PointProcess:
    item_type= '"PointProcess 1"'
    name=PraatString
    xmin=NUMBER
    xmax=NUMBER
    nt=INT
    t*=T
;

T:
    value=FLOAT
;

Formant:
    item_type= '"Formant 2"'
    name=PraatString
    xmin=NUMBER
    xmax=NUMBER
    nx=INT
    dx=FLOAT
    x1=FLOAT
    size=INT
    frames*=Frame
;

PitchOrIntensityTier:
    item_type=/"PitchTier"|"IntensityTier"/
    xmin=NUMBER
    xmax=NUMBER
    size=INT
    points*=Point
;

Point:
    number=FLOAT
    value=FLOAT
;

Frame:
    intensity=FLOAT
    candidates=Candidates?
    formants=Formants?
;

Candidates:
    size=INT
    candidates*=CandidateElement
;

CandidateElement:
    frequency=FLOAT
    strength=FLOAT
;

Formants:
    size=INT
    formants*=FormantElement
;

FormantElement:
    frequency=FLOAT
    bandwidth=FLOAT
;
"""

PraatShortTextModel = metamodel_from_str(grammar)
