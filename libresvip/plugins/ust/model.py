from typing import List, Optional

from pydantic import Field
from textx import metamodel_from_str

from libresvip.model.base import BaseModel

grammar = """
UTAUProject:
    (version_info=UTAUVersion)?
    '[#SETTING]' LineBreak
    'Tempo=' tempo=FLOAT LineBreak
    ('Tracks=' track_count=INT LineBreak)?
    ('Project' 'Name'? '=' project_name=/[^\r\n]*/ LineBreak)?
    ('VoiceDir=' voice_dir=/[^\r\n]*/ LineBreak)?
    ('OutFile=' out_file=/[^\r\n]*/ LineBreak)?
    ('CacheDir=' cache_dir=/[^\r\n]*/ LineBreak)?
    ('Tool1=' tool1=/[^\r\n]*/ LineBreak)?
    ('Tool2=' tool2=/[^\r\n]*/ LineBreak)?
    ('Mode2=' pitch_mode2=BOOL LineBreak)?
    ('Autoren=' autoren=BOOL LineBreak)?
    ('MapFirst=' map_first=BOOL LineBreak)?
    ('Flags=' flags=/[^\r\n]*/ LineBreak)?
    (track=UTAUTrack)?
;
LineBreak: '\r'? '\n';
UTAUVersion:
    '[#VERSION]' LineBreak
    'UST Version' ust_version=FLOAT LineBreak
    ('Charset=' charset=/[^\r\n]*/ LineBreak)?
;
UTAUEnvelopeBase:
    p1=INT ',' p2=INT ',' p3=INT ',' v1=INT ',' v2=INT ',' v3=INT ',' v4=INT
;
UTAUEnvelope:
    base=UTAUEnvelopeBase (
        (',,' p4=INT) |
        (',%,' p4=INT (',' p5=INT (',' v5=INT)?)?)
    )?
;
UTAUPBM: text=/[srj]?/ ','?;
UTAUPitchBendType: '5' | 'OldData';
UTAUOptionalAttr:
    (key='PreUtterance' '=' pre_utterance=/[^\r\n]*/ LineBreak) |
    (key='VoiceOverlap' '=' voice_overlap=FLOAT LineBreak) |
    (key='Intensity' '=' intensity=FLOAT LineBreak) |
    (key=/(Modulation|Moduration)/ '=' modulation=FLOAT LineBreak) |
    (key='StartPoint' '=' start_point=FLOAT LineBreak) |
    (key='Envelope' '=' envelope=UTAUEnvelope LineBreak) |
    (key='Tempo' '=' tempo=FLOAT LineBreak) |
    (key='Velocity' '=' velocity=FLOAT LineBreak) |
    (key='Label' '=' label=/[^\r\n]*/ LineBreak) |
    (key='Flags' '=' flags=/[^\r\n]*/ LineBreak) |
    (key='PBType' '=' pitchbend_type=UTAUPitchBendType LineBreak) |
    (key='PBStart' '=' pitchbend_start=FLOAT LineBreak) |
    (key=/(Piches|Pitches|PitchBend)/ '=' pitch_bend_points*=INT[','] LineBreak) |
    (key='PBS' '=' pbs_1=FLOAT (';' pbs_2=FLOAT)? LineBreak) |
    (key='PBW' '=' pbw*=FLOAT[','] ','? LineBreak) |
    (key='PBY' '=' pby*=FLOAT[','] ','? LineBreak) |
    (key='PBM' '=' pbm*=UTAUPBM LineBreak) |
    (key='VBR' '=' vbr*=FLOAT[','] ','? LineBreak) |
    (key=/\\$[^=]+/ '=' value=/[^\r\n]*/ LineBreak)
;
UTAUTrack:
    notes+=UTAUNote
    '[#TRACKEND]' LineBreak?
;
UTAUNoteType: /(\\d+|PREV|NEXT|INSERT|DELETE)/;
UTAUNote:
    '[#' note_type=UTAUNoteType ']' LineBreak
    'Length=' length=INT LineBreak
    'Lyric=' lyric=/[^\r\n]*/ LineBreak
    'NoteNum=' note_num=INT LineBreak
    optional_attrs*=UTAUOptionalAttr
;
"""


class UTAUPBM(BaseModel):
    text: str


class UTAUEnvelopeBase(BaseModel):
    p1: int
    p2: int
    p3: int
    v1: int
    v2: int
    v3: int
    v4: int


class UTAUEnvelope(BaseModel):
    base: UTAUEnvelopeBase
    p4: Optional[int] = None
    p5: Optional[int] = None
    v5: Optional[int] = None


class UTAUOptionalAttr(BaseModel):
    key: str
    value: Optional[str]
    pre_utterance: Optional[str]
    voice_overlap: Optional[float]
    intensity: Optional[float]
    modulation: Optional[float]
    start_point: Optional[float]
    envelope: Optional[UTAUEnvelope]
    tempo: Optional[float]
    velocity: Optional[float]
    label: Optional[str]
    flags: Optional[str]
    pitchbend_type: Optional[str]
    pitchbend_start: Optional[float]
    pitch_bend_points: Optional[List[int]]
    pbs_1: Optional[float]
    pbs_2: Optional[float]
    pbw: Optional[List[float]]
    pby: Optional[List[float]]
    pbm: Optional[List[UTAUPBM]]
    vbr: Optional[List[float]]


class UTAUNote(BaseModel):
    note_type: str
    length: int
    lyric: str
    note_num: int
    optional_attrs: List[UTAUOptionalAttr] = Field(default_factory=list)


class UTAUTrack(BaseModel):
    notes: List[UTAUNote] = Field(default_factory=list)


class UTAUVersion(BaseModel):
    ust_version: float
    charset: Optional[str]


class UTAUProject(BaseModel):
    version_info: Optional[UTAUVersion]
    tempo: float
    track_count: Optional[int]
    project_name: Optional[str]
    voice_dir: Optional[str]
    out_file: Optional[str]
    cache_dir: Optional[str]
    tool1: Optional[str]
    tool2: Optional[str]
    pitch_mode2: Optional[bool]
    autoren: Optional[bool]
    map_first: Optional[bool]
    flags: Optional[str]
    track: Optional[UTAUTrack]


UstModel = metamodel_from_str(
    grammar,
    skipws=False,
    classes=[
        UTAUProject,
        UTAUVersion,
        UTAUTrack,
        UTAUNote,
        UTAUOptionalAttr,
        UTAUEnvelope,
        UTAUEnvelopeBase,
        UTAUPBM,
    ],
)
