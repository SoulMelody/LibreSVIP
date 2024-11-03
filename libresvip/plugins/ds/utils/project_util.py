from collections.abc import Iterable

from libresvip.model.base import (
    ParamCurve,
    Params,
    Points,
    Project,
    SingingTrack,
    TimeSignature,
)
from libresvip.model.point import Point
from libresvip.model.reset_time_axis import reset_time_axis


def split_into_segments(
    project: Project, min_interval: int = 400, min_length: int = 5000
) -> Iterable[tuple[float, Project, float]]:
    track = next((t for t in project.track_list if isinstance(t, SingingTrack)), None)
    if not track or not track.note_list:
        return

    project = reset_time_axis(project)
    buffer = [track.note_list[0]]

    cur_seg_start = max(
        track.note_list[0].start_pos - 600,
        int(track.note_list[0].start_pos * 0.8),
    )
    cur_seg_interval = track.note_list[0].start_pos
    for i in range(1, len(track.note_list)):
        prev = track.note_list[i - 1]
        cur = track.note_list[i]
        interval = cur.start_pos - prev.end_pos
        if (
            interval >= min_interval
            and cur.start_pos - interval * 0.8 - cur_seg_start >= min_length
        ):
            prepare_space = min(600, int(cur_seg_interval * 0.8))
            trailing_space = min(400, int(cur_seg_interval * 0.2))
            seg_note_start_pos = buffer[0].start_pos
            pitch_points = [
                Point(pos - seg_note_start_pos + prepare_space, val)
                for pos, val in track.edited_params.pitch.points.root
                if 1920 <= pos - 1920 <= buffer[-1].end_pos + 50
            ]
            gender_points = [
                Point(pos - seg_note_start_pos + prepare_space, val)
                for pos, val in track.edited_params.gender.points.root
                if 1920 <= pos - 1920 <= buffer[-1].end_pos + 50
            ]
            for note in buffer:
                note.start_pos = note.start_pos - seg_note_start_pos + prepare_space

            cur_seg_start = cur.start_pos - min(600, int(interval * 0.8))
            cur_seg_interval = interval
            segment = Project(
                song_tempo_list=project.song_tempo_list,
                time_signature_list=[TimeSignature(bar_index=0, numerator=4, denominator=4)],
                track_list=[
                    SingingTrack(
                        note_list=buffer,
                        edited_params=Params(
                            pitch=ParamCurve(points=Points(root=pitch_points)),
                            gender=ParamCurve(points=Points(root=gender_points)),
                        ),
                    )
                ],
            )
            yield (
                (seg_note_start_pos - prepare_space) / 1000.0,
                segment,
                trailing_space / 1000.0,
            )

            buffer = []

        buffer.append(cur)

    prepare_space = min(600, int(cur_seg_interval * 0.8))
    seg_note_start_pos = buffer[0].start_pos
    pitch_points = [
        Point(pos - seg_note_start_pos + prepare_space, val)
        for pos, val in track.edited_params.pitch.points.root
        if 1920 <= pos - 1920 <= buffer[-1].end_pos + 50
    ]
    gender_points = [
        Point(pos - seg_note_start_pos + prepare_space, val)
        for pos, val in track.edited_params.gender.points.root
        if 1920 <= pos - 1920 <= buffer[-1].end_pos + 50
    ]
    for note in buffer:
        note.start_pos = note.start_pos - seg_note_start_pos + prepare_space

    segment = Project(
        song_tempo_list=project.song_tempo_list,
        time_signature_list=[TimeSignature(bar_index=0, numerator=4, denominator=4)],
        track_list=[
            SingingTrack(
                note_list=buffer,
                edited_params=Params(
                    pitch=ParamCurve(points=Points(root=pitch_points)),
                    gender=ParamCurve(points=Points(root=gender_points)),
                ),
            )
        ],
    )
    yield (seg_note_start_pos - prepare_space) / 1000.0, segment, 0.5
