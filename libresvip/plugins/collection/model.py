from textx import metamodel_from_str

grammar = """
PraatCollectionFile:
    "File type =" file_type= '"ooTextFile"'
    "Object class =" object_class= '"Collection"'
    "size =" size=INT
    "item []:" items*=PraatRootItem
;

PraatString:
    parts*=STRING
;

PraatRootItem:
    TextGrid | Pitch | IntensityOrHarmonicity | Formant | PointProcess | PitchOrIntensityTier
;

TextGrid:
    "item [" index=INT "]" ":"
    "class =" class= '"TextGrid"'
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
    "item [" index=INT "]" ":"
    "class =" class= '"IntervalTier"'
    "name =" name=PraatString
    "xmin =" xmin=NUMBER
    "xmax =" xmax=NUMBER
    "intervals:"
    "size =" size=INT
    intervals*=Interval
;

TextTier:
    "item [" index=INT "]" ":"
    "class =" class= '"TextTier"'
    "name =" name=PraatString
    "xmin =" xmin=NUMBER
    "xmax =" xmax=NUMBER
    "points:"
    "size =" size=INT
    points*=TextPoint
;

TextPoint:
    "points [" index=INT "]" ":"
    "number =" number=FLOAT
    "mark =" mark=PraatString
;

Interval:
    "intervals [" index=INT "]" ":"
    "xmin =" xmin=FLOAT
    "xmax =" xmax=FLOAT
    "text =" text=PraatString
;

Pitch:
    "item [" index=INT "]" ":"
    "class =" class= '"Pitch 1"'
    "name =" name=PraatString
    "xmin =" xmin=NUMBER
    "xmax =" xmax=NUMBER
    "nx =" nx=INT
    "dx =" dx=FLOAT
    "x1 =" x1=FLOAT
    "ceiling =" ceiling=INT
    "maxnCandidates =" maxnCandidates=INT
    "frames []:"
    frames*=Frame
;

IntensityOrHarmonicity:
    "item [" index=INT "]" ":"
    "class =" class=/"Intensity 2"|"Harmonicity 2"/
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
    z?=Z
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
    "z [" y=INT "] [" x=INT "] =" value=FLOAT
;

PointProcess:
    "item [" index=INT "]" ":"
    "class =" class= '"PointProcess 1"'
    "name =" name=PraatString
    "xmin =" xmin=NUMBER
    "xmax =" xmax=NUMBER
    "nt =" nt=INT
    "t []:" t*=T
;

T:
    "t [" index=INT "] =" value=FLOAT
;

Formant:
    "item [" index=INT "]" ":"
    "class =" class= '"Formant 2"'
    "name =" name=PraatString
    "xmin =" xmin=NUMBER
    "xmax =" xmax=NUMBER
    "nx =" nx=INT
    "dx =" dx=FLOAT
    "x1 =" x1=FLOAT
    "maxnFormants =" maxnFormants=INT
    "frames []:"
    frames*=Frame
;

PitchOrIntensityTier:
    "item [" index=INT "]" ":"
    "class =" class=/"PitchTier"|"IntensityTier"/
    "xmin =" xmin=NUMBER
    "xmax =" xmax=NUMBER
    "points :"
    "size =" size=INT
    points*=Point
;

Point:
    "points [" index=INT "]" ":"
    "number =" number=FLOAT
    "value =" value=FLOAT
;

Frame:
    "frames [" index=INT "]" ":"
    "intensity =" intensity=FLOAT
    candidates?=Candidates
    formants?=Formants
;

Candidates:
    "nCandidates =" nCandidates=INT
    "candidates []:"
    candidates*=CandidateElement
;

CandidateElement:
    "candidates [" index=INT "]" ":"
    "frequency =" frequency=FLOAT
    "strength =" strength=FLOAT
;

Formants:
    "nFormants =" nFormants=INT
    "formants []:"
    formants*=FormantElement
;

FormantElement:
    "frequency =" frequency=FLOAT
    "bandwidth =" bandwidth=FLOAT
;
"""

PraatCollectionModel = metamodel_from_str(grammar)
