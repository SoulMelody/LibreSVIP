import functools
from collections.abc import Callable
from typing import Optional

import more_itertools

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
    func: Callable[[int], float],
    ori_first_bar_ticks: int,
    new_first_bar_ticks: int,
    limit_func: Optional[Callable[[int], bool]] = None,
) -> ParamCurve:
    return ParamCurve(
        points=Points(
            root=[
                point._replace(x=round(func(point.x - ori_first_bar_ticks)) + new_first_bar_ticks)
                for point in curve.points.root
                if limit_func is None or limit_func(point.x - ori_first_bar_ticks)
            ]
        )
    )


def reset_time_axis(project: Project, tempo: float = DEFAULT_BPM) -> Project:
    synchronizer = TimeSynchronizer(
        project.song_tempo_list,
        _is_absolute_time_code=True,
        _default_tempo=tempo,
    )
    new_time_signature = TimeSignature(bar_index=0, numerator=4, denominator=4)
    update_curve_points_position = functools.partial(
        _update_curve_points_position,
        func=synchronizer.get_actual_ticks_from_ticks,
        new_first_bar_ticks=round(new_time_signature.bar_length()),
        ori_first_bar_ticks=round(project.time_signature_list[0].bar_length()),
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


def zoom_project(project: Project, factor: float) -> Project:
    time_signature_list = [
        time_signature.model_copy(update={"bar_index": round(time_signature.bar_index * factor)})
        for time_signature in more_itertools.unique_in_window(
            project.time_signature_list, 2, key=str
        )
    ]
    update_curve_points_position = functools.partial(
        _update_curve_points_position,
        func=factor.__mul__,
        new_first_bar_ticks=round(time_signature_list[0].bar_length()),
        ori_first_bar_ticks=round(project.time_signature_list[0].bar_length()),
    )
    return project.model_copy(
        update={
            "song_tempo_list": [
                song_tempo.model_copy(
                    update={
                        "position": round(song_tempo.position * factor),
                        "bpm": song_tempo.bpm * factor,
                    }
                )
                for song_tempo in project.song_tempo_list
            ],
            "time_signature_list": time_signature_list,
            "track_list": [
                track.model_copy(update={"offset": round(factor * track.offset)})
                if isinstance(track, InstrumentalTrack)
                else track.model_copy(
                    update={
                        "note_list": [
                            note.model_copy(
                                update={
                                    "start_pos": round(factor * note.start_pos),
                                    "length": round(factor * note.length),
                                }
                            )
                            for note in track.note_list
                        ],
                        "edited_params": Params(
                            pitch=update_curve_points_position(track.edited_params.pitch),
                            volume=update_curve_points_position(track.edited_params.volume),
                            breath=update_curve_points_position(track.edited_params.breath),
                            gender=update_curve_points_position(track.edited_params.gender),
                            strength=update_curve_points_position(track.edited_params.strength),
                        ),
                    }
                )
                for track in project.track_list
            ],
        }
    )


def limit_bars(project: Project, max_bars: int) -> Project:
    time_signature_list = [
        time_signature
        for time_signature in project.time_signature_list
        if time_signature.bar_index < max_bars
    ]
    first_bar_length = round(time_signature_list[0].bar_length())
    max_ticks = max_bars * first_bar_length
    update_curve_points_position = functools.partial(
        _update_curve_points_position,
        func=int,
        new_first_bar_ticks=first_bar_length,
        ori_first_bar_ticks=first_bar_length,
        limit_func=max_ticks.__gt__,
    )
    return project.model_copy(
        update={
            "song_tempo_list": [
                song_tempo
                for song_tempo in project.song_tempo_list
                if song_tempo.position < max_ticks
            ],
            "time_signature_list": time_signature_list,
            "track_list": [
                track
                if isinstance(track, InstrumentalTrack)
                else track.model_copy(
                    update={
                        "note_list": [note for note in track.note_list if note.end_pos < max_ticks],
                        "edited_params": Params(
                            pitch=update_curve_points_position(track.edited_params.pitch),
                            volume=update_curve_points_position(track.edited_params.volume),
                            breath=update_curve_points_position(track.edited_params.breath),
                            gender=update_curve_points_position(track.edited_params.gender),
                            strength=update_curve_points_position(track.edited_params.strength),
                        ),
                    }
                )
                for track in project.track_list
            ],
        }
    )
