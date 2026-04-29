import functools
from collections.abc import MutableMapping
from importlib.resources import files
from typing import Any

from libresvip.core.config import LibreSVIPSettingsContainer, LyricsReplacement
from libresvip.extension import base as plugin_base
from libresvip.model.base import Project, SingingTrack

from .options import ProcessOptions


def replace_lyric(text: str, replacement: LyricsReplacement | MutableMapping[str, Any]) -> str:
    if isinstance(replacement, MutableMapping):
        replacement = LyricsReplacement(**replacement)
    return replacement.replace(text)


class ReplaceLyricsMiddleware(plugin_base.Middleware):
    process_option_cls = ProcessOptions
    info = plugin_base.MiddlewarePluginInfo.load_from_string(
        (files(__package__) / "replace_lyric.yapsy-plugin").read_text(encoding="utf-8")
    )
    _alias_ = "replace_lyric"
    _version_ = "1.0.0"

    @classmethod
    def process(cls, project: Project, options: plugin_base.OptionsDict) -> Project:
        options_obj = cls.process_option_cls.model_validate(options)
        if (settings := LibreSVIPSettingsContainer.settings.resolve_sync()) and (
            options_obj.lyric_replacement_preset_name in settings.lyric_replace_rules
        ):
            for track in project.track_list:
                if isinstance(track, SingingTrack):
                    for note in track.note_list:
                        note.lyric = functools.reduce(
                            lambda lyric, replacement: replace_lyric(replacement, lyric),
                            settings.lyric_replace_rules[options_obj.lyric_replacement_preset_name],
                            note.lyric,
                        )
        return project
