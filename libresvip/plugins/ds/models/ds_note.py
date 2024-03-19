from dataclasses import InitVar, dataclass, field
from typing import Literal


@dataclass
class DsPhonemeItem:
    phoneme: str = ""
    duration: float = 0.0
    note_name: str = ""


@dataclass
class DsPhoneme:
    consonant: DsPhonemeItem = field(default_factory=DsPhonemeItem)
    vowel: DsPhonemeItem = field(default_factory=DsPhonemeItem)


@dataclass
class DsNote:
    duration: float
    ds_phoneme: DsPhoneme
    lyric: str = ""
    note_name: str = ""

    @property
    def is_slur(self) -> bool:
        return "-" in self.lyric


@dataclass
class AspirationDsPhoneme(DsPhoneme):
    _duration: InitVar[float] = 0.0

    def __post_init__(self, _duration: float) -> None:
        self.vowel = DsPhonemeItem("AP", _duration, "rest")


@dataclass
class AspirationDsNote(DsNote):
    ds_phoneme: AspirationDsPhoneme
    lyric: Literal["AP"] = "AP"
    note_name: Literal["rest"] = "rest"


@dataclass
class RestDsPhoneme(DsPhoneme):
    _duration: InitVar[float] = 0.0

    def __post_init__(self, _duration: float) -> None:
        self.vowel = DsPhonemeItem("SP", _duration, "rest")


@dataclass
class RestDsNote(DsNote):
    ds_phoneme: RestDsPhoneme
    lyric: Literal["SP"] = "SP"
    note_name: Literal["rest"] = "rest"
