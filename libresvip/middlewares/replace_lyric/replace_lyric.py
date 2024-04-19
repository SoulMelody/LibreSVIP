import functools

from libresvip.core.config import get_ui_settings
from libresvip.extension import base as plugin_base
from libresvip.model.base import Project, SingingTrack

from .options import ProcessOptions


class RemoveShortSilencesMiddleware(plugin_base.MiddlewareBase):
    def process(self, project: Project, options: ProcessOptions) -> Project:
        settings = get_ui_settings()
        if options.lyric_replacement_preset_name in settings.lyric_replace_rules:
            for track in project.track_list:
                if isinstance(track, SingingTrack):
                    for note in track.note_list:
                        note.lyric = functools.reduce(
                            lambda lyric, replacement: replacement.replace(lyric),
                            settings.lyric_replace_rules[options.lyric_replacement_preset_name],
                            note.lyric,
                        )
        return project
