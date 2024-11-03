from libresvip.core.lyric_phoneme.chinese import get_pinyin_series
from libresvip.core.lyric_phoneme.japanese import (
    to_hiragana,
    to_katakana,
    to_romaji,
)
from libresvip.core.lyric_phoneme.japanese.vocaloid_xsampa import legato_chars
from libresvip.extension import base as plugin_base
from libresvip.model.base import Project, SingingTrack

from .options import ProcessOptions, PronounciationConversionOptions


class PronounciationMiddleware(plugin_base.MiddlewareBase):
    def process(self, project: Project, options: ProcessOptions) -> Project:
        if options.mode != PronounciationConversionOptions.NONE:
            if options.mode == PronounciationConversionOptions.TO_ROMAJI:
                lyric_transformer = to_romaji
            elif options.mode == PronounciationConversionOptions.TO_KATAKANA:
                lyric_transformer = to_katakana
            elif options.mode == PronounciationConversionOptions.TO_HIRAGANA:
                lyric_transformer = to_hiragana
            else:

                def lyric_transformer(lyric: str) -> str:  # type: ignore[misc]
                    return " ".join(get_pinyin_series([lyric]))

            for track in project.track_list:
                if isinstance(track, SingingTrack):
                    for note in track.note_list:
                        note.lyric = (
                            "-" if note.lyric in legato_chars else lyric_transformer(note.lyric)
                        )
        return project
