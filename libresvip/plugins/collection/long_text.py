from textx import metamodel_from_str

grammar = """
PraatCollectionFile:
    'File type = "ooTextFile"'
    'Object class = "Collection"'
    "size =" size=INT
    "item []:" items*=PraatRootItem
;

PraatString:
    parts*=STRING
;

PraatRootItem:
    TextGrid | Pitch | ThreeDimensional | Formant | PointProcess | RootTier
;

TextGrid:
    "item [" INT "]" ":"
    "class =" item_type= '"TextGrid"'
    "name =" name=PraatString
    "xmin =" xmin=NUMBER
    "xmax =" xmax=NUMBER
    "tiers?" has_tiers?="<exists>"
    "size =" size=INT
    "item []:" tiers*=IntervalOrTextTier
;

IntervalOrTextTier:
    IntervalTier | TextTier
;

IntervalTier:
    "item [" INT "]" ":"
    "class =" item_type= '"IntervalTier"'
    "name =" name=PraatString
    "xmin =" xmin=NUMBER
    "xmax =" xmax=NUMBER
    "intervals:"
    "size =" size=INT
    intervals*=Interval
;

TextTier:
    "item [" INT "]" ":"
    "class =" item_type= '"TextTier"'
    "name =" name=PraatString
    "xmin =" xmin=NUMBER
    "xmax =" xmax=NUMBER
    "points:"
    "size =" size=INT
    points*=TextPoint
;

TextPoint:
    "points [" INT "]" ":"
    "number =" number=FLOAT
    "mark =" mark=PraatString
;

Interval:
    "intervals [" INT "]" ":"
    "xmin =" xmin=FLOAT
    "xmax =" xmax=FLOAT
    "text =" text=PraatString
;

Pitch:
    "item [" INT "]" ":"
    "class =" item_type= '"Pitch 1"'
    "name =" name=PraatString
    "xmin =" xmin=NUMBER
    "xmax =" xmax=NUMBER
    "nx =" nx=INT
    "dx =" dx=FLOAT
    "x1 =" x1=FLOAT
    "ceiling =" ceiling=INT
    "maxnCandidates =" size=INT
    "frames []:"
    frames*=Frame
;

ThreeDimensional:
    "item [" INT "]" ":"
    "class =" item_type=/"Intensity 2"|"Harmonicity 2"|"Sound 2"/
    "name =" name=PraatString
    "xmin =" xmin=NUMBER
    "xmax =" xmax=NUMBER
    "nx =" nx=INT
    "dx =" dx=FLOAT
    "x1 =" x1=FLOAT
    "ymin =" ymin=FLOAT
    "ymax =" ymax=FLOAT
    "ny =" ny=INT
    "dy =" dy=FLOAT
    "y1 =" y1=FLOAT
    z=Z?
;

Z:
    "z [] []:"
    y*=Y
;

Y:
    "z [" y=INT "]:"
    x*=X
;

X:
    "z [" INT "] [" INT "] =" value=FLOAT
;

PointProcess:
    "item [" INT "]" ":"
    "class =" item_type= '"PointProcess 1"'
    "name =" name=PraatString
    "xmin =" xmin=NUMBER
    "xmax =" xmax=NUMBER
    "nt =" nt=INT
    "t []:" t*=T
;

T:
    "t [" INT "] =" value=FLOAT
;

Formant:
    "item [" INT "]" ":"
    "class =" item_type= '"Formant 2"'
    "name =" name=PraatString
    "xmin =" xmin=NUMBER
    "xmax =" xmax=NUMBER
    "nx =" nx=INT
    "dx =" dx=FLOAT
    "x1 =" x1=FLOAT
    "maxnFormants =" size=INT
    "frames []:"
    frames*=Frame
;

RootTier:
    "item [" INT "]" ":"
    "class =" item_type=/"PitchTier"|"IntensityTier"|"DurationTier"/
    "xmin =" xmin=NUMBER
    "xmax =" xmax=NUMBER
    "points :"
    "size =" size=INT
    points*=Point
;

Point:
    "points [" INT "]" ":"
    "number =" number=FLOAT
    "value =" value=FLOAT
;

Frame:
    "frames [" INT "]" ":"
    "intensity =" intensity=FLOAT
    candidates=Candidates?
    formants=Formants?
;

Candidates:
    "nCandidates =" size=INT
    "candidates []:"
    candidates*=CandidateElement
;

CandidateElement:
    "candidates [" INT "]" ":"
    "frequency =" frequency=FLOAT
    "strength =" strength=FLOAT
;

Formants:
    "nFormants =" size=INT
    "formants []:"
    formants*=FormantElement
;

FormantElement:
    "frequency =" frequency=FLOAT
    "bandwidth =" bandwidth=FLOAT
;
"""

PraatLongTextModel = metamodel_from_str(grammar)
