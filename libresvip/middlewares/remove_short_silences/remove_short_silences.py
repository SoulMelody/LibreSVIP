import fractions
from importlib.resources import files

import more_itertools

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project, SingingTrack

from .options import ProcessOptions


class RemoveShortSilencesMiddleware(plugin_base.Middleware):
    process_option_cls = ProcessOptions
    info = plugin_base.MiddlewarePluginInfo.load_from_string(
        (files(__package__) / "remove_short_silences.yapsy-plugin").read_text(encoding="utf-8")
    )
    _alias_ = "remove_short_silences"
    _version_ = "1.0.0"

    @classmethod
    def process(cls, project: Project, options: plugin_base.OptionsDict) -> Project:
        options_obj = cls.process_option_cls.model_validate(options)
        first_bar_tick = round(project.time_signature_list[0].bar_length())
        if min_silence_length := fractions.Fraction(options_obj.fill_threshold.value):
            silence_threshold = first_bar_tick * min_silence_length
            for track in project.track_list:
                if isinstance(track, SingingTrack):
                    for prev_note, note in more_itertools.pairwise(track.note_list):
                        if 0 < note.start_pos - prev_note.end_pos < silence_threshold:
                            prev_note.length = note.start_pos - prev_note.start_pos
        return project
