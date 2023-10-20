from typing import Literal, NamedTuple, Optional, Union

from pydantic import Field
from textx import metamodel_from_str

from libresvip.model.base import BaseModel

grammar = r"""
UTAUProject:
    (
        '[#VERSION]'
        LineBreak 'UST Version' '='? ust_version=FLOAT
        (LineBreak 'Charset=' charset=/[^\r\n]*/)?
    )?
    LineBreak? '[#SETTING]'
    (LineBreak 'UstVersion=' ust_version=FLOAT)?
    (
        (LineBreak 'Tempo=' tempo=/[^\r\n]*/) |
        (LineBreak 'TimeSignatures=' time_signatures*=UTAUTimeSignature[','] ','?) |
        (LineBreak 'Tracks=' track_count=INT) |
        (LineBreak 'Project' 'Name'? '=' project_name=/[^\r\n]*/) |
        (LineBreak 'VoiceDir=' voice_dir=/[^\r\n]*/) |
        (LineBreak 'OutFile=' out_file=/[^\r\n]*/) |
        (LineBreak 'CacheDir=' cache_dir=/[^\r\n]*/) |
        (LineBreak 'Tool1=' tool1=/[^\r\n]*/) |
        (LineBreak 'Tool2=' tool2=/[^\r\n]*/) |
        (LineBreak 'Mode2=' pitch_mode2=BOOL) |
        (LineBreak 'Autoren=' autoren=BOOL) |
        (LineBreak 'MapFirst=' map_first=BOOL) |
        (LineBreak 'Flags=' flags=/[^\r\n]*/)
    )*
    (track*=UTAUTrack) LineBreak*
;
UTAUTimeSignature:
    '(' numerator=INT '/' denominator=INT '/' bar_index=INT ')'
;
LineBreak: '\r'? '\n';
UTAUEnvelope:
    (p1=FLOAT ',' p2=FLOAT ',' p3=FLOAT ',' v1=FLOAT ',' v2=FLOAT ',' v3=FLOAT ',' v4=FLOAT) (
        (',,' p4=FLOAT) |
        (',%,' p4=FLOAT (',' p5=FLOAT (',' v5=FLOAT)?)?) |
        (',' other_points+=FLOAT[','])
    )?
;
UTAUPitchBendMode: /[srj]/ | '';
UTAUOptionalFloat: FLOAT | '';
UTAUPitchBendType: '5' | 'OldData';
UTAUTrack:
    notes+=UTAUNote
    (LineBreak '[#TRACKEND]')?
;
UTAUNoteType: /(\d{4}|PREV|NEXT|INSERT|DELETE)/;
UTAUNoteHead: '[#' UTAUNoteType ']';
UTAUNote:
    LineBreak '[#' note_type=UTAUNoteType ']'
    (
        (LineBreak 'Length' '=' length=FLOAT) |
        (LineBreak 'Duration' '=' duration=FLOAT) |
        (LineBreak 'Lyric' '=' lyric=/[^\r\n]*/) |
        (LineBreak 'NoteNum' '=' note_num=INT) |
        (LineBreak 'Delta' '=' delta=INT) |
        (LineBreak 'PreUtterance' '=' pre_utterance=/[^\r\n]*/) |
        (LineBreak 'VoiceOverlap' '=' voice_overlap=FLOAT) |
        (LineBreak 'Intensity' '=' intensity=FLOAT) |
        (LineBreak /(Modulation|Moduration)/ '=' modulation=FLOAT) |
        (LineBreak 'StartPoint' '=' start_point=FLOAT) |
        (LineBreak 'Envelope' '=' envelope=UTAUEnvelope) |
        (LineBreak 'Tempo' '=' tempo=/[^\r\n]*/) |
        (LineBreak 'Velocity' '=' velocity=FLOAT) |
        (LineBreak 'Label' '=' label=/[^\r\n]*/) |
        (LineBreak 'Flags' '=' flags=/[^\r\n]*/) |
        (LineBreak 'PBType' '=' pitchbend_type=UTAUPitchBendType) |
        (LineBreak 'PBStart' '=' pitchbend_start=FLOAT) |
        (LineBreak /(Piches|Pitches|PitchBend)/ '=' pitch_bend_points*=INT[',']) |
        (LineBreak 'PBS' '=' pbs+=FLOAT[/;|,/]) |
        (LineBreak 'PBW' '=' pbw*=UTAUOptionalFloat[',']) |
        (LineBreak 'PBY' '=' pby*=UTAUOptionalFloat[',']) |
        (LineBreak 'VBR' '=' vbr*=UTAUOptionalFloat[',']) |
        (LineBreak 'PBM' '=' pbm*=UTAUPitchBendMode[',']) |
        (LineBreak 'stptrim' '=' stp_trim=FLOAT) |
        (LineBreak 'layer' '=' layer=INT) |
        (LineBreak '@preuttr' '=' at_preutterance=FLOAT) |
        (LineBreak '@overlap' '=' at_overlap=FLOAT) |
        (LineBreak '@stpoint' '=' at_start_point=FLOAT) |
        (LineBreak '@filename' '=' sample_filename=/[^\r\n]*/) |
        (LineBreak '@alias' '=' alias=/[^\r\n]*/) |
        (LineBreak '@cache' '=' cache_location=/[^\r\n]*/) |
        (LineBreak key=/\$?[^=\r\n]+/ '=' value=/[^\r\n]*/) |
        (LineBreak !UTAUNoteHead /[^=\r\n]*/)
    )*
;
"""

UTAUPitchBendMode = Literal["s", "r", "j", ""]

UTAUPitchBendType = Literal["OldData", "5"]

UTAUOptionalFloat = Union[float, Literal[""]]


class UTAUVibrato(NamedTuple):
    length: float
    period: float
    depth: Optional[float]
    fade_in: Optional[float]
    fade_out: Optional[float]
    phase_shift: Optional[float]
    shift: Optional[float]


class UTAUEnvelope(BaseModel):
    p1: float
    p2: float
    p3: float
    v1: float
    v2: float
    v3: float
    v4: float
    p4: Optional[float] = None
    p5: Optional[float] = None
    v5: Optional[float] = None
    other_points: Optional[list[float]] = None


class UTAUNote(BaseModel):
    note_type: str
    length: list[int] = Field(default_factory=list)
    duration: list[int] = Field(default_factory=list)
    lyric: list[str] = Field(default_factory=list)
    note_num: list[int] = Field(default_factory=list)
    delta: list[int] = Field(default_factory=list)
    key: list[str] = Field(default_factory=list)
    value: list[str] = Field(default_factory=list)
    pre_utterance: list[str] = Field(default_factory=list)
    voice_overlap: list[float] = Field(default_factory=list)
    intensity: list[float] = Field(default_factory=list)
    modulation: list[float] = Field(default_factory=list)
    start_point: list[float] = Field(default_factory=list)
    envelope: list[UTAUEnvelope] = Field(default_factory=list)
    tempo: list[str] = Field(default_factory=list)
    velocity: list[float] = Field(default_factory=list)
    label: list[str] = Field(default_factory=list)
    flags: list[str] = Field(default_factory=list)
    pitchbend_type: list[UTAUPitchBendType] = Field(default_factory=list)
    pitchbend_start: list[float] = Field(default_factory=list)
    pitch_bend_points: list[int] = Field(default_factory=list)
    pbs: list[float] = Field(default_factory=list)
    pbw: list[UTAUOptionalFloat] = Field(default_factory=list)
    pby: list[UTAUOptionalFloat] = Field(default_factory=list)
    vbr: list[UTAUOptionalFloat] = Field(default_factory=list)
    pbm: list[UTAUPitchBendMode] = Field(default_factory=list)
    stp_trim: list[float] = Field(default_factory=list)
    layer: list[int] = Field(default_factory=list)
    at_preutterance: list[float] = Field(default_factory=list)
    at_overlap: list[float] = Field(default_factory=list)
    at_start_point: list[float] = Field(default_factory=list)
    sample_filename: list[str] = Field(default_factory=list)
    alias: list[str] = Field(default_factory=list)
    cache_location: list[str] = Field(default_factory=list)


class UTAUTrack(BaseModel):
    notes: list[UTAUNote] = Field(default_factory=list)


class UTAUTimeSignature(BaseModel):
    numerator: int
    denominator: int
    bar_index: int


class UTAUProject(BaseModel):
    ust_version: list[float] = Field(default_factory=list)
    charset: Optional[str] = None
    tempo: list[str] = Field(default_factory=list)
    time_signatures: list[UTAUTimeSignature] = Field(default_factory=list)
    project_name: list[str] = Field(default_factory=list)
    voice_dir: list[str] = Field(default_factory=list)
    out_file: list[str] = Field(default_factory=list)
    cache_dir: list[str] = Field(default_factory=list)
    tool1: list[str] = Field(default_factory=list)
    tool2: list[str] = Field(default_factory=list)
    autoren: list[bool] = Field(default_factory=list)
    map_first: list[bool] = Field(default_factory=list)
    flags: list[str] = Field(default_factory=list)
    track_count: list[int] = Field(default_factory=list)
    pitch_mode2: list[bool] = Field(default_factory=list)
    track: list[UTAUTrack] = Field(default_factory=list)


USTModel = metamodel_from_str(
    grammar,
    skipws=False,
    classes=[
        UTAUProject,
        UTAUTrack,
        UTAUNote,
        UTAUEnvelope,
        UTAUTimeSignature,
    ],
)
