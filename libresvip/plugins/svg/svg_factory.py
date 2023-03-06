import dataclasses
from typing import List

import more_itertools
from svgwrite.shapes import Line, Polyline, Rect
from svgwrite.text import Text

from libresvip.core.constants import TICKS_IN_BEAT
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import Note, TimeSignature
from libresvip.model.point import Point

from .coordinate_helper import CoordinateHelper
from .model import NotePositionParameters
from .options import OutputOptions, TextPositionOption


@dataclasses.dataclass
class SvgFactory:
    coordinate_helper: CoordinateHelper
    time_synchronizer: TimeSynchronizer
    options: OutputOptions
    line_elements: List[Line] = dataclasses.field(default_factory=list)
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
}}
.line {{
    fill: none;
    stroke: {self.options.grid_color.as_hex()};
    stroke-width: {self.options.grid_stroke_width}px;
}}"""

    def draw_grid(self, time_signature_list: List[TimeSignature]) -> None:
        prev_pos = 0
        pos = 0
        beat_start = self.coordinate_helper.position_range_start
        for previous_time_signature, time_signature in more_itertools.pairwise(
            time_signature_list
        ):
            beat_length = (
                time_signature.bar_index - previous_time_signature.bar_index
            ) * previous_time_signature.numerator
            for beat_offset in range(beat_length):
                pos = prev_pos + beat_offset * TICKS_IN_BEAT
                if pos >= beat_start:
                    x = int(
                        (pos - self.coordinate_helper.position_range_start)
                        * self.options.pixel_per_beat
                        / TICKS_IN_BEAT
                    )
                    line_element = Line(
                        start=(x, 0),
                        end=(x, self.coordinate_helper.size[1]),
                    )
                    line_element.attribs["class"] = "line"
                    self.line_elements.append(line_element)
            prev_pos += beat_length * TICKS_IN_BEAT
        if len(time_signature_list):
            pos = prev_pos
            while pos <= self.coordinate_helper.position_range_end:
                pos += TICKS_IN_BEAT
                if pos >= beat_start:
                    x = int(
                        (pos - beat_start) * self.options.pixel_per_beat / TICKS_IN_BEAT
                    )
                    line_element = Line(
                        start=(x, 0),
                        end=(x, self.coordinate_helper.size[1]),
                    )
                    line_element.attribs["class"] = "line"
                    self.line_elements.append(line_element)
        for key in range(
            self.coordinate_helper.key_range_start,
            self.coordinate_helper.key_range_end + 1,
        ):
            y = (self.coordinate_helper.key_range_end - key) * self.options.note_height
            line_element = Line(
                start=(0, y),
                end=(self.coordinate_helper.size[0], y),
            )
            line_element.attribs["class"] = "line"
            self.line_elements.append(line_element)

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
