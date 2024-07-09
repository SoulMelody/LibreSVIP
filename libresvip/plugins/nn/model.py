from typing import Any

from parsimonious import Grammar, NodeVisitor
from parsimonious.nodes import Node
from pydantic import Field

from libresvip.model.base import BaseModel

nn_grammar = Grammar(
    r"""
    nn_project        =
        nn_info_line newline
        int newline
        (nn_note newline?)*
        nn_chord?
        nn_drum?

    nn_chord          =
        "#CHORD" newline
        int newline
        ('[' nn_legacy_points ']' newline)*

    nn_drum           =
        "#DRUM" newline
        '[' nn_legacy_points ']' newline

    newline           = ~"\r?\n"
    nn_time_signature = int " " int
    nn_info_line      = float ' ' nn_time_signature ' ' int ' ' int ' ' int ' 0 0 0 0'
    nn_points         = int (',' int)*
    nn_legacy_points  = int (', ' int)*
    nn_note           = ' ' word ' ' pinyin ' ' int ' ' int ' ' int ' ' int ' ' int ' ' int ' ' int ' ' int ' ' int ' ' nn_points ' ' nn_points ' ' int

    word              = ~"([\u4e00-\u9fff]|-|[a-z]+)"
    pinyin            = ~"[a-z-]+"
    float             = ~"[-+]?(\\d+(\\.\\d*)?|\\.\\d+)"
    int               = ~"[-+]?\\d+"
    """
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


class NNVisitor(NodeVisitor):
    def visit_nn_project(self, node: Node, visited_children: list[Any]) -> NNProject:
        info_line, _, note_count, _, note_pairs, _, _ = visited_children
        return NNProject(
            info_line=info_line,
            note_count=note_count,
            notes=[note_pair[0] for note_pair in note_pairs],
        )

    def visit_nn_info_line(self, node: Node, visited_children: list[Any]) -> NNInfoLine:
        tempo, time_signature, bar_count, version, unknown = visited_children[::2]
        return NNInfoLine(
            tempo=tempo,
            time_signature=time_signature,
            bar_count=bar_count,
            version=version,
            unknown=unknown,
        )

    def visit_nn_time_signature(self, node: Node, visited_children: list[Any]) -> NNTimeSignature:
        numerator, _, denominator = visited_children
        return NNTimeSignature(numerator=numerator, denominator=denominator)

    def visit_nn_note(self, node: Node, visited_children: list[Any]) -> NNNote:
        (
            lyric,
            pronunciation,
            start,
            duration,
            key,
            cle,
            vel,
            por,
            vibrato_length,
            vibrato_depth,
            vibrato_rate,
            dynamics,
            pitch,
            pitch_bend_sensitivity,
        ) = visited_children[1::2]
        return NNNote(
            lyric=lyric,
            pronunciation=pronunciation,
            start=start,
            duration=duration,
            key=key,
            cle=cle,
            vel=vel,
            por=por,
            vibrato_length=vibrato_length,
            vibrato_depth=vibrato_depth,
            vibrato_rate=vibrato_rate,
            dynamics=dynamics,
            pitch=pitch,
            pitch_bend_sensitivity=pitch_bend_sensitivity,
        )

    def visit_nn_points(self, node: Node, visited_children: list[Any]) -> NNPoints:
        point_count, point_node_root = visited_children
        points = [point_node[-1] for point_node in point_node_root]
        return NNPoints(point_count=point_count, points=points)

    def visit_word(self, node: Node, visited_children: list[Any]) -> str:
        return node.text

    def visit_pinyin(self, node: Node, visited_children: list[Any]) -> str:
        return node.text

    def visit_int(self, node: Node, visited_children: list[Any]) -> int:
        return int(node.text)

    def visit_float(self, node: Node, visited_children: list[Any]) -> float:
        return float(node.text)

    def generic_visit(self, node: Node, visited_children: list[Any]) -> Any:
        return visited_children or node


nn_visitor = NNVisitor()
