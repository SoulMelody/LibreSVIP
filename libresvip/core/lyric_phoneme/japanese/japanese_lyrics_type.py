from enum import Enum, IntFlag


class JapaneseLyricsTypeFLag(IntFlag):
    IS_ROMAJI = 1
    IS_CV = 2
    OTHER = 4


class JapaneseLyricsType(Enum):
    UNKNOWN = JapaneseLyricsTypeFLag.OTHER
    ROMAJI_CV = (
        ~JapaneseLyricsTypeFLag.OTHER
        & JapaneseLyricsTypeFLag.IS_ROMAJI
        & JapaneseLyricsTypeFLag.IS_CV
    )
    ROMAJI_VCV = (
        ~JapaneseLyricsTypeFLag.OTHER
        & JapaneseLyricsTypeFLag.IS_ROMAJI
        & ~JapaneseLyricsTypeFLag.IS_CV
    )
    KANA_CV = (
        ~JapaneseLyricsTypeFLag.OTHER
        & ~JapaneseLyricsTypeFLag.IS_ROMAJI
        & JapaneseLyricsTypeFLag.IS_CV
    )
    KANA_VCV = (
        ~JapaneseLyricsTypeFLag.OTHER
        & ~JapaneseLyricsTypeFLag.IS_ROMAJI
        & ~JapaneseLyricsTypeFLag.IS_CV
    )
