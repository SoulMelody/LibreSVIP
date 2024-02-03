import dataclasses

from drawsvg import Drawing

from libresvip.core.time_sync import TimeSynchronizer
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
            pitch_position_offset=int(project.time_signature_list[0].bar_length()),
        )
        self.svg_factory = SvgFactory(
            coordinate_helper=self.coordinate_helper,
            time_synchronizer=TimeSynchronizer(project.song_tempo_list),
            options=self.options,
        )
        if self.options.track_index < 0:
            first_singing_track = next(
                (track for track in project.track_list if isinstance(track, SingingTrack)),
                None,
            )
        else:
            first_singing_track = project.track_list[self.options.track_index]
        if first_singing_track is not None:
            self.coordinate_helper.calculate_range(first_singing_track)
            if self.options.show_grid:
                self.svg_factory.draw_grid(project.time_signature_list)
            self.generate_notes(first_singing_track.note_list)
            self.generate_pitch(first_singing_track.edited_params.pitch)

        drawing = self.generate_svg()
        return drawing

    def generate_svg(self) -> Drawing:
        drawing = Drawing(*self.coordinate_helper.size)
        drawing.append_css(self.svg_factory.style)
        drawing.extend(self.svg_factory.line_elements)
        drawing.extend(self.svg_factory.rect_elements)
        drawing.extend(self.svg_factory.polyline_elements)
        drawing.extend(self.svg_factory.text_elements)
        return drawing

    def generate_notes(self, note_list: list[Note]) -> None:
        for note in note_list:
            self.svg_factory.draw_note(note)

    def generate_pitch(self, pitch: ParamCurve) -> None:
        for point in pitch.points.root[1:-1]:
            self.svg_factory.draw_pitch(point)
