from importlib.resources import files

from libresvip.extension import base as plugin_base
from libresvip.model.base import ParamCurve, Points, Project, SingingTrack

from .options import ProcessOptions


class PitchShiftMiddleware(plugin_base.Middleware):
    process_option_cls = ProcessOptions
    info = plugin_base.MiddlewarePluginInfo.load_from_string(
        (files(__package__) / "pitch_shift.yapsy-plugin").read_text(encoding="utf-8")
    )
    _alias_ = "pitch_shift"
    _version_ = "1.0.0"

    @classmethod
    def process(cls, project: Project, options: plugin_base.OptionsDict) -> Project:
        options_obj = cls.process_option_cls.model_validate(options)
        if options_obj.key:
            return project.model_copy(
                update={
                    "track_list": [
                        track.model_copy(
                            update={
                                "note_list": [
                                    note.model_copy(
                                        update={"key_number": note.key_number + options_obj.key}
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
                                                        y=point.y + options_obj.key * 100
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
