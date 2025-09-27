import dataclasses
import itertools

import more_itertools
from svg import Line, Polyline, Rect, Style, Text

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
    polyline_elements: list[Polyline] = dataclasses.field(default_factory=list)
    rect_elements: list[Rect] = dataclasses.field(default_factory=list)
    text_elements: list[Text] = dataclasses.field(default_factory=list)
    pitch_points_buf: list[Point] = dataclasses.field(default_factory=list)
    style: str = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        self.style = Style(
            text=f"""\
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
        )

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
                        x1=x,
                        y1=0,
                        x2=x,
                        y2=self.coordinate_helper.size["height"],
                        class_=["line"],
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
                        x1=x,
                        y1=0,
                        x2=x,
                        y2=self.coordinate_helper.size["height"],
                        class_=["line"],
                    )
                    self.line_elements.append(line_element)
        for key in range(
            self.coordinate_helper.key_range_start,
            self.coordinate_helper.key_range_end + 1,
        ):
            y = (self.coordinate_helper.key_range_end - key) * self.options.note_height
            line_element = Line(
                x1=0,
                y1=y,
                x2=self.coordinate_helper.size["width"],
                y2=y,
                class_=["line"],
            )
            self.line_elements.append(line_element)

    def draw_text(
        self,
        position: TextPositionOption,
        text: str | None,
        parameters: NotePositionParameters,
        is_phoneme: bool,
    ) -> None:
        if not text:
            return
        elif position == TextPositionOption.UPPER:
            insert_pos = parameters.upper_text
        elif position == TextPositionOption.LOWER:
            insert_pos = parameters.lower_text
        elif position == TextPositionOption.INNER:
            insert_pos = parameters.inner_text
        else:
            return
        text_element = Text(
            text=text,
            font_size=self.coordinate_helper.font_size,
            x=insert_pos[0],
            y=insert_pos[1],
        )
        class_name = "inner" if position == TextPositionOption.INNER else "side"
        if is_phoneme:
            class_name += " pinyin"
        text_element.class_ = class_name
        self.text_elements.append(text_element)

    def draw_note(self, note: Note) -> None:
        parameters = self.coordinate_helper.get_note_position_parameters(note)
        rect_element = Rect(
            x=parameters.point_1[0],
            y=parameters.point_1[1],
            width=parameters.point_2[0] - parameters.point_1[0],
            height=parameters.point_2[1] - parameters.point_1[1],
            rx=self.options.note_round,
            ry=self.options.note_round,
            class_=["note"],
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
                polyline_element = Polyline(
                    points=list(
                        itertools.chain.from_iterable(
                            self.coordinate_helper.get_pitch_point(p) for p in self.pitch_points_buf
                        )
                    ),
                    class_=["pitch"],
                )
                self.polyline_elements.append(polyline_element)
                self.pitch_points_buf.clear()
        else:
            self.pitch_points_buf.append(point)
