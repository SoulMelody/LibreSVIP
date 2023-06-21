from dataclasses import dataclass

from .model import PitchPoint, USTXProject, UVoicePart
from .utils.music_math import MusicMath
from .utils.time_axis import TimeAxis


@dataclass
class BasePitchGenerator:
    pitch_start: int = 0
    pitch_interval: int = 5

    @classmethod
    def base_pitch(cls, part: UVoicePart, project: USTXProject) -> list[float]:
        time_axis = TimeAxis()
        time_axis.build_segments(project)
        u_notes = part.notes
        prev_note = None

        pitches = [0.0] * ((part.notes[-1].end if len(part.notes) else 0) // cls.pitch_interval)
        index = 0
        for note in u_notes:
            if cls.pitch_start + index * cls.pitch_interval < note.position and index < len(pitches) and index > 0:
                pitches[index] = pitches[index - 1]
                index += 1
            while cls.pitch_start + index * cls.pitch_interval < note.end and index < len(pitches):
                pitches[index] = note.tone * 100
                index += 1
        index = max(1, index)
        while index < len(pitches):
            pitches[index] = pitches[index - 1]
            index += 1
        for note in u_notes:
            if note.vibrato.length <= 0:
                continue
            start_index = max(0, int((note.position - cls.pitch_start) / cls.pitch_interval))
            end_index = min(len(pitches), (note.end - cls.pitch_start) // cls.pitch_interval)
            n_period = note.vibrato.period / time_axis.ms_between_tick_pos(note.position, note.end)
            for i in range(start_index, end_index):
                n_pos = (cls.pitch_start + i * cls.pitch_interval - note.position) / note.duration
                point = note.vibrato.evaluate(n_pos, n_period, note)
                pitches[i] = point.y * 100
        for note in u_notes:
            pitch_points = note.pitch.data
            pitch_points = [PitchPoint(
                x=time_axis.ms_pos_to_tick_pos(time_axis.tick_pos_to_ms_pos(part.position + note.position) + point.x) - part.position,
                y=point.y * 10 + note.tone * 100,
                shape=point.shape
            ) for point in pitch_points]
            if len(pitch_points) == 0:
                pitch_points.append(PitchPoint(x=note.position, y=note.tone * 100))
                pitch_points.append(PitchPoint(x=note.end, y=note.tone * 100))
            if note == u_notes[0] and pitch_points[0].x > cls.pitch_start:
                pitch_points.insert(0, PitchPoint(x=cls.pitch_start, y=pitch_points[0].y))
            elif pitch_points[0].x > note.position:
                pitch_points.insert(0, PitchPoint(x=note.position, y=pitch_points[0].y))
            if pitch_points[-1].x < note.end:
                pitch_points.append(PitchPoint(x=note.end, y=pitch_points[-1].y))
            prev_point = pitch_points[0]
            index = max(0, int((prev_point.x - cls.pitch_start) / cls.pitch_interval))
            for point in pitch_points[1:]:
                x = cls.pitch_start + index * cls.pitch_interval
                while x <= point.x and index < len(pitches):
                    pitch = MusicMath.interpolate_shape(prev_point.x, point.x, prev_point.y, point.y, x, prev_point.shape)
                    base_pitch = prev_note.tone * 100 if prev_note is not None and x < prev_note.end else note.tone * 100
                    pitches[index] += pitch - base_pitch
                    index += 1
                    x += cls.pitch_interval
                prev_point = point
            prev_note = note
        return pitches
