import dataclasses
import itertools
from typing import Optional

import more_itertools
from drawsvg import Line, Lines, Rectangle, Text

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
    line_elements: list[Line] = dataclasses.field(default_factory=list)
    polyline_elements: list[Lines] = dataclasses.field(default_factory=list)
    rect_elements: list[Rectangle] = dataclasses.field(default_factory=list)
    text_elements: list[Text] = dataclasses.field(default_factory=list)
    pitch_points_buf: list[Point] = dataclasses.field(default_factory=list)
    style: str = dataclasses.field(init=False)

    def __post_init__(self) -> None:
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

    def draw_grid(self, time_signature_list: list[TimeSignature]) -> None:
        prev_pos = 0
        pos = 0
        beat_start = self.coordinate_helper.position_range_start
        for previous_time_signature, time_signature in more_itertools.pairwise(time_signature_list):
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
                        sx=x,
                        sy=0,
                        ex=x,
                        ey=self.coordinate_helper.size[1],
                        class_="line",
                    )
                    self.line_elements.append(line_element)
            prev_pos += beat_length * TICKS_IN_BEAT
        if len(time_signature_list):
            pos = prev_pos
            while pos <= self.coordinate_helper.position_range_end:
                pos += TICKS_IN_BEAT
                if pos >= beat_start:
                    x = int((pos - beat_start) * self.options.pixel_per_beat / TICKS_IN_BEAT)
                    line_element = Line(
                        sx=x,
                        sy=0,
                        ex=x,
                        ey=self.coordinate_helper.size[1],
                        class_="line",
                    )
                    self.line_elements.append(line_element)
        for key in range(
            self.coordinate_helper.key_range_start,
            self.coordinate_helper.key_range_end + 1,
        ):
            y = (self.coordinate_helper.key_range_end - key) * self.options.note_height
            line_element = Line(
                sx=0,
                sy=y,
                ex=self.coordinate_helper.size[0],
                ey=y,
                class_="line",
            )
            self.line_elements.append(line_element)

    def draw_text(
        self,
        position: TextPositionOption,
        text: Optional[str],
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
        text_element = Text(
            text,
            self.coordinate_helper.font_size,
            x=insert_pos[0],
            y=insert_pos[1],
        )
        class_name = "inner" if position == TextPositionOption.INNER else "side"
        if is_phoneme:
            class_name += " pinyin"
        text_element.args["class"] = class_name
        self.text_elements.append(text_element)

    def draw_note(self, note: Note) -> None:
        parameters = self.coordinate_helper.get_note_position_parameters(note)
        rect_element = Rectangle(
            x=parameters.point_1[0],
            y=parameters.point_1[1],
            width=parameters.point_2[0] - parameters.point_1[0],
            height=parameters.point_2[1] - parameters.point_1[1],
            rx=self.options.note_round,
            ry=self.options.note_round,
            class_="note",
        )
        self.rect_elements.append(rect_element)
        self.draw_text(self.options.lyric_position, note.lyric, parameters, False)
        self.draw_text(
            self.options.pronounciation_position,
            note.pronunciation,
            parameters,
            True,
        )

    def draw_pitch(self, point: Point) -> None:
        if point.y == -100:
            if len(self.pitch_points_buf):
                start_point = self.coordinate_helper.get_pitch_point(self.pitch_points_buf[0])
                polyline_element = Lines(
                    start_point[0],
                    start_point[1],
                    *itertools.chain.from_iterable(
                        self.coordinate_helper.get_pitch_point(p) for p in self.pitch_points_buf[1:]
                    ),
                    class_="pitch",
                )
                self.polyline_elements.append(polyline_element)
                self.pitch_points_buf.clear()
        else:
            self.pitch_points_buf.append(point)
