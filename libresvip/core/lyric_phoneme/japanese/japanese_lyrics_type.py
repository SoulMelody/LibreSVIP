from enum import Enum, IntFlag


class JapaneseLyricsTypeFLag(IntFlag):
    IS_ROMAJI = 1
    IS_CV = 2


class JapaneseLyricsType(Enum):
    UNKNOWN = ~JapaneseLyricsTypeFLag.IS_ROMAJI & ~JapaneseLyricsTypeFLag.IS_CV
    ROMAJI_CV = JapaneseLyricsTypeFLag.IS_ROMAJI & JapaneseLyricsTypeFLag.IS_CV
    ROMAJI_VCV = JapaneseLyricsTypeFLag.IS_ROMAJI & ~JapaneseLyricsTypeFLag.IS_CV
    KANA_CV = ~JapaneseLyricsTypeFLag.IS_ROMAJI & JapaneseLyricsTypeFLag.IS_CV
    KANA_VCV = ~JapaneseLyricsTypeFLag.IS_ROMAJI & ~JapaneseLyricsTypeFLag.IS_CV
