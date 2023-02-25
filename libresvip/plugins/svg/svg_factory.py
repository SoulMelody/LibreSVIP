import dataclasses
from typing import List

from svgwrite.shapes import Polyline, Rect
from svgwrite.text import Text

from libresvip.model.base import Note
from libresvip.model.point import Point

from .coordinate_helper import CoordinateHelper
from .model import NotePositionParameters
from .options import OutputOptions, TextPositionOption


@dataclasses.dataclass
class SvgFactory:
    coordinate_helper: CoordinateHelper
    options: OutputOptions
    polyline_elements: List[Polyline] = dataclasses.field(default_factory=list)
    rect_elements: List[Rect] = dataclasses.field(default_factory=list)
    text_elements: List[Text] = dataclasses.field(default_factory=list)
    style: str = dataclasses.field(init=False)

    def __post_init__(self):
        self.style = f"""\
.note {{
    fill: {self.options.note_fill_color.as_hex()};
    stroke: {self.options.note_stroke_color.as_hex()};
    stroke-width: {self.options.note_stroke_width}px;
}}
.pitch {{
    fill: none;
    stroke: {self.options.pitch_stroke_color.as_hex()};
    stroke-width: {self.options.pitch_stroke_width}px;
}}
text {{
    font-size: {self.coordinate_helper.font_size}px;
    text-anchor: {self.coordinate_helper.text_anchor};
}}
.inner {{
    fill: {self.options.inner_text_color.as_hex()};
}}
.side {{
    fill: {self.options.side_text_color.as_hex()};
    font-size: {max(self.coordinate_helper.font_size - 4, 10)}px;
}}"""

    def draw_text(
        self,
        position: TextPositionOption,
        text: str,
        parameters: NotePositionParameters,
        is_phoneme: bool,
    ) -> None:
        if position == TextPositionOption.NONE or not text:
            return
        elif position == TextPositionOption.UPPER:
            insert_pos = parameters.upper_text
        elif position == TextPositionOption.LOWER:
            insert_pos = parameters.lower_text
        elif position == TextPositionOption.INNER:
            insert_pos = parameters.inner_text
        text_element = Text(text, insert_pos)
        class_name = "inner" if position == TextPositionOption.INNER else "side"
        if is_phoneme:
            class_name += " pinyin"
        text_element.attribs["class"] = class_name
        self.text_elements.append(text_element)

    def draw_note(self, note: Note):
        parameters = self.coordinate_helper.get_note_position_parameters(note)
        rect_element = Rect(
            insert=parameters.point_1,
            size=(
                parameters.point_2[0] - parameters.point_1[0],
                parameters.point_2[1] - parameters.point_1[1],
            ),
            rx=self.options.note_round,
            ry=self.options.note_round,
        )
        rect_element.attribs["class"] = "note"
        self.rect_elements.append(rect_element)
        self.draw_text(self.options.lyric_position, note.lyric, parameters, False)
        self.draw_text(
            self.options.pronounciation_position, note.pronunciation, parameters, True
        )

    def draw_pitch(self, point: Point):
        if point.y == -100:
            polyline_element = Polyline()
            polyline_element.attribs["class"] = "pitch"
            self.polyline_elements.append(polyline_element)
        else:
            if not len(self.polyline_elements):
                polyline_element = Polyline()
                polyline_element.attribs["class"] = "pitch"
                self.polyline_elements.append(polyline_element)
            self.polyline_elements[-1].points.append(
                self.coordinate_helper.get_pitch_point(point)
            )
