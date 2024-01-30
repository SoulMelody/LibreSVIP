from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional, Union

from xsdata.models.datatype import XmlTime


@dataclass
class CeVIOAuthor:
    class Meta:
        name = "Author"

    version: Optional[str] = field(
        default="3.2.21.2",
        metadata={
            "name": "Version",
            "type": "Attribute",
        },
    )


@dataclass
class CeVIONoData:
    class Meta:
        name = "NoData"

    index: Optional[int] = field(
        default=None,
        metadata={
            "name": "Index",
            "type": "Attribute",
        },
    )
    repeat: Optional[int] = field(
        default=None,
        metadata={
            "name": "Repeat",
            "type": "Attribute",
        },
    )


@dataclass
class CeVIOData(CeVIONoData):
    class Meta:
        name = "Data"

    value: Optional[Union[float, int, Decimal]] = field(default=None)


@dataclass
class CeVIODictExtension:
    class Meta:
        name = "Extension"

    version: Optional[str] = field(
        default="1.0.0",
        metadata={
            "name": "Version",
            "type": "Attribute",
        },
    )

    language: Optional[str] = field(
        default="English",
        metadata={
            "name": "Language",
            "type": "Attribute",
        },
    )


@dataclass
class CeVIODictionary:
    class Meta:
        name = "Dictionary"

    version: Optional[str] = field(
        default="1.0.0",
        metadata={
            "name": "Version",
            "type": "Attribute",
        },
    )
    extension: Optional[CeVIODictExtension] = field(
        default=None,
        metadata={
            "name": "Extension",
            "type": "Element",
        },
    )


@dataclass
class CeVIODynamics:
    class Meta:
        name = "Dynamics"

    clock: Optional[int] = field(
        default=None,
        metadata={
            "name": "Clock",
            "type": "Attribute",
        },
    )
    value: Optional[int] = field(
        default=None,
        metadata={
            "name": "Value",
            "type": "Attribute",
        },
    )


@dataclass
class CeVIOTalkExtension:
    class Meta:
        name = "Extension"

    vertical_ratio: Optional[str] = field(
        default=None,
        metadata={
            "name": "VerticalRatio",
            "type": "Attribute",
        },
    )


@dataclass
class CeVIOGroup:
    class Meta:
        name = "Group"

    version: Optional[str] = field(
        default="1.0",
        metadata={
            "name": "Version",
            "type": "Attribute",
        },
    )
    group_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "Id",
            "type": "Attribute",
        },
    )
    category: str = field(
        default="SingerSong",
        metadata={
            "name": "Category",
            "type": "Attribute",
        },
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "name": "Name",
            "type": "Attribute",
        },
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "name": "Color",
            "type": "Attribute",
        },
    )
    volume: Optional[float] = field(
        default=None,
        metadata={
            "name": "Volume",
            "type": "Attribute",
        },
    )
    pan: Optional[float] = field(
        default=None,
        metadata={
            "name": "Pan",
            "type": "Attribute",
        },
    )
    is_solo: Optional[bool] = field(
        default=False,
        metadata={
            "name": "IsSolo",
            "type": "Attribute",
        },
    )
    is_muted: Optional[bool] = field(
        default=False,
        metadata={
            "name": "IsMuted",
            "type": "Attribute",
        },
    )
    cast_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "CastId",
            "type": "Attribute",
        },
    )
    language: Optional[str] = field(
        default="Japanese",
        metadata={
            "name": "Language",
            "type": "Attribute",
        },
    )
    snapshot: Optional[str] = field(
        default=None,
        metadata={
            "name": "SnapShot",
            "type": "Attribute",
        },
    )


@dataclass
class CeVIOKey:
    class Meta:
        name = "Key"

    clock: Optional[int] = field(
        default=None,
        metadata={
            "name": "Clock",
            "type": "Attribute",
        },
    )
    fifths: Optional[int] = field(
        default=None,
        metadata={
            "name": "Fifths",
            "type": "Attribute",
        },
    )
    mode: Optional[int] = field(
        default=None,
        metadata={
            "name": "Mode",
            "type": "Attribute",
        },
    )


@dataclass
class CeVIONote:
    class Meta:
        name = "Note"

    clock: Optional[int] = field(
        default=None,
        metadata={
            "name": "Clock",
            "type": "Attribute",
        },
    )
    pitch_step: Optional[int] = field(
        default=None,
        metadata={
            "name": "PitchStep",
            "type": "Attribute",
        },
    )
    pitch_octave: Optional[int] = field(
        default=None,
        metadata={
            "name": "PitchOctave",
            "type": "Attribute",
        },
    )
    duration: Optional[int] = field(
        default=None,
        metadata={
            "name": "Duration",
            "type": "Attribute",
        },
    )
    lyric: Optional[str] = field(
        default=None,
        metadata={
            "name": "Lyric",
            "type": "Attribute",
        },
    )
    phonetic: Optional[str] = field(
        default=None,
        metadata={
            "name": "Phonetic",
            "type": "Attribute",
        },
    )
    do_re_mi: Optional[bool] = field(
        default=None,
        metadata={
            "name": "DoReMi",
            "type": "Attribute",
        },
    )
    staccato: Optional[bool] = field(
        default=None,
        metadata={
            "name": "Staccato",
            "type": "Attribute",
        },
    )
    slur_start: Optional[bool] = field(
        default=None,
        metadata={
            "name": "SlurStart",
            "type": "Attribute",
        },
    )
    slur_stop: Optional[bool] = field(
        default=None,
        metadata={
            "name": "SlurStop",
            "type": "Attribute",
        },
    )
    syllabic: Optional[int] = field(
        default=None,
        metadata={
            "name": "Syllabic",
            "type": "Attribute",
        },
    )
    accent: Optional[bool] = field(
        default=None,
        metadata={
            "name": "Accent",
            "type": "Attribute",
        },
    )
    breath: Optional[bool] = field(
        default=None,
        metadata={
            "name": "Breath",
            "type": "Attribute",
        },
    )


@dataclass
class CeVIOReferenceState:
    class Meta:
        name = "ReferenceState"

    current: Optional[str] = field(
        default=None,
        metadata={
            "name": "Current",
            "type": "Attribute",
        },
    )
    previous: Optional[str] = field(
        default=None,
        metadata={
            "name": "Previous",
            "type": "Attribute",
        },
    )


@dataclass
class CeVIOSound:
    class Meta:
        name = "Sound"

    clock: Optional[int] = field(
        default=None,
        metadata={
            "name": "Clock",
            "type": "Attribute",
        },
    )
    tempo: Optional[float] = field(
        default=None,
        metadata={
            "name": "Tempo",
            "type": "Attribute",
        },
    )


@dataclass
class CeVIOSoundSetting:
    class Meta:
        name = "SoundSetting"

    rhythm: Optional[str] = field(
        default="4/4",
        metadata={
            "name": "Rhythm",
            "type": "Attribute",
        },
    )
    tempo: Optional[float] = field(
        default=120.0,
        metadata={
            "name": "Tempo",
            "type": "Attribute",
        },
    )
    master_volume: Optional[float] = field(
        default=None,
        metadata={
            "name": "MasterVolume",
            "type": "Attribute",
        },
    )


@dataclass
class CeVIOSoundSource:
    class Meta:
        name = "SoundSource"

    version: Optional[str] = field(
        default="1.0.0",
        metadata={
            "name": "Version",
            "type": "Attribute",
        },
    )
    sound_source_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "Id",
            "type": "Attribute",
        },
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "name": "Name",
            "type": "Attribute",
        },
    )


@dataclass
class CeVIOTime:
    class Meta:
        name = "Time"

    clock: Optional[int] = field(
        default=None,
        metadata={
            "name": "Clock",
            "type": "Attribute",
        },
    )
    beats: Optional[int] = field(
        default=None,
        metadata={
            "name": "Beats",
            "type": "Attribute",
        },
    )
    beat_type: Optional[int] = field(
        default=None,
        metadata={
            "name": "BeatType",
            "type": "Attribute",
        },
    )


@dataclass
class CeVIOViewScale:
    class Meta:
        name = "ViewScale"

    horizontal: Optional[Union[int, float]] = field(
        default=None,
        metadata={
            "name": "Horizontal",
            "type": "Attribute",
        },
    )
    vertical: Optional[Union[int, Decimal]] = field(
        default=None,
        metadata={
            "name": "Vertical",
            "type": "Attribute",
        },
    )


@dataclass
class CeVIOBeat:
    class Meta:
        name = "Beat"

    time: list[CeVIOTime] = field(
        default_factory=list,
        metadata={
            "name": "Time",
            "type": "Element",
        },
    )


@dataclass
class CeVIOGroups:
    class Meta:
        name = "Groups"

    active_group: Optional[str] = field(
        default=None,
        metadata={
            "name": "ActiveGroup",
            "type": "Attribute",
        },
    )
    group: list[CeVIOGroup] = field(
        default_factory=list,
        metadata={
            "name": "Group",
            "type": "Element",
        },
    )


@dataclass
class CeVIOScore:
    class Meta:
        name = "Score"

    alpha: Optional[float] = field(
        default=None,
        metadata={
            "name": "Alpha",
            "type": "Attribute",
        },
    )
    tune: Optional[float] = field(
        default=None,
        metadata={
            "name": "Tune",
            "type": "Attribute",
        },
    )
    pitch_shift: Optional[float] = field(
        default=None,
        metadata={
            "name": "PitchShift",
            "type": "Attribute",
        },
    )
    pitch_tune: Optional[float] = field(
        default=None,
        metadata={
            "name": "PitchTune",
            "type": "Attribute",
        },
    )
    husky: Optional[float] = field(
        default=None,
        metadata={
            "name": "Husky",
            "type": "Attribute",
        },
    )
    vib_amp: Optional[float] = field(
        default=None,
        metadata={
            "name": "VibAmp",
            "type": "Attribute",
        },
    )
    vib_frq: Optional[float] = field(
        default=None,
        metadata={
            "name": "VibFrq",
            "type": "Attribute",
        },
    )
    emotion0: Optional[Union[float, int]] = field(
        default=None,
        metadata={
            "name": "Emotion0",
            "type": "Attribute",
        },
    )
    emotion1: Optional[Union[float, int]] = field(
        default=None,
        metadata={
            "name": "Emotion1",
            "type": "Attribute",
        },
    )
    key: list[CeVIOKey] = field(
        default_factory=list,
        metadata={
            "name": "Key",
            "type": "Element",
        },
    )
    dynamics: list[CeVIODynamics] = field(
        default_factory=list,
        metadata={
            "name": "Dynamics",
            "type": "Element",
            "sequential": True,
        },
    )
    note: list[CeVIONote] = field(
        default_factory=list,
        metadata={
            "name": "Note",
            "type": "Element",
            "sequential": True,
        },
    )


@dataclass
class CeVIOSongEditor:
    class Meta:
        name = "SongEditor"

    partition: Optional[int] = field(
        default=None,
        metadata={
            "name": "Partition",
            "type": "Attribute",
        },
    )
    quantize: Optional[int] = field(
        default=None,
        metadata={
            "name": "Quantize",
            "type": "Attribute",
        },
    )
    mode: Optional[int] = field(
        default=None,
        metadata={
            "name": "Mode",
            "type": "Attribute",
        },
    )
    editing_tool: Optional[int] = field(
        default=None,
        metadata={
            "name": "EditingTool",
            "type": "Attribute",
        },
    )
    view_scale: Optional[CeVIOViewScale] = field(
        default=None,
        metadata={
            "name": "ViewScale",
            "type": "Element",
        },
    )
    reference_state: Optional[CeVIOReferenceState] = field(
        default=None,
        metadata={
            "name": "ReferenceState",
            "type": "Element",
        },
    )


@dataclass
class CeVIOSoundSources:
    class Meta:
        name = "SoundSources"

    sound_source: list[CeVIOSoundSource] = field(
        default_factory=list,
        metadata={
            "name": "SoundSource",
            "type": "Element",
        },
    )


@dataclass
class CeVIOTts:
    class Meta:
        name = "TTS"

    version: Optional[str] = field(
        default="3.1.0",
        metadata={
            "name": "Version",
            "type": "Attribute",
        },
    )
    dictionary: Optional[CeVIODictionary] = field(
        default_factory=CeVIODictionary,
        metadata={
            "name": "Dictionary",
            "type": "Element",
        },
    )
    sound_sources: Optional[CeVIOSoundSources] = field(
        default_factory=CeVIOSoundSources,
        metadata={
            "name": "SoundSources",
            "type": "Element",
        },
    )


@dataclass
class CeVIOTalkEditor:
    class Meta:
        name = "TalkEditor"

    partition: Optional[int] = field(
        default=None,
        metadata={
            "name": "Partition",
            "type": "Attribute",
        },
    )
    extension: Optional[CeVIOTalkExtension] = field(
        default=None,
        metadata={
            "name": "Extension",
            "type": "Element",
        },
    )


@dataclass
class CeVIOTempo:
    class Meta:
        name = "Tempo"

    sound: list[CeVIOSound] = field(
        default_factory=list,
        metadata={
            "name": "Sound",
            "type": "Element",
        },
    )


@dataclass
class CeVIOTimeline:
    class Meta:
        name = "Timeline"

    partition: Optional[str] = field(
        default=None,
        metadata={
            "name": "Partition",
            "type": "Attribute",
        },
    )
    current_position: Optional[XmlTime] = field(
        default=None,
        metadata={
            "name": "CurrentPosition",
            "type": "Attribute",
        },
    )
    start_position: Optional[XmlTime] = field(
        default=None,
        metadata={
            "name": "StartPosition",
            "type": "Attribute",
        },
    )
    end_position: Optional[XmlTime] = field(
        default=None,
        metadata={
            "name": "EndPosition",
            "type": "Attribute",
        },
    )
    view_scale: Optional[CeVIOViewScale] = field(
        default=None,
        metadata={
            "name": "ViewScale",
            "type": "Element",
        },
    )


@dataclass
class CeVIOParameter:
    class Meta:
        name = "Parameter"

    length: Optional[int] = field(
        default=None,
        metadata={
            "name": "Length",
            "type": "Attribute",
        },
    )
    data: list[Union[CeVIOData, float, Decimal, int]] = field(
        default_factory=list,
        metadata={
            "name": "Data",
            "type": "Element",
        },
    )
    no_data: Optional[list[CeVIONoData]] = field(
        default=None,
        metadata={
            "name": "NoData",
            "type": "Element",
        },
    )


@dataclass
class CeVIOParameters:
    class Meta:
        name = "Parameters"

    timing: Optional[CeVIOParameter] = field(
        default=None,
        metadata={
            "name": "Timing",
            "type": "Element",
        },
    )
    log_f0: Optional[CeVIOParameter] = field(
        default=None,
        metadata={
            "name": "LogF0",
            "type": "Element",
        },
    )
    c0: Optional[CeVIOParameter] = field(
        default=None,
        metadata={
            "name": "C0",
            "type": "Element",
        },
    )
    vib_amp: Optional[CeVIOParameter] = field(
        default=None,
        metadata={
            "name": "VibAmp",
            "type": "Element",
        },
    )
    vib_frq: Optional[CeVIOParameter] = field(
        default=None,
        metadata={
            "name": "VibFrq",
            "type": "Element",
        },
    )
    alpha: Optional[CeVIOParameter] = field(
        default=None,
        metadata={
            "name": "Alpha",
            "type": "Element",
        },
    )
    husky: Optional[CeVIOParameter] = field(
        default=None,
        metadata={
            "name": "Husky",
            "type": "Element",
        },
    )


@dataclass
class CeVIOSvss:
    class Meta:
        name = "SVSS"

    version: Optional[str] = field(
        default="3.0.5",
        metadata={
            "name": "Version",
            "type": "Attribute",
        },
    )
    dictionary: Optional[CeVIODictionary] = field(
        default_factory=CeVIODictionary,
        metadata={
            "name": "Dictionary",
            "type": "Element",
        },
    )
    sound_sources: Optional[CeVIOSoundSources] = field(
        default_factory=CeVIOSoundSources,
        metadata={
            "name": "SoundSources",
            "type": "Element",
        },
    )


@dataclass
class CeVIOGeneration:
    class Meta:
        name = "Generation"

    author: Optional[CeVIOAuthor] = field(
        default_factory=CeVIOAuthor,
        metadata={
            "name": "Author",
            "type": "Element",
        },
    )
    tts: Optional[CeVIOTts] = field(
        default_factory=CeVIOTts,
        metadata={
            "name": "TTS",
            "type": "Element",
        },
    )
    svss: Optional[CeVIOSvss] = field(
        default_factory=CeVIOSvss,
        metadata={
            "name": "SVSS",
            "type": "Element",
        },
    )


@dataclass
class CeVIOSong:
    class Meta:
        name = "Song"

    version: Optional[str] = field(
        default="1.02",
        metadata={
            "name": "Version",
            "type": "Attribute",
        },
    )
    common_keys: Optional[bool] = field(
        default=None,
        metadata={
            "name": "CommonKeys",
            "type": "Attribute",
        },
    )
    tempo: Optional[CeVIOTempo] = field(
        default=None,
        metadata={
            "name": "Tempo",
            "type": "Element",
        },
    )
    beat: Optional[CeVIOBeat] = field(
        default=None,
        metadata={
            "name": "Beat",
            "type": "Element",
        },
    )
    score: Optional[CeVIOScore] = field(
        default_factory=CeVIOScore,
        metadata={
            "name": "Score",
            "type": "Element",
        },
    )
    parameter: Optional[CeVIOParameters] = field(
        default_factory=CeVIOParameters,
        metadata={
            "name": "Parameter",
            "type": "Element",
        },
    )


@dataclass
class CeVIOBaseUnit:
    version: Optional[str] = field(
        default="1.0",
        metadata={
            "name": "Version",
            "type": "Attribute",
        },
    )
    unit_id: Optional[str] = field(
        default="",
        metadata={
            "name": "Id",
            "type": "Attribute",
        },
    )
    group: Optional[str] = field(
        default=None,
        metadata={
            "name": "Group",
            "type": "Attribute",
        },
    )
    start_time: Optional[XmlTime] = field(
        default=None,
        metadata={
            "name": "StartTime",
            "type": "Attribute",
        },
    )
    duration: Optional[XmlTime] = field(
        default=None,
        metadata={
            "name": "Duration",
            "type": "Attribute",
        },
    )
    category: str = field(
        default="SingerSong",
        metadata={
            "name": "Category",
            "type": "Attribute",
        },
    )
    text: Optional[str] = field(
        default=None,
        metadata={
            "name": "Text",
            "type": "Attribute",
        },
    )
    snap_shot: Optional[str] = field(
        default=None,
        metadata={
            "name": "SnapShot",
            "type": "Attribute",
        },
    )


@dataclass
class CeVIOSongUnit(CeVIOBaseUnit):
    song: Optional[CeVIOSong] = field(
        default=None,
        metadata={
            "name": "Song",
            "type": "Element",
        },
    )
    cast_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "CastId",
            "type": "Attribute",
        },
    )
    language: Optional[str] = field(
        default="Japanese",
        metadata={
            "name": "Language",
            "type": "Attribute",
        },
    )


@dataclass
class CeVIOComponent:
    class Meta:
        name = "Component"

    name: Optional[str] = field(
        default=None,
        metadata={
            "name": "Name",
            "type": "Attribute",
            "required": True,
        },
    )
    value: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "Value",
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass
class CeVIOPhoneme:
    class Meta:
        name = "Phoneme"

    data: Optional[str] = field(
        default=None,
        metadata={
            "name": "Data",
            "type": "Attribute",
            "required": True,
        },
    )
    volume: Optional[Union[Decimal, float]] = field(
        default=None,
        metadata={
            "name": "Volume",
            "type": "Attribute",
        },
    )
    speed: Optional[Union[float, Decimal]] = field(
        default=None,
        metadata={
            "name": "Speed",
            "type": "Attribute",
        },
    )
    tone: Optional[Union[Decimal, float]] = field(
        default=None,
        metadata={
            "name": "Tone",
            "type": "Attribute",
        },
    )


@dataclass
class CeVIODirection:
    class Meta:
        name = "Direction"

    volume: Optional[float] = field(
        default=None,
        metadata={
            "name": "Volume",
            "type": "Attribute",
            "required": True,
        },
    )
    speed: Optional[float] = field(
        default=None,
        metadata={
            "name": "Speed",
            "type": "Attribute",
            "required": True,
        },
    )
    tone: Optional[float] = field(
        default=None,
        metadata={
            "name": "Tone",
            "type": "Attribute",
            "required": True,
        },
    )
    alpha: Optional[float] = field(
        default=None,
        metadata={
            "name": "Alpha",
            "type": "Attribute",
            "required": True,
        },
    )
    log_f0_scale: Optional[float] = field(
        default=None,
        metadata={
            "name": "LogF0Scale",
            "type": "Attribute",
            "required": True,
        },
    )
    component: list[CeVIOComponent] = field(
        default_factory=list,
        metadata={
            "name": "Component",
            "type": "Element",
            "min_occurs": 1,
        },
    )


@dataclass
class CeVIOPhonemes:
    class Meta:
        name = "Phonemes"

    phoneme: list[CeVIOPhoneme] = field(
        default_factory=list,
        metadata={
            "name": "Phoneme",
            "type": "Element",
            "min_occurs": 1,
        },
    )


@dataclass
class Word:
    class Meta:
        name = "word"

    phoneme: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    pronunciation: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    pos: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    value: str = field(default="")


@dataclass
class AcousticPhrase:
    class Meta:
        name = "acoustic_phrase"

    word: list[Word] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )


@dataclass
class Base:
    acoustic_phrase: list[AcousticPhrase] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )


@dataclass
class Edited:
    acoustic_phrase: list[AcousticPhrase] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )


@dataclass
class CeVIOMetadataEN:
    class Meta:
        name = "Metadata_EN"

    base: Optional[Base] = field(
        default=None,
        metadata={
            "name": "Base",
            "type": "Element",
            "required": True,
        },
    )
    edited: Optional[Edited] = field(
        default=None,
        metadata={
            "name": "Edited",
            "type": "Element",
        },
    )


@dataclass
class CeVIOTalkUnit(CeVIOBaseUnit):
    metadata: Optional[str] = field(
        default=None,
        metadata={
            "name": "Metadata",
            "type": "Element",
        },
    )
    metadata_en: Optional[CeVIOMetadataEN] = field(
        default=None,
        metadata={
            "name": "Metadata_EN",
            "type": "Element",
        },
    )
    direction: Optional[CeVIODirection] = field(
        default=None,
        metadata={
            "name": "Direction",
            "type": "Element",
            "required": True,
        },
    )
    phonemes: Optional[CeVIOPhonemes] = field(
        default=None,
        metadata={
            "name": "Phonemes",
            "type": "Element",
            "required": True,
        },
    )


@dataclass
class CeVIOAudioUnit(CeVIOBaseUnit):
    file_path: Optional[str] = field(
        default=None,
        metadata={
            "name": "FilePath",
            "type": "Attribute",
        },
    )


@dataclass
class CeVIOUnit(CeVIOSongUnit, CeVIOTalkUnit, CeVIOAudioUnit):
    class Meta:
        name = "Unit"


@dataclass
class CeVIOUnits:
    class Meta:
        name = "Units"

    unit: list[CeVIOUnit] = field(
        default_factory=list,
        metadata={
            "name": "Unit",
            "type": "Element",
        },
    )


@dataclass
class CeVIOScene:
    class Meta:
        name = "Scene"

    scene_id: Optional[str] = field(
        default="",
        metadata={
            "name": "Id",
            "type": "Attribute",
        },
    )
    timeline: Optional[CeVIOTimeline] = field(
        default=None,
        metadata={
            "name": "Timeline",
            "type": "Element",
        },
    )
    talk_editor: Optional[CeVIOTalkEditor] = field(
        default=None,
        metadata={
            "name": "TalkEditor",
            "type": "Element",
        },
    )
    song_editor: Optional[CeVIOSongEditor] = field(
        default=None,
        metadata={
            "name": "SongEditor",
            "type": "Element",
        },
    )
    units: Optional[CeVIOUnits] = field(
        default_factory=CeVIOUnits,
        metadata={
            "name": "Units",
            "type": "Element",
        },
    )
    groups: Optional[CeVIOGroups] = field(
        default_factory=CeVIOGroups,
        metadata={
            "name": "Groups",
            "type": "Element",
        },
    )
    sound_setting: Optional[CeVIOSoundSetting] = field(
        default_factory=CeVIOSoundSetting,
        metadata={
            "name": "SoundSetting",
            "type": "Element",
        },
    )


@dataclass
class CeVIOSequence:
    class Meta:
        name = "Sequence"

    sequence_id: Optional[str] = field(
        default="",
        metadata={
            "name": "Id",
            "type": "Attribute",
        },
    )
    scene: Optional[CeVIOScene] = field(
        default_factory=CeVIOScene,
        metadata={
            "name": "Scene",
            "type": "Element",
        },
    )


@dataclass
class CeVIOCreativeStudioProject:
    class Meta:
        name = "Scenario"

    code: Optional[str] = field(
        default="7251BC4B6168E7B2992FA620BD3E1E77",
        metadata={
            "name": "Code",
            "type": "Attribute",
        },
    )
    generation: Optional[CeVIOGeneration] = field(
        default_factory=CeVIOGeneration,
        metadata={
            "name": "Generation",
            "type": "Element",
        },
    )
    sequence: Optional[CeVIOSequence] = field(
        default_factory=CeVIOSequence,
        metadata={
            "name": "Sequence",
            "type": "Element",
        },
    )
