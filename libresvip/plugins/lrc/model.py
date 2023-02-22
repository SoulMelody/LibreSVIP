from functools import partial
from typing import List, Optional

from textx import LanguageDesc, metamodel_from_str

from libresvip.model.base import BaseModel

grammar = """
LyricFile:
    info_tags*=InfoTag
    lyric_lines+=LyricLine
;
LineBreak: '\r'? '\n';
Tag: /[a-zA-Z]+/;
Word: /[^\r\n]*?/;
TimeTag: '[' minute=INT ':' second=INT '.' percent_second=INT ']';
LyricLine: time_tags+=TimeTag lyric?=Word LineBreak;
InfoTag: '[' key=Tag ':' value=Word ']' LineBreak;
"""


class TimeTag(BaseModel):
    minute: int
    second: int
    percent_second: int


class LyricLine(BaseModel):
    time_tags: List[TimeTag]
    lyric: Optional[str]


class InfoTag(BaseModel):
    key: str
    value: str


class LrcFile(BaseModel):
    info_tags: List[InfoTag]
    lyric_lines: List[LyricLine]


TitleInfoTag = partial(InfoTag, key="ti")
ArtistInfoTag = partial(InfoTag, key="ar")
AlbumInfoTag = partial(InfoTag, key="al")
ByInfoTag = partial(InfoTag, key="by")
OffsetInfoTag = partial(InfoTag, key="offset")


LrcModel = metamodel_from_str(
    grammar, skipws=False, classes=[TimeTag, LyricLine, InfoTag]
)

lrc_language = LanguageDesc("lrc", "*.lrc", "lrc歌词文件", metamodel=LrcModel)
