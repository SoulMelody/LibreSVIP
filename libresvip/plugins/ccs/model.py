from decimal import Decimal

from xsdata.models.datatype import XmlTime
from xsdata_pydantic.fields import field

from libresvip.model.base import BaseModel


class CeVIOAuthor(BaseModel):
    class Meta:
        name = "Author"

    version: str | None = field(
        default="3.2.21.2",
        metadata={
            "name": "Version",
            "type": "Attribute",
        },
    )


class CeVIONoData(BaseModel):
    class Meta:
        name = "NoData"

    index: int | None = field(
        default=None,
        metadata={
            "name": "Index",
            "type": "Attribute",
        },
    )
    repeat: int | None = field(
        default=None,
        metadata={
            "name": "Repeat",
            "type": "Attribute",
        },
    )


class CeVIOData(CeVIONoData):
    class Meta:
        name = "Data"

    value: float | int | Decimal | None = field(default=None)


class CeVIODictExtension(BaseModel):
    class Meta:
        name = "Extension"

    version: str | None = field(
        default="1.0.0",
        metadata={
            "name": "Version",
            "type": "Attribute",
        },
    )

    language: str | None = field(
        default="English",
        metadata={
            "name": "Language",
            "type": "Attribute",
        },
    )


class CeVIODictionary(BaseModel):
    class Meta:
        name = "Dictionary"

    version: str | None = field(
        default="1.0.0",
        metadata={
            "name": "Version",
            "type": "Attribute",
        },
    )
    extension: CeVIODictExtension | None = field(
        default=None,
        metadata={
            "name": "Extension",
            "type": "Element",
        },
    )


class CeVIODynamics(BaseModel):
    class Meta:
        name = "Dynamics"

    clock: int | None = field(
        default=None,
        metadata={
            "name": "Clock",
            "type": "Attribute",
        },
    )
    value: int | None = field(
        default=None,
        metadata={
            "name": "Value",
            "type": "Attribute",
        },
    )


class CeVIOTalkExtension(BaseModel):
    class Meta:
        name = "Extension"

    vertical_ratio: str | None = field(
        default=None,
        metadata={
            "name": "VerticalRatio",
            "type": "Attribute",
        },
    )


class CeVIOGroup(BaseModel):
    class Meta:
        name = "Group"

    version: str | None = field(
        default="1.0",
        metadata={
            "name": "Version",
            "type": "Attribute",
        },
    )
    group_id: str | None = field(
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
    name: str | None = field(
        default=None,
        metadata={
            "name": "Name",
            "type": "Attribute",
        },
    )
    color: str | None = field(
        default=None,
        metadata={
            "name": "Color",
            "type": "Attribute",
        },
    )
    volume: float | None = field(
        default=None,
        metadata={
            "name": "Volume",
            "type": "Attribute",
        },
    )
    pan: float | None = field(
        default=None,
        metadata={
            "name": "Pan",
            "type": "Attribute",
        },
    )
    is_solo: bool | None = field(
        default=False,
        metadata={
            "name": "IsSolo",
            "type": "Attribute",
        },
    )
    is_muted: bool | None = field(
        default=False,
        metadata={
            "name": "IsMuted",
            "type": "Attribute",
        },
    )
    cast_id: str | None = field(
        default=None,
        metadata={
            "name": "CastId",
            "type": "Attribute",
        },
    )
    language: str | None = field(
        default="Japanese",
        metadata={
            "name": "Language",
            "type": "Attribute",
        },
    )
    snapshot: str | None = field(
        default=None,
        metadata={
            "name": "SnapShot",
            "type": "Attribute",
        },
    )


class CeVIOKey(BaseModel):
    class Meta:
        name = "Key"

    clock: int | None = field(
        default=None,
        metadata={
            "name": "Clock",
            "type": "Attribute",
        },
    )
    fifths: int | None = field(
        default=None,
        metadata={
            "name": "Fifths",
            "type": "Attribute",
        },
    )
    mode: int | None = field(
        default=None,
        metadata={
            "name": "Mode",
            "type": "Attribute",
        },
    )


class CeVIONote(BaseModel):
    class Meta:
        name = "Note"

    clock: int | None = field(
        default=None,
        metadata={
            "name": "Clock",
            "type": "Attribute",
        },
    )
    pitch_step: int | None = field(
        default=None,
        metadata={
            "name": "PitchStep",
            "type": "Attribute",
        },
    )
    pitch_octave: int | None = field(
        default=None,
        metadata={
            "name": "PitchOctave",
            "type": "Attribute",
        },
    )
    duration: int | None = field(
        default=None,
        metadata={
            "name": "Duration",
            "type": "Attribute",
        },
    )
    lyric: str | None = field(
        default=None,
        metadata={
            "name": "Lyric",
            "type": "Attribute",
        },
    )
    phonetic: str | None = field(
        default=None,
        metadata={
            "name": "Phonetic",
            "type": "Attribute",
        },
    )
    do_re_mi: bool | None = field(
        default=None,
        metadata={
            "name": "DoReMi",
            "type": "Attribute",
        },
    )
    staccato: bool | None = field(
        default=None,
        metadata={
            "name": "Staccato",
            "type": "Attribute",
        },
    )
    slur_start: bool | None = field(
        default=None,
        metadata={
            "name": "SlurStart",
            "type": "Attribute",
        },
    )
    slur_stop: bool | None = field(
        default=None,
        metadata={
            "name": "SlurStop",
            "type": "Attribute",
        },
    )
    syllabic: int | None = field(
        default=None,
        metadata={
            "name": "Syllabic",
            "type": "Attribute",
        },
    )
    accent: bool | None = field(
        default=None,
        metadata={
            "name": "Accent",
            "type": "Attribute",
        },
    )
    breath: bool | None = field(
        default=None,
        metadata={
            "name": "Breath",
            "type": "Attribute",
        },
    )


class CeVIOReferenceState(BaseModel):
    class Meta:
        name = "ReferenceState"

    current: str | None = field(
        default=None,
        metadata={
            "name": "Current",
            "type": "Attribute",
        },
    )
    previous: str | None = field(
        default=None,
        metadata={
            "name": "Previous",
            "type": "Attribute",
        },
    )


class CeVIOSound(BaseModel):
    class Meta:
        name = "Sound"

    clock: int | None = field(
        default=None,
        metadata={
            "name": "Clock",
            "type": "Attribute",
        },
    )
    tempo: float | None = field(
        default=None,
        metadata={
            "name": "Tempo",
            "type": "Attribute",
        },
    )


class CeVIOSoundSetting(BaseModel):
    class Meta:
        name = "SoundSetting"

    rhythm: str | None = field(
        default="4/4",
        metadata={
            "name": "Rhythm",
            "type": "Attribute",
        },
    )
    tempo: float | None = field(
        default=120.0,
        metadata={
            "name": "Tempo",
            "type": "Attribute",
        },
    )
    master_volume: float | None = field(
        default=None,
        metadata={
            "name": "MasterVolume",
            "type": "Attribute",
        },
    )


class CeVIOSoundSource(BaseModel):
    class Meta:
        name = "SoundSource"

    version: str | None = field(
        default="1.0.0",
        metadata={
            "name": "Version",
            "type": "Attribute",
        },
    )
    sound_source_id: str | None = field(
        default=None,
        metadata={
            "name": "Id",
            "type": "Attribute",
        },
    )
    name: str | None = field(
        default=None,
        metadata={
            "name": "Name",
            "type": "Attribute",
        },
    )


class CeVIOTime(BaseModel):
    class Meta:
        name = "Time"

    clock: int = field(
        metadata={
            "name": "Clock",
            "type": "Attribute",
        },
    )
    beats: int | None = field(
        default=None,
        metadata={
            "name": "Beats",
            "type": "Attribute",
        },
    )
    beat_type: int | None = field(
        default=None,
        metadata={
            "name": "BeatType",
            "type": "Attribute",
        },
    )


class CeVIOViewScale(BaseModel):
    class Meta:
        name = "ViewScale"

    horizontal: int | float | None = field(
        default=None,
        metadata={
            "name": "Horizontal",
            "type": "Attribute",
        },
    )
    vertical: int | Decimal | None = field(
        default=None,
        metadata={
            "name": "Vertical",
            "type": "Attribute",
        },
    )


class CeVIOBeat(BaseModel):
    class Meta:
        name = "Beat"

    time: list[CeVIOTime] = field(
        default_factory=list,
        metadata={
            "name": "Time",
            "type": "Element",
        },
    )


class CeVIOGroups(BaseModel):
    class Meta:
        name = "Groups"

    active_group: str | None = field(
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


class CeVIOScore(BaseModel):
    class Meta:
        name = "Score"

    alpha: float | None = field(
        default=None,
        metadata={
            "name": "Alpha",
            "type": "Attribute",
        },
    )
    tune: float | None = field(
        default=None,
        metadata={
            "name": "Tune",
            "type": "Attribute",
        },
    )
    pitch_shift: float | None = field(
        default=None,
        metadata={
            "name": "PitchShift",
            "type": "Attribute",
        },
    )
    pitch_tune: float | None = field(
        default=None,
        metadata={
            "name": "PitchTune",
            "type": "Attribute",
        },
    )
    husky: float | None = field(
        default=None,
        metadata={
            "name": "Husky",
            "type": "Attribute",
        },
    )
    vib_amp: float | None = field(
        default=None,
        metadata={
            "name": "VibAmp",
            "type": "Attribute",
        },
    )
    vib_frq: float | None = field(
        default=None,
        metadata={
            "name": "VibFrq",
            "type": "Attribute",
        },
    )
    emotion0: float | int | None = field(
        default=None,
        metadata={
            "name": "Emotion0",
            "type": "Attribute",
        },
    )
    emotion1: float | int | None = field(
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


class CeVIOSongEditor(BaseModel):
    class Meta:
        name = "SongEditor"

    partition: int | None = field(
        default=None,
        metadata={
            "name": "Partition",
            "type": "Attribute",
        },
    )
    quantize: int | None = field(
        default=None,
        metadata={
            "name": "Quantize",
            "type": "Attribute",
        },
    )
    mode: int | None = field(
        default=None,
        metadata={
            "name": "Mode",
            "type": "Attribute",
        },
    )
    editing_tool: int | None = field(
        default=None,
        metadata={
            "name": "EditingTool",
            "type": "Attribute",
        },
    )
    view_scale: CeVIOViewScale | None = field(
        default=None,
        metadata={
            "name": "ViewScale",
            "type": "Element",
        },
    )
    reference_state: CeVIOReferenceState | None = field(
        default=None,
        metadata={
            "name": "ReferenceState",
            "type": "Element",
        },
    )


class CeVIOSoundSources(BaseModel):
    class Meta:
        name = "SoundSources"

    sound_source: list[CeVIOSoundSource] = field(
        default_factory=list,
        metadata={
            "name": "SoundSource",
            "type": "Element",
        },
    )


class CeVIOTts(BaseModel):
    class Meta:
        name = "TTS"

    version: str | None = field(
        default="3.1.0",
        metadata={
            "name": "Version",
            "type": "Attribute",
        },
    )
    dictionary: CeVIODictionary | None = field(
        default_factory=CeVIODictionary,
        metadata={
            "name": "Dictionary",
            "type": "Element",
        },
    )
    sound_sources: CeVIOSoundSources = field(
        default_factory=CeVIOSoundSources,
        metadata={
            "name": "SoundSources",
            "type": "Element",
        },
    )


class CeVIOTalkEditor(BaseModel):
    class Meta:
        name = "TalkEditor"

    partition: int | None = field(
        default=None,
        metadata={
            "name": "Partition",
            "type": "Attribute",
        },
    )
    extension: CeVIOTalkExtension | None = field(
        default=None,
        metadata={
            "name": "Extension",
            "type": "Element",
        },
    )


class CeVIOTempo(BaseModel):
    class Meta:
        name = "Tempo"

    sound: list[CeVIOSound] = field(
        default_factory=list,
        metadata={
            "name": "Sound",
            "type": "Element",
        },
    )


class CeVIOTimeline(BaseModel):
    class Meta:
        name = "Timeline"

    partition: str | None = field(
        default=None,
        metadata={
            "name": "Partition",
            "type": "Attribute",
        },
    )
    current_position: XmlTime | None = field(
        default=None,
        metadata={
            "name": "CurrentPosition",
            "type": "Attribute",
        },
    )
    start_position: XmlTime | None = field(
        default=None,
        metadata={
            "name": "StartPosition",
            "type": "Attribute",
        },
    )
    end_position: XmlTime | None = field(
        default=None,
        metadata={
            "name": "EndPosition",
            "type": "Attribute",
        },
    )
    view_scale: CeVIOViewScale | None = field(
        default=None,
        metadata={
            "name": "ViewScale",
            "type": "Element",
        },
    )


class CeVIOParameter(BaseModel):
    class Meta:
        name = "Parameter"

    length: int | None = field(
        default=None,
        metadata={
            "name": "Length",
            "type": "Attribute",
        },
    )
    data: list[CeVIOData | float | Decimal | int] = field(
        default_factory=list,
        metadata={
            "name": "Data",
            "type": "Element",
        },
    )
    no_data: list[CeVIONoData] = field(
        default_factory=list,
        metadata={
            "name": "NoData",
            "type": "Element",
        },
    )


class CeVIOParameters(BaseModel):
    class Meta:
        name = "Parameters"

    timing: CeVIOParameter | None = field(
        default=None,
        metadata={
            "name": "Timing",
            "type": "Element",
        },
    )
    log_f0: CeVIOParameter | None = field(
        default=None,
        metadata={
            "name": "LogF0",
            "type": "Element",
        },
    )
    c0: CeVIOParameter | None = field(
        default=None,
        metadata={
            "name": "C0",
            "type": "Element",
        },
    )
    vib_amp: CeVIOParameter | None = field(
        default=None,
        metadata={
            "name": "VibAmp",
            "type": "Element",
        },
    )
    vib_frq: CeVIOParameter | None = field(
        default=None,
        metadata={
            "name": "VibFrq",
            "type": "Element",
        },
    )
    alpha: CeVIOParameter | None = field(
        default=None,
        metadata={
            "name": "Alpha",
            "type": "Element",
        },
    )
    husky: CeVIOParameter | None = field(
        default=None,
        metadata={
            "name": "Husky",
            "type": "Element",
        },
    )


class CeVIOSvss(BaseModel):
    class Meta:
        name = "SVSS"

    version: str | None = field(
        default="3.0.5",
        metadata={
            "name": "Version",
            "type": "Attribute",
        },
    )
    dictionary: CeVIODictionary | None = field(
        default_factory=CeVIODictionary,
        metadata={
            "name": "Dictionary",
            "type": "Element",
        },
    )
    sound_sources: CeVIOSoundSources = field(
        default_factory=CeVIOSoundSources,
        metadata={
            "name": "SoundSources",
            "type": "Element",
        },
    )


class CeVIOGeneration(BaseModel):
    class Meta:
        name = "Generation"

    author: CeVIOAuthor | None = field(
        default_factory=CeVIOAuthor,
        metadata={
            "name": "Author",
            "type": "Element",
        },
    )
    tts: CeVIOTts | None = field(
        default_factory=CeVIOTts,
        metadata={
            "name": "TTS",
            "type": "Element",
        },
    )
    svss: CeVIOSvss = field(
        default_factory=CeVIOSvss,
        metadata={
            "name": "SVSS",
            "type": "Element",
        },
    )


class CeVIOSong(BaseModel):
    class Meta:
        name = "Song"

    version: str | None = field(
        default="1.02",
        metadata={
            "name": "Version",
            "type": "Attribute",
        },
    )
    common_keys: bool | None = field(
        default=None,
        metadata={
            "name": "CommonKeys",
            "type": "Attribute",
        },
    )
    tempo: CeVIOTempo | None = field(
        default=None,
        metadata={
            "name": "Tempo",
            "type": "Element",
        },
    )
    beat: CeVIOBeat | None = field(
        default=None,
        metadata={
            "name": "Beat",
            "type": "Element",
        },
    )
    score: CeVIOScore = field(
        default_factory=CeVIOScore,
        metadata={
            "name": "Score",
            "type": "Element",
        },
    )
    parameter: CeVIOParameters = field(
        default_factory=CeVIOParameters,
        metadata={
            "name": "Parameter",
            "type": "Element",
        },
    )


class CeVIOBaseUnit(BaseModel):
    version: str | None = field(
        default="1.0",
        metadata={
            "name": "Version",
            "type": "Attribute",
        },
    )
    unit_id: str | None = field(
        default="",
        metadata={
            "name": "Id",
            "type": "Attribute",
        },
    )
    group: str | None = field(
        default=None,
        metadata={
            "name": "Group",
            "type": "Attribute",
        },
    )
    start_time: XmlTime | None = field(
        default=None,
        metadata={
            "name": "StartTime",
            "type": "Attribute",
        },
    )
    duration: XmlTime | None = field(
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
    text: str | None = field(
        default=None,
        metadata={
            "name": "Text",
            "type": "Attribute",
        },
    )
    snap_shot: str | None = field(
        default=None,
        metadata={
            "name": "SnapShot",
            "type": "Attribute",
        },
    )


class CeVIOSongUnit(CeVIOBaseUnit):
    song: CeVIOSong = field(
        default_factory=CeVIOSong,
        metadata={
            "name": "Song",
            "type": "Element",
        },
    )
    cast_id: str | None = field(
        default=None,
        metadata={
            "name": "CastId",
            "type": "Attribute",
        },
    )
    language: str | None = field(
        default="Japanese",
        metadata={
            "name": "Language",
            "type": "Attribute",
        },
    )


class CeVIOComponent(BaseModel):
    class Meta:
        name = "Component"

    name: str | None = field(
        default=None,
        metadata={
            "name": "Name",
            "type": "Attribute",
            "required": True,
        },
    )
    value: Decimal | None = field(
        default=None,
        metadata={
            "name": "Value",
            "type": "Attribute",
            "required": True,
        },
    )


class CeVIOPhoneme(BaseModel):
    class Meta:
        name = "Phoneme"

    data: str | None = field(
        default=None,
        metadata={
            "name": "Data",
            "type": "Attribute",
            "required": True,
        },
    )
    volume: Decimal | float | None = field(
        default=None,
        metadata={
            "name": "Volume",
            "type": "Attribute",
        },
    )
    speed: float | Decimal | None = field(
        default=None,
        metadata={
            "name": "Speed",
            "type": "Attribute",
        },
    )
    tone: Decimal | float | None = field(
        default=None,
        metadata={
            "name": "Tone",
            "type": "Attribute",
        },
    )


class CeVIODirection(BaseModel):
    class Meta:
        name = "Direction"

    volume: float | None = field(
        default=None,
        metadata={
            "name": "Volume",
            "type": "Attribute",
            "required": True,
        },
    )
    speed: float | None = field(
        default=None,
        metadata={
            "name": "Speed",
            "type": "Attribute",
            "required": True,
        },
    )
    tone: float | None = field(
        default=None,
        metadata={
            "name": "Tone",
            "type": "Attribute",
            "required": True,
        },
    )
    alpha: float | None = field(
        default=None,
        metadata={
            "name": "Alpha",
            "type": "Attribute",
            "required": True,
        },
    )
    log_f0_scale: float | None = field(
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


class CeVIOPhonemes(BaseModel):
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


class Word(BaseModel):
    class Meta:
        name = "word"

    phoneme: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    pronunciation: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        },
    )
    pos: str | None = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    value: str = field(default="")


class AcousticPhrase(BaseModel):
    class Meta:
        name = "acoustic_phrase"

    word: list[Word] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )


class Base(BaseModel):
    acoustic_phrase: list[AcousticPhrase] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )


class Edited(BaseModel):
    acoustic_phrase: list[AcousticPhrase] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )


class CeVIOMetadataEN(BaseModel):
    class Meta:
        name = "Metadata_EN"

    base: Base | None = field(
        default=None,
        metadata={
            "name": "Base",
            "type": "Element",
            "required": True,
        },
    )
    edited: Edited | None = field(
        default=None,
        metadata={
            "name": "Edited",
            "type": "Element",
        },
    )


class CeVIOTalkUnit(CeVIOBaseUnit):
    metadata: str | None = field(
        default=None,
        metadata={
            "name": "Metadata",
            "type": "Element",
        },
    )
    metadata_en: CeVIOMetadataEN | None = field(
        default=None,
        metadata={
            "name": "Metadata_EN",
            "type": "Element",
        },
    )
    direction: CeVIODirection | None = field(
        default=None,
        metadata={
            "name": "Direction",
            "type": "Element",
            "required": True,
        },
    )
    phonemes: CeVIOPhonemes | None = field(
        default=None,
        metadata={
            "name": "Phonemes",
            "type": "Element",
            "required": True,
        },
    )


class CeVIOAudioUnit(CeVIOBaseUnit):
    file_path: str | None = field(
        default=None,
        metadata={
            "name": "FilePath",
            "type": "Attribute",
        },
    )


class CeVIOUnit(CeVIOSongUnit, CeVIOTalkUnit, CeVIOAudioUnit):
    class Meta:
        name = "Unit"


class CeVIOUnits(BaseModel):
    class Meta:
        name = "Units"

    unit: list[CeVIOUnit] = field(
        default_factory=list,
        metadata={
            "name": "Unit",
            "type": "Element",
        },
    )


class CeVIOScene(BaseModel):
    class Meta:
        name = "Scene"

    scene_id: str | None = field(
        default="",
        metadata={
            "name": "Id",
            "type": "Attribute",
        },
    )
    timeline: CeVIOTimeline | None = field(
        default=None,
        metadata={
            "name": "Timeline",
            "type": "Element",
        },
    )
    talk_editor: CeVIOTalkEditor | None = field(
        default=None,
        metadata={
            "name": "TalkEditor",
            "type": "Element",
        },
    )
    song_editor: CeVIOSongEditor | None = field(
        default=None,
        metadata={
            "name": "SongEditor",
            "type": "Element",
        },
    )
    units: CeVIOUnits = field(
        default_factory=CeVIOUnits,
        metadata={
            "name": "Units",
            "type": "Element",
        },
    )
    groups: CeVIOGroups = field(
        default_factory=CeVIOGroups,
        metadata={
            "name": "Groups",
            "type": "Element",
        },
    )
    sound_setting: CeVIOSoundSetting | None = field(
        default_factory=CeVIOSoundSetting,
        metadata={
            "name": "SoundSetting",
            "type": "Element",
        },
    )


class CeVIOSequence(BaseModel):
    class Meta:
        name = "Sequence"

    sequence_id: str | None = field(
        default="",
        metadata={
            "name": "Id",
            "type": "Attribute",
        },
    )
    scene: CeVIOScene = field(
        default_factory=CeVIOScene,
        metadata={
            "name": "Scene",
            "type": "Element",
        },
    )


class CeVIOCreativeStudioProject(BaseModel):
    class Meta:
        name = "Scenario"

    code: str | None = field(
        default="7251BC4B6168E7B2992FA620BD3E1E77",
        metadata={
            "name": "Code",
            "type": "Attribute",
        },
    )
    generation: CeVIOGeneration = field(
        default_factory=CeVIOGeneration,
        metadata={
            "name": "Generation",
            "type": "Element",
        },
    )
    sequence: CeVIOSequence = field(
        default_factory=CeVIOSequence,
        metadata={
            "name": "Sequence",
            "type": "Element",
        },
    )
