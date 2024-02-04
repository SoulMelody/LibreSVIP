import dataclasses
import math

from libresvip.core.constants import TICKS_IN_BEAT
from libresvip.model.base import Note, SingingTrack
from libresvip.model.point import Point

from .model import NotePositionParameters
from .options import OutputOptions, TextAlignOption

PADDING: int = 4


@dataclasses.dataclass
class CoordinateHelper:
    options: OutputOptions
    pitch_position_offset: int
    position_range_start: int = dataclasses.field(init=False)
    position_range_end: int = dataclasses.field(init=False)
    key_range_start: int = dataclasses.field(init=False)
    key_range_end: int = dataclasses.field(init=False)

    def calculate_range(self, track: SingingTrack) -> None:
        self.position_range_start = min(
            track.note_list[0].start_pos, track.edited_params.pitch.points[1].x
        )
        self.position_range_end = max(
            track.note_list[-1].end_pos, track.edited_params.pitch.points[-2].x
        )
        self.key_range_start = min(note.key_number for note in track.note_list)
        self.key_range_end = max(note.key_number for note in track.note_list)
        for point in track.edited_params.pitch.points.root[1:-1]:
            if point.y == -100:
                continue
            self.key_range_start = min(self.key_range_start, int(math.floor(point.y / 100)))
            self.key_range_end = max(self.key_range_end, int(math.ceil(point.y / 100)))

    def get_note_position_parameters(self, note: Note) -> NotePositionParameters:
        text_x = 0
        if self.options.text_align == TextAlignOption.START:
            text_x = int(
                (note.start_pos - self.position_range_start)
                * self.options.pixel_per_beat
                / TICKS_IN_BEAT
                + PADDING
            )
        elif self.options.text_align == TextAlignOption.MIDDLE:
            text_x = int(
                ((note.start_pos + note.end_pos) / 2 - self.position_range_start)
                * self.options.pixel_per_beat
                / TICKS_IN_BEAT
            )
        elif self.options.text_align == TextAlignOption.END:
            text_x = int(
                (note.end_pos - self.position_range_start)
                * self.options.pixel_per_beat
                / TICKS_IN_BEAT
                - PADDING
            )
        return NotePositionParameters(
            point_1=(
                int(
                    (note.start_pos - self.position_range_start)
                    * self.options.pixel_per_beat
                    / TICKS_IN_BEAT
                ),
                int((self.key_range_end - note.key_number) * self.options.note_height),
            ),
            point_2=(
                int(
                    (note.end_pos - self.position_range_start)
                    * self.options.pixel_per_beat
                    / TICKS_IN_BEAT
                ),
                int((self.key_range_end - note.key_number + 1) * self.options.note_height),
            ),
            text_size=self.font_size,
            inner_text=(
                text_x,
                int(
                    (self.key_range_end - note.key_number + 1) * self.options.note_height
                    - PADDING * 1.5
                ),
            ),
            upper_text=(
                text_x,
                int((self.key_range_end - note.key_number) * self.options.note_height - PADDING),
            ),
            lower_text=(
                text_x,
                (self.key_range_end - note.key_number + 2) * self.options.note_height - PADDING,
            ),
        )

    def get_pitch_point(self, param_point: Point) -> tuple[float, float]:
        return (
            (param_point.x - self.position_range_start - self.pitch_position_offset)
            * self.options.pixel_per_beat
            / TICKS_IN_BEAT,
            (self.key_range_end - param_point.y / 100 + 0.5) * self.options.note_height,
        )

    @property
    def size(self) -> tuple[float, float]:
        return (
            (self.position_range_end - self.position_range_start)
            * self.options.pixel_per_beat
            / TICKS_IN_BEAT,
            (self.key_range_end - self.key_range_start + 1) * self.options.note_height,
        )

    @property
    def font_size(self) -> int:
        return self.options.note_height - 2 * PADDING

    @property
    def text_anchor(self) -> str:
        return self.options.text_align.value
