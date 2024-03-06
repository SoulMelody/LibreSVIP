from libresvip.extension import base as plugin_base
from libresvip.model.base import ParamCurve, Points, Project, SingingTrack

from .options import ProcessOptions


class PitchShiftMiddleware(plugin_base.MiddlewareBase):
    def process(self, project: Project, options: ProcessOptions) -> Project:
        if options.key:
            return project.model_copy(
                update={
                    "track_list": [
                        track.model_copy(
                            update={
                                "note_list": [
                                    note.model_copy(
                                        update={"key_number": note.key_number + options.key}
                                    )
                                    for note in track.note_list
                                ],
                                "edited_params": track.edited_params.model_copy(
                                    update={
                                        "pitch": ParamCurve(
                                            points=Points(
                                                root=[
                                                    point
                                                    if point.y == -100
                                                    else point._replace(
                                                        y=point.y + options.key * 100
                                                    )
                                                    for point in track.edited_params.pitch.points.root
                                                ]
                                            )
                                        )
                                    }
                                ),
                            }
                        )
                        if isinstance(track, SingingTrack)
                        else track
                        for track in project.track_list
                    ]
                }
            )
        else:
            return project
