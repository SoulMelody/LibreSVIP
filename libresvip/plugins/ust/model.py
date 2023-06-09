from typing import Optional

from pydantic import Field
from textx import metamodel_from_str

from libresvip.model.base import BaseModel

grammar = r"""
UTAUProject:
    (version_info=UTAUVersion)?
    '[#SETTING]' LineBreak
    'Tempo=' tempo=/[^\r\n]*/ LineBreak
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
UTAUEnvelope:
    (p1=FLOAT ',' p2=FLOAT ',' p3=FLOAT ',' v1=FLOAT ',' v2=FLOAT ',' v3=FLOAT ',' v4=FLOAT) (
        (',,' p4=FLOAT) |
        (',%,' p4=FLOAT (',' p5=FLOAT (',' v5=FLOAT)?)?)
    )?
;
UTAUPBM: text=/[srj]?/ ','?;
UTAUPitchBendType: '5' | 'OldData';
UTAUTrack:
    notes+=UTAUNote
    '[#TRACKEND]'? LineBreak?
;
UTAUNoteType: /(\d+|PREV|NEXT|INSERT|DELETE)/;
UTAUNote:
    '[#' note_type=UTAUNoteType ']' LineBreak
    (
        ('Length' '=' length=FLOAT LineBreak)
        ('Lyric' '=' lyric=/[^\r\n]*/ LineBreak)
        ('NoteNum' '=' note_num=INT LineBreak)
    )#
    (
        ('PreUtterance' '=' pre_utterance=/[^\r\n]*/ LineBreak) |
        ('VoiceOverlap' '=' voice_overlap=FLOAT LineBreak) |
        ('Intensity' '=' intensity=FLOAT LineBreak) |
        (/(Modulation|Moduration)/ '=' modulation=FLOAT LineBreak) |
        ('StartPoint' '=' start_point=FLOAT LineBreak) |
        ('Envelope' '=' envelope=UTAUEnvelope LineBreak) |
        ('Tempo' '=' tempo=/[^\r\n]*/ LineBreak) |
        ('Velocity' '=' velocity=FLOAT LineBreak) |
        ('Label' '=' label=/[^\r\n]*/ LineBreak) |
        ('Flags' '=' flags=/[^\r\n]*/ LineBreak) |
        ('PBType' '=' pitchbend_type=UTAUPitchBendType LineBreak) |
        ('PBStart' '=' pitchbend_start=FLOAT LineBreak) |
        (/(Piches|Pitches|PitchBend)/ '=' pitch_bend_points*=INT[','] LineBreak) |
        ('PBS' '=' pbs_1=FLOAT (';' pbs_2=FLOAT)? LineBreak) |
        ('PBW' '=' ','* pbw*=FLOAT[/,+/] ','* LineBreak) |
        ('PBY' '=' ','* pby*=FLOAT[/,+/] ','* LineBreak) |
        ('PBM' '=' pbm*=UTAUPBM LineBreak) |
        ('VBR' '=' ','* vbr*=FLOAT[/,+/] ','* LineBreak) |
        (key=/\$[^=]+/ '=' value=/[^\r\n]*/ LineBreak)
    )*
;
"""


class UTAUPBM(BaseModel):
    text: str

class UTAUEnvelope(BaseModel):
    p1: int
    p2: int
    p3: int
    v1: int
    v2: int
    v3: int
    v4: int
    p4: Optional[int] = None
    p5: Optional[int] = None
    v5: Optional[int] = None


class UTAUNote(BaseModel):
    note_type: str
    length: int
    lyric: str
    note_num: int
    # Optional keys
    key: Optional[list[str]]
    value: Optional[list[str]]
    pre_utterance: Optional[list[str]]
    voice_overlap: Optional[list[float]]
    intensity: Optional[list[float]]
    modulation: Optional[list[float]]
    start_point: Optional[list[float]]
    envelope: Optional[list[UTAUEnvelope]]
    tempo: Optional[list[str]]
    velocity: Optional[list[float]]
    label: Optional[list[str]]
    flags: Optional[list[str]]
    pitchbend_type: Optional[list[str]]
    pitchbend_start: Optional[list[float]]
    pitch_bend_points: Optional[list[int]]
    pbs_1: Optional[list[float]]
    pbs_2: Optional[list[float]]
    pbw: Optional[list[float]]
    pby: Optional[list[float]]
    pbm: Optional[list[UTAUPBM]]
    vbr: Optional[list[float]]


class UTAUTrack(BaseModel):
    notes: list[UTAUNote] = Field(default_factory=list)


class UTAUVersion(BaseModel):
    ust_version: float
    charset: Optional[str]


class UTAUProject(BaseModel):
    version_info: Optional[UTAUVersion]
    tempo: str
    project_name: Optional[str]
    voice_dir: Optional[str]
    out_file: Optional[str]
    cache_dir: Optional[str]
    tool1: Optional[str]
    tool2: Optional[str]
    autoren: Optional[bool]
    map_first: Optional[bool]
    flags: Optional[str]
    track: Optional[UTAUTrack]
    track_count: Optional[int] = 1
    pitch_mode2: Optional[bool] = False


USTModel = metamodel_from_str(
    grammar,
    skipws=False,
    classes=[
        UTAUProject,
        UTAUVersion,
        UTAUTrack,
        UTAUNote,
        UTAUEnvelope,
        UTAUPBM,
    ],
)
