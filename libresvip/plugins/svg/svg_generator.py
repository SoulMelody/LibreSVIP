import dataclasses
from typing import List

from svgwrite import Drawing

from libresvip.core.constants import TICKS_IN_BEAT
from libresvip.model.base import Note, ParamCurve, Project, SingingTrack

from .coordinate_helper import CoordinateHelper
from .options import OutputOptions
from .svg_factory import SvgFactory


@dataclasses.dataclass
class SvgGenerator:
    options: OutputOptions
    coordinate_helper: CoordinateHelper = dataclasses.field(init=False)
    svg_factory: SvgFactory = dataclasses.field(init=False)

    def generate_project(self, project: Project) -> Drawing:
        self.coordinate_helper = CoordinateHelper(
            options=self.options,
            pitch_position_offset=project.time_signature_list[0].numerator
            * TICKS_IN_BEAT,
        )
        self.svg_factory = SvgFactory(
            coordinate_helper=self.coordinate_helper,
            options=self.options,
        )
        if self.options.track_index < 0:
            first_singing_track = next(
                (
                    track
                    for track in project.track_list
                    if isinstance(track, SingingTrack)
                ),
                None,
            )
        else:
            first_singing_track = project.track_list[self.options.track_index]
        if first_singing_track is not None:
            self.coordinate_helper.calculate_range(first_singing_track)
            self.generate_notes(first_singing_track.note_list)
            self.generate_pitch(first_singing_track.edited_params.pitch)

        drawing = self.generate_svg()
        return drawing

    def generate_svg(self) -> Drawing:
        drawing = Drawing(size=self.coordinate_helper.size)
        drawing.embed_stylesheet(self.svg_factory.style)
        for rect in self.svg_factory.rect_elements:
            drawing.add(rect)
        for polyline in self.svg_factory.polyline_elements:
            if len(polyline.points):
                drawing.add(polyline)
        for text in self.svg_factory.text_elements:
            drawing.add(text)
        return drawing

    def generate_notes(self, note_list: List[Note]) -> None:
        for note in note_list:
            self.svg_factory.draw_note(note)

    def generate_pitch(self, pitch: ParamCurve) -> None:
        for point in pitch.points[1:-1]:
            self.svg_factory.draw_pitch(point)
