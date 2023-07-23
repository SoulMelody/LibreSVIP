from typing import Iterable

from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    ParamCurve,
    Params,
    Point,
    Points,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
)


def reset_time_axis(project: Project, tempo: int = 125) -> None:
    synchronizer = TimeSynchronizer(project.song_tempo_list, _is_absolute_time_code=True, _default_tempo=tempo)
    for track in project.track_list:
        if isinstance(track, SingingTrack):
            for note in track.note_list:
                end = round(synchronizer.get_actual_ticks_from_ticks(note.start_pos + note.length))
                note.start_pos = round(synchronizer.get_actual_ticks_from_ticks(note.start_pos))
                note.length = end - note.start_pos

            first_bar_ticks = 1920 * project.time_signature_list[0].numerator / project.time_signature_list[0].denominator
            for i in range(len(track.edited_params.pitch.points)):
                pos, val = track.edited_params.pitch.points[i].x, track.edited_params.pitch.points[i].y
                pos = round(synchronizer.get_actual_ticks_from_ticks(pos - first_bar_ticks)) + 1920
                track.edited_params.pitch.points[i] = Point(pos, val)
            for i in range(len(track.edited_params.gender.points)):
                pos, val = track.edited_params.gender.points[i].x, track.edited_params.gender.points[i].y
                pos = round(synchronizer.get_actual_ticks_from_ticks(pos - first_bar_ticks)) + 1920
                track.edited_params.gender.points[i] = Point(pos, val)

    project.song_tempo_list = [SongTempo(bpm=tempo, position=0)]
    project.time_signature_list = [TimeSignature(bar_index=0, numerator=4, denominator=4)]


def split_into_segments(project: Project, min_interval: int = 400, min_length: int = 5000) -> Iterable[tuple[float, Project, float]]:
    track = next((t for t in project.track_list if isinstance(t, SingingTrack)), None)
    if not track or not track.note_list:
        return []

    reset_time_axis(project)
    buffer = [track.note_list[0]]

    cur_seg_start = max(track.note_list[0].start_pos - 600, int(track.note_list[0].start_pos * 0.8))
    cur_seg_interval = track.note_list[0].start_pos
    for i in range(1, len(track.note_list)):
        prev = track.note_list[i - 1]
        cur = track.note_list[i]
        interval = cur.start_pos - prev.end_pos
        if interval >= min_interval and cur.start_pos - interval * 0.8 - cur_seg_start >= min_length:
            prepare_space = min(600, int(cur_seg_interval * 0.8))
            trailing_space = min(400, int(cur_seg_interval * 0.2))
            seg_note_start_pos = buffer[0].start_pos
            pitch_points = [Point(pos - seg_note_start_pos + prepare_space, val) for pos, val in track.edited_params.pitch.points if 1920 <= pos - 1920 <= buffer[-1].end_pos + 50]
            gender_points = [Point(pos - seg_note_start_pos + prepare_space, val) for pos, val in track.edited_params.gender.points if 1920 <= pos - 1920 <= buffer[-1].end_pos + 50]
            for note in buffer:
                note.start_pos = note.start_pos - seg_note_start_pos + prepare_space

            cur_seg_start = cur.start_pos - min(600, int(interval * 0.8))
            cur_seg_interval = interval
            segment = Project(
                song_tempo_list=project.song_tempo_list,
                time_signature_list=[TimeSignature(bar_index=0, numerator=4, denominator=4)],
                track_list=[SingingTrack(
                    note_list=buffer,
                    edited_params=Params(
                        pitch=ParamCurve(points=Points(root=pitch_points)),
                        gender=ParamCurve(points=Points(root=gender_points))
                    )
                )]
            )
            yield (seg_note_start_pos - prepare_space) / 1000.0, segment, trailing_space / 1000.0

            buffer = []

        buffer.append(cur)

    prepare_space = min(600, int(cur_seg_interval * 0.8))
    seg_note_start_pos = buffer[0].start_pos
    pitch_points = [Point(pos - seg_note_start_pos + prepare_space, val) for pos, val in track.edited_params.pitch.points if 1920 <= pos - 1920 <= buffer[-1].end_pos + 50]
    gender_points = [Point(pos - seg_note_start_pos + prepare_space, val) for pos, val in track.edited_params.gender.points if 1920 <= pos - 1920 <= buffer[-1].end_pos + 50]
    for note in buffer:
        note.start_pos = note.start_pos - seg_note_start_pos + prepare_space

    segment = Project(
        song_tempo_list=project.song_tempo_list,
        time_signature_list=[TimeSignature(bar_index=0, numerator=4, denominator=4)],
        track_list=[SingingTrack(
            note_list=buffer,
            edited_params=Params(
                pitch=ParamCurve(points=Points(root=pitch_points)),
                gender=ParamCurve(points=Points(root=gender_points))
            )
        )]
    )
    yield (seg_note_start_pos - prepare_space) / 1000.0, segment, 0.5
