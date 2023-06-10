from typing import List

from pydantic import Field
from textx import metamodel_from_str

from libresvip.model.base import BaseModel

grammar = """
NNProject:
    info_line=NNInfoLine LineBreak
    note_count=INT LineBreak
    (notes+=NNNote LineBreak?)*
;
LineBreak: '\r'? '\n';
NNTimeSignature: numerator=INT ' ' denominator=INT;
NNInfoLine: tempo=FLOAT ' ' time_signature=NNTimeSignature ' ' bar_count=INT ' ' version=INT ' ' unknown=INT ' 0 0 0 0';
NNPoints: point_count=INT ',' points*=INT[','];
Word: /([\u4e00-\u9fff]|-|[a-z]+)/;
Pinyin: /[a-z-]+/;
NNNote: ' ' lyric=Word ' ' pronunciation=Pinyin ' ' start=INT ' ' duration=INT ' ' key=INT ' ' cle=INT ' ' vel=INT ' ' por=INT ' ' vibrato_length=INT ' ' vibrato_depth=INT ' ' vibrato_rate=INT ' ' dynamics=NNPoints ' ' pitch=NNPoints ' ' pitch_bend_sensitivity=INT;
"""


class NNPoints(BaseModel):
    point_count: int = 100
    points: List[int] = Field(default_factory=list)


class NNTimeSignature(BaseModel):
    numerator: int = 4
    denominator: int = 4


class NNInfoLine(BaseModel):
    tempo: float
    time_signature: NNTimeSignature
    bar_count: int = 0
    version: int = 19
    unknown: int = 0


class NNNote(BaseModel):
    lyric: str
    pronunciation: str
    start: int
    duration: int
    key: int
    cle: int
    vel: int
    por: int
    vibrato_length: int
    vibrato_depth: int
    vibrato_rate: int
    dynamics: NNPoints = Field(default_factory=NNPoints)
    pitch: NNPoints = Field(default_factory=NNPoints)
    pitch_bend_sensitivity: int = 0


class NNProject(BaseModel):
    info_line: NNInfoLine
    note_count: int
    notes: List[NNNote] = Field(default_factory=list)


NNModel = metamodel_from_str(
    grammar,
    skipws=False,
    classes=[NNProject, NNInfoLine, NNTimeSignature, NNNote, NNPoints],
)
