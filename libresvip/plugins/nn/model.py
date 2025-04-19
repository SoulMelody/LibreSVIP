import tatsu
from pydantic import Field
from tatsu.grammars import Grammar
from tatsu.objectmodel import Node
from tatsu.walkers import NodeWalker

from libresvip.model.base import BaseModel


def get_nn_grammar() -> Grammar:
    return tatsu.compile(
        """
        @@grammar::Nn
        @@whitespace :: None

        nn_project::nn_project
            =
            info_line:nn_info_line newline
            note_count:int newline
            notes:{nn_note [newline]}*
            [nn_chord] [nn_drum] ;

        nn_chord
            = "#CHORD" newline int newline {'[' nn_legacy_points ']' newline}* ;
        nn_drum
            = "#DRUM" newline '[' nn_legacy_points ']' newline ;
        nn_legacy_points  = int {', ' int}* ;

        nn_points::nn_points
            =
            point_count:int
            points:{',' int}* ;
        nn_note::nn_note
            =
            ' ' lyric:word
            ' ' pronunciation:pinyin
            ' ' start:int
            ' ' duration:int
            ' ' key:int
            ' ' cle:int
            ' ' vel:int
            ' ' por:int
            ' ' vibrato_length:int
            ' ' vibrato_depth:int
            ' ' vibrato_rate:int
            ' ' dynamics:nn_points
            ' ' pitch:nn_points
            ' ' pitch_bend_sensitivity:int ;
        nn_time_signature::nn_time_signature
            =
            numerator:int ' '
            denominator:int ;
        nn_info_line::nn_info_line
            =
            tempo:float ' '
            time_signature:nn_time_signature ' '
            bar_count:int ' '
            version:int ' '
            unknown:int ' 0 0 0 0' ;

        newline           = /\r?\n/ ;
        word              = ?"([\u4e00-\u9fff]|-|[a-z]+)" ;
        pinyin            = ?"[a-z-]+" ;
        float::float      = ?"[-+]?(?:\\d+(?:\\.\\d*)?|\\.\\d+)" ;
        int::int          = ?"[-+]?\\d+" ;
        """,
        asmodel=True,
    )


class NNPoints(BaseModel):
    point_count: int = 100
    points: list[int] = Field(default_factory=lambda: [50] * 100)


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
    cle: int = 0
    vel: int = 50
    por: int = 20
    vibrato_length: int = 0
    vibrato_depth: int = 0
    vibrato_rate: int = 0
    dynamics: NNPoints = Field(default_factory=NNPoints)
    pitch: NNPoints = Field(default_factory=NNPoints)
    pitch_bend_sensitivity: int = 12


class NNProject(BaseModel):
    info_line: NNInfoLine
    note_count: int = 0
    notes: list[NNNote] = Field(default_factory=list)


class NnWalker(NodeWalker):
    def walk_nn_points(self, node: Node) -> NNPoints:
        return NNPoints(point_count=node.point_count, points=[i[1] for i in node.points])

    def walk_nn_note(self, node: Node) -> NNNote:
        return NNNote(
            lyric=node.lyric,
            pronunciation=node.pronunciation,
            start=node.start,
            duration=node.duration,
            key=node.key,
            cle=node.cle,
            vel=node.vel,
            por=node.por,
            vibrato_length=node.vibrato_length,
            vibrato_depth=node.vibrato_depth,
            vibrato_rate=node.vibrato_rate,
            dynamics=self.walk(node.dynamics),
            pitch=self.walk(node.pitch),
            pitch_bend_sensitivity=node.pitch_bend_sensitivity,
        )

    def walk_nn_info_line(self, node: Node) -> NNInfoLine:
        return NNInfoLine(
            tempo=node.tempo,
            time_signature=self.walk(node.time_signature),
            bar_count=node.bar_count,
            version=node.version,
            unknown=node.unknown,
        )

    def walk_nn_time_signature(self, node: Node) -> NNTimeSignature:
        return NNTimeSignature(
            numerator=node.numerator,
            denominator=node.denominator,
        )

    def walk_nn_project(self, node: Node) -> NNProject:
        return NNProject(
            info_line=self.walk(node.info_line),
            note_count=node.note_count,
            notes=[n[0] for n in self.walk(node.notes)],
        )


nn_walker = NnWalker()
