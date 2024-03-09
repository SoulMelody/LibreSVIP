import fractions

import more_itertools

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project, SingingTrack

from .options import ProcessOptions


class RemoveShortSilencesMiddleware(plugin_base.MiddlewareBase):
    def process(self, project: Project, options: ProcessOptions) -> Project:
        first_bar_tick = round(project.time_signature_list[0].bar_length())
        if min_silence_length := fractions.Fraction(options.fill_threshold.value):
            silence_threshold = first_bar_tick * min_silence_length
            for track in project.track_list:
                if isinstance(track, SingingTrack):
                    for prev_note, note in more_itertools.pairwise(track.note_list):
                        if 0 < note.start_pos - prev_note.end_pos < silence_threshold:
                            prev_note.length = note.start_pos - prev_note.start_pos
        return project
