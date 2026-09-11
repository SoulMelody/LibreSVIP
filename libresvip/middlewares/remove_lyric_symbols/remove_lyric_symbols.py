import unicodedata
from importlib.resources import files

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project, SingingTrack

from .options import ProcessOptions

_STRUCTURAL_LYRICS = frozenset({"-", "+", "+~", "+*"})


def remove_numbers_and_punctuation(lyric: str) -> str:
    if lyric in _STRUCTURAL_LYRICS:
        return lyric
    return "".join(
        char
        for char in lyric
        if (category := unicodedata.category(char)) != "Nd" and not category.startswith("P")
    )


class RemoveLyricSymbolsMiddleware(plugin_base.Middleware):
    process_option_cls = ProcessOptions
    info = plugin_base.MiddlewarePluginInfo.load_from_string(
        (files(__package__) / "remove_lyric_symbols.yapsy-plugin").read_text(encoding="utf-8")
    )
    _alias_ = "remove_lyric_symbols"
    _version_ = "1.0.0"

    @classmethod
    def process(cls, project: Project, options: plugin_base.OptionsDict) -> Project:
        cls.process_option_cls.model_validate(options)
        for track in project.track_list:
            if isinstance(track, SingingTrack):
                for note in track.note_list:
                    note.lyric = remove_numbers_and_punctuation(note.lyric)
        return project
