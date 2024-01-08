import functools

from libresvip.core.constants import DEFAULT_BPM
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    InstrumentalTrack,
    ParamCurve,
    Params,
    Points,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
)


def _update_curve_points_position(
    curve: ParamCurve,
    synchronizer: TimeSynchronizer,
    ori_first_bar_ticks: int,
    new_first_bar_ticks: int,
) -> ParamCurve:
    return ParamCurve(
        points=Points(
            root=[
                point._replace(
                    x=round(synchronizer.get_actual_ticks_from_ticks(point.x - ori_first_bar_ticks))
                    + new_first_bar_ticks
                )
                for point in curve.points.root
            ]
        )
    )


def reset_time_axis(project: Project, tempo: float = DEFAULT_BPM) -> Project:
    synchronizer = TimeSynchronizer(
        project.song_tempo_list, _is_absolute_time_code=True, _default_tempo=tempo
    )
    new_time_signature = TimeSignature(bar_index=0, numerator=4, denominator=4)
    update_curve_points_position = functools.partial(
        _update_curve_points_position,
        synchronizer=synchronizer,
        new_first_bar_ticks=round(new_time_signature.bar_length()),
        ori_first_bar_ticks=project.time_signature_list[0].bar_length(),
    )
    new_track_list = []
    for track in project.track_list:
        if isinstance(track, InstrumentalTrack):
            new_track_list.append(
                track.model_copy(
                    deep=True,
                    update={
                        "offset": round(synchronizer.get_actual_ticks_from_ticks(track.offset))
                    },
                )
            )
        elif isinstance(track, SingingTrack):
            new_note_list = []
            for note in track.note_list:
                note_end = round(synchronizer.get_actual_ticks_from_ticks(note.end_pos))
                note_start = round(synchronizer.get_actual_ticks_from_ticks(note.start_pos))
                new_note_list.append(
                    note.model_copy(
                        deep=True,
                        update={
                            "start_pos": note_start,
                            "length": note_end - note_start,
                        },
                    )
                )
            new_track_list.append(
                track.model_copy(
                    deep=True,
                    update={
                        "note_list": new_note_list,
                        "edited_params": Params(
                            pitch=update_curve_points_position(track.edited_params.pitch),
                            volume=update_curve_points_position(track.edited_params.volume),
                            breath=update_curve_points_position(track.edited_params.breath),
                            gender=update_curve_points_position(track.edited_params.gender),
                            strength=update_curve_points_position(track.edited_params.strength),
                        ),
                    },
                )
            )

    return Project(
        song_tempo_list=[SongTempo(bpm=tempo, position=0)],
        time_signature_list=[new_time_signature],
        track_list=new_track_list,
    )
