from functools import partial
from typing import Optional

from libresvip.model.base import BaseModel


class TimeTag(BaseModel):
    minute: int
    second: int
    percent_second: int


class LyricLine(BaseModel):
    time_tags: list[TimeTag]
    lyric: Optional[str] = None


class InfoTag(BaseModel):
    key: str
    value: str


class LrcFile(BaseModel):
    info_tags: list[InfoTag]
    lyric_lines: list[LyricLine]


TitleInfoTag = partial(InfoTag, key="ti")
ArtistInfoTag = partial(InfoTag, key="ar")
AlbumInfoTag = partial(InfoTag, key="al")
ByInfoTag = partial(InfoTag, key="by")
OffsetInfoTag = partial(InfoTag, key="offset")
