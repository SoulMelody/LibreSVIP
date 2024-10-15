# mypy: disable-error-code="attr-defined"
import dataclasses
import operator

import more_itertools

from .model import PitchPoint, USTXProject, UVoicePart
from .utils import music_math
from .utils.time_axis import TimeAxis


@dataclasses.dataclass
class BasePitchGenerator:
    project: dataclasses.InitVar[USTXProject]
    pitch_start: int = 0
    pitch_interval: int = 5
    time_axis: TimeAxis = dataclasses.field(init=False)

    def __post_init__(self, project: USTXProject) -> None:
        self.time_axis = TimeAxis()
        self.time_axis.build_segments(project)

    def base_pitch(self, part: UVoicePart) -> list[float]:
        pitches = [0.0] * (part.notes[-1].end // self.pitch_interval) if part.notes else []
        prev_note = None

        index = 0
        for note in part.notes:
            if (
                0 < index < len(pitches)
                and self.pitch_start + index * self.pitch_interval < note.position
            ):
                pitches[index] = pitches[index - 1]
                index += 1
            if (
                index < len(pitches)
                and (pad := (note.end - self.pitch_start) // self.pitch_interval - index) >= 0
            ):
                pitches[index : index + pad + 1] = [note.tone * 100] * (pad + 1)
                index += pad + 1
        index = max(1, index)
        if index < len(pitches):
            pitches[index:] = [pitches[index - 1]] * (len(pitches) - index)

        for note in part.notes:
            if note.vibrato.length <= 0 or note.vibrato.period is None:
                continue
            start_index = max(
                0,
                int((note.position - self.pitch_start) / self.pitch_interval),
            )
            end_index = min(
                len(pitches),
                (note.end - self.pitch_start) // self.pitch_interval,
            )
            n_period = note.vibrato.period / self.time_axis.ms_between_tick_pos(
                note.position, note.end
            )
            for i in range(start_index, end_index):
                n_pos = (self.pitch_start + i * self.pitch_interval - note.position) / note.duration
                point = note.vibrato.evaluate(n_pos, n_period, note)
                pitches[i] = point[1] * 100

        for note in part.notes:
            pitch_points = list(
                more_itertools.unique_justseen(
                    (
                        PitchPoint(
                            x=self.time_axis.ms_pos_to_tick_pos(
                                self.time_axis.tick_pos_to_ms_pos(part.position + note.position)
                                + point.x
                            )
                            - part.position,
                            y=point.y * 10 + note.tone * 100,
                            shape=point.shape,
                        )
                        for point in note.pitch.data
                    ),
                    key=operator.attrgetter("x"),
                )
            )
            if not pitch_points:
                pitch_points.append(PitchPoint(x=note.position, y=note.tone * 100))
                pitch_points.append(PitchPoint(x=note.end, y=note.tone * 100))
            if note == part.notes[0] and pitch_points[0].x > self.pitch_start:
                pitch_points.insert(0, PitchPoint(x=self.pitch_start, y=pitch_points[0].y))
            elif pitch_points[0].x > note.position:
                pitch_points.insert(0, PitchPoint(x=note.position, y=pitch_points[0].y))
            if pitch_points[-1].x < note.end:
                pitch_points.append(PitchPoint(x=note.end, y=pitch_points[-1].y))
            prev_point = pitch_points[0]
            index = max(0, int((prev_point.x - self.pitch_start) / self.pitch_interval))
            for point in pitch_points[1:]:
                x = self.pitch_start + index * self.pitch_interval
                while x <= point.x and index < len(pitches):
                    pitch = music_math.interpolate_shape(
                        (prev_point.x, prev_point.y),
                        (point.x, point.y),
                        x,
                        prev_point.shape or "lo",
                    )
                    base_pitch = (
                        prev_note.tone * 100
                        if prev_note is not None and x <= prev_note.end
                        else note.tone * 100
                    )
                    pitches[index] += pitch - base_pitch
                    index += 1
                    x += self.pitch_interval
                prev_point = point
            prev_note = note

        return pitches
