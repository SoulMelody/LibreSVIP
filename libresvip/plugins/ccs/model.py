from dataclasses import field
from decimal import Decimal
from typing import List, Optional, Union

from pydantic.dataclasses import dataclass
from xsdata.models.datatype import XmlTime


@dataclass
class Author:
    version: Optional[str] = field(
        default=None,
        metadata={
            "name": "Version",
            "type": "Attribute",
        }
    )


@dataclass
class Data:
    index: Optional[int] = field(
        default=None,
        metadata={
            "name": "Index",
            "type": "Attribute",
        }
    )
    repeat: Optional[int] = field(
        default=None,
        metadata={
            "name": "Repeat",
            "type": "Attribute",
        }
    )
    value: Optional[Union[float, int, Decimal]] = field(
        default=None
    )


@dataclass
class Dictionary:
    version: Optional[str] = field(
        default=None,
        metadata={
            "name": "Version",
            "type": "Attribute",
        }
    )


@dataclass
class Dynamics:
    clock: Optional[int] = field(
        default=None,
        metadata={
            "name": "Clock",
            "type": "Attribute",
        }
    )
    value: Optional[int] = field(
        default=None,
        metadata={
            "name": "Value",
            "type": "Attribute",
        }
    )


@dataclass
class Extension:
    vertical_ratio: Optional[str] = field(
        default=None,
        metadata={
            "name": "VerticalRatio",
            "type": "Attribute",
        }
    )


@dataclass
class Group:
    version: Optional[float] = field(
        default=None,
        metadata={
            "name": "Version",
            "type": "Attribute",
        }
    )
    id: Optional[str] = field(
        default=None,
        metadata={
            "name": "Id",
            "type": "Attribute",
        }
    )
    category: Optional[str] = field(
        default=None,
        metadata={
            "name": "Category",
            "type": "Attribute",
        }
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "name": "Name",
            "type": "Attribute",
        }
    )
    color: Optional[str] = field(
        default=None,
        metadata={
            "name": "Color",
            "type": "Attribute",
        }
    )
    volume: Optional[float] = field(
        default=None,
        metadata={
            "name": "Volume",
            "type": "Attribute",
        }
    )
    pan: Optional[int] = field(
        default=None,
        metadata={
            "name": "Pan",
            "type": "Attribute",
        }
    )
    is_solo: Optional[bool] = field(
        default=None,
        metadata={
            "name": "IsSolo",
            "type": "Attribute",
        }
    )
    is_muted: Optional[bool] = field(
        default=None,
        metadata={
            "name": "IsMuted",
            "type": "Attribute",
        }
    )
    cast_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "CastId",
            "type": "Attribute",
        }
    )
    language: Optional[str] = field(
        default=None,
        metadata={
            "name": "Language",
            "type": "Attribute",
        }
    )


@dataclass
class Key:
    clock: Optional[int] = field(
        default=None,
        metadata={
            "name": "Clock",
            "type": "Attribute",
        }
    )
    fifths: Optional[int] = field(
        default=None,
        metadata={
            "name": "Fifths",
            "type": "Attribute",
        }
    )
    mode: Optional[int] = field(
        default=None,
        metadata={
            "name": "Mode",
            "type": "Attribute",
        }
    )


@dataclass
class Note:
    clock: Optional[int] = field(
        default=None,
        metadata={
            "name": "Clock",
            "type": "Attribute",
        }
    )
    pitch_step: Optional[int] = field(
        default=None,
        metadata={
            "name": "PitchStep",
            "type": "Attribute",
        }
    )
    pitch_octave: Optional[int] = field(
        default=None,
        metadata={
            "name": "PitchOctave",
            "type": "Attribute",
        }
    )
    duration: Optional[int] = field(
        default=None,
        metadata={
            "name": "Duration",
            "type": "Attribute",
        }
    )
    lyric: Optional[str] = field(
        default=None,
        metadata={
            "name": "Lyric",
            "type": "Attribute",
        }
    )
    phonetic: Optional[str] = field(
        default=None,
        metadata={
            "name": "Phonetic",
            "type": "Attribute",
        }
    )
    do_re_mi: Optional[bool] = field(
        default=None,
        metadata={
            "name": "DoReMi",
            "type": "Attribute",
        }
    )


@dataclass
class ReferenceState:
    current: Optional[str] = field(
        default=None,
        metadata={
            "name": "Current",
            "type": "Attribute",
        }
    )
    previous: Optional[str] = field(
        default=None,
        metadata={
            "name": "Previous",
            "type": "Attribute",
        }
    )


@dataclass
class Sound:
    clock: Optional[int] = field(
        default=None,
        metadata={
            "name": "Clock",
            "type": "Attribute",
        }
    )
    tempo: Optional[int] = field(
        default=None,
        metadata={
            "name": "Tempo",
            "type": "Attribute",
        }
    )


@dataclass
class SoundSetting:
    rhythm: Optional[str] = field(
        default=None,
        metadata={
            "name": "Rhythm",
            "type": "Attribute",
        }
    )
    tempo: Optional[float] = field(
        default=120.0,
        metadata={
            "name": "Tempo",
            "type": "Attribute",
        }
    )
    master_volume: Optional[float] = field(
        default=None,
        metadata={
            "name": "MasterVolume",
            "type": "Attribute",
        }
    )


@dataclass
class SoundSource:
    version: Optional[str] = field(
        default=None,
        metadata={
            "name": "Version",
            "type": "Attribute",
        }
    )
    id: Optional[str] = field(
        default=None,
        metadata={
            "name": "Id",
            "type": "Attribute",
        }
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "name": "Name",
            "type": "Attribute",
        }
    )


@dataclass
class Time:
    clock: Optional[int] = field(
        default=None,
        metadata={
            "name": "Clock",
            "type": "Attribute",
        }
    )
    beats: Optional[int] = field(
        default=None,
        metadata={
            "name": "Beats",
            "type": "Attribute",
        }
    )
    beat_type: Optional[int] = field(
        default=None,
        metadata={
            "name": "BeatType",
            "type": "Attribute",
        }
    )


@dataclass
class ViewScale:
    horizontal: Optional[Union[int, float]] = field(
        default=None,
        metadata={
            "name": "Horizontal",
            "type": "Attribute",
        }
    )
    vertical: Optional[Union[int, Decimal]] = field(
        default=None,
        metadata={
            "name": "Vertical",
            "type": "Attribute",
        }
    )


@dataclass
class Beat:
    time: Optional[Time] = field(
        default=None,
        metadata={
            "name": "Time",
            "type": "Element",
        }
    )


@dataclass
class C0:
    length: Optional[int] = field(
        default=None,
        metadata={
            "name": "Length",
            "type": "Attribute",
        }
    )
    data: List[Union[Data, float, Decimal]] = field(
        default_factory=list,
        metadata={
            "name": "Data",
            "type": "Element",
        }
    )


@dataclass
class Groups:
    active_group: Optional[str] = field(
        default=None,
        metadata={
            "name": "ActiveGroup",
            "type": "Attribute",
        }
    )
    group: List[Group] = field(
        default_factory=list,
        metadata={
            "name": "Group",
            "type": "Element",
        }
    )


@dataclass
class LogF0:
    length: Optional[int] = field(
        default=None,
        metadata={
            "name": "Length",
            "type": "Attribute",
        }
    )
    data: List[Union[Data, Decimal, float]] = field(
        default_factory=list,
        metadata={
            "name": "Data",
            "type": "Element",
        }
    )


@dataclass
class Score:
    alpha: Optional[float] = field(
        default=None,
        metadata={
            "name": "Alpha",
            "type": "Attribute",
        }
    )
    emotion0: Optional[Union[float, int]] = field(
        default=None,
        metadata={
            "name": "Emotion0",
            "type": "Attribute",
        }
    )
    emotion1: Optional[Union[float, int]] = field(
        default=None,
        metadata={
            "name": "Emotion1",
            "type": "Attribute",
        }
    )
    key: Optional[Key] = field(
        default=None,
        metadata={
            "name": "Key",
            "type": "Element",
        }
    )
    dynamics: List[Dynamics] = field(
        default_factory=list,
        metadata={
            "name": "Dynamics",
            "type": "Element",
            "sequential": True,
        }
    )
    note: List[Note] = field(
        default_factory=list,
        metadata={
            "name": "Note",
            "type": "Element",
            "sequential": True,
        }
    )


@dataclass
class SongEditor:
    partition: Optional[int] = field(
        default=None,
        metadata={
            "name": "Partition",
            "type": "Attribute",
        }
    )
    quantize: Optional[int] = field(
        default=None,
        metadata={
            "name": "Quantize",
            "type": "Attribute",
        }
    )
    mode: Optional[int] = field(
        default=None,
        metadata={
            "name": "Mode",
            "type": "Attribute",
        }
    )
    editing_tool: Optional[int] = field(
        default=None,
        metadata={
            "name": "EditingTool",
            "type": "Attribute",
        }
    )
    view_scale: Optional[ViewScale] = field(
        default=None,
        metadata={
            "name": "ViewScale",
            "type": "Element",
        }
    )
    reference_state: Optional[ReferenceState] = field(
        default=None,
        metadata={
            "name": "ReferenceState",
            "type": "Element",
        }
    )


@dataclass
class SoundSources:
    sound_source: Optional[SoundSource] = field(
        default=None,
        metadata={
            "name": "SoundSource",
            "type": "Element",
        }
    )


@dataclass
class Tts:
    class Meta:
        name = "TTS"

    version: Optional[str] = field(
        default=None,
        metadata={
            "name": "Version",
            "type": "Attribute",
        }
    )
    dictionary: Optional[Dictionary] = field(
        default=None,
        metadata={
            "name": "Dictionary",
            "type": "Element",
        }
    )
    sound_sources: Optional[object] = field(
        default=None,
        metadata={
            "name": "SoundSources",
            "type": "Element",
        }
    )


@dataclass
class TalkEditor:
    partition: Optional[int] = field(
        default=None,
        metadata={
            "name": "Partition",
            "type": "Attribute",
        }
    )
    extension: Optional[Extension] = field(
        default=None,
        metadata={
            "name": "Extension",
            "type": "Element",
        }
    )


@dataclass
class Tempo:
    sound: List[Sound] = field(
        default_factory=list,
        metadata={
            "name": "Sound",
            "type": "Element",
        }
    )


@dataclass
class Timeline:
    partition: Optional[str] = field(
        default=None,
        metadata={
            "name": "Partition",
            "type": "Attribute",
        }
    )
    current_position: Optional[XmlTime] = field(
        default=None,
        metadata={
            "name": "CurrentPosition",
            "type": "Attribute",
        }
    )
    view_scale: Optional[ViewScale] = field(
        default=None,
        metadata={
            "name": "ViewScale",
            "type": "Element",
        }
    )


@dataclass
class Timing:
    length: Optional[int] = field(
        default=None,
        metadata={
            "name": "Length",
            "type": "Attribute",
        }
    )
    data: List[Union[Data, Decimal, float]] = field(
        default_factory=list,
        metadata={
            "name": "Data",
            "type": "Element",
        }
    )


@dataclass
class VibAmp:
    length: Optional[int] = field(
        default=None,
        metadata={
            "name": "Length",
            "type": "Attribute",
        }
    )
    data: List[Union[Data, float, Decimal, int]] = field(
        default_factory=list,
        metadata={
            "name": "Data",
            "type": "Element",
        }
    )


@dataclass
class VibFrq:
    length: Optional[int] = field(
        default=None,
        metadata={
            "name": "Length",
            "type": "Attribute",
        }
    )
    data: List[Union[Data, float, Decimal]] = field(
        default_factory=list,
        metadata={
            "name": "Data",
            "type": "Element",
        }
    )


@dataclass
class Parameter:
    timing: Optional[Timing] = field(
        default=None,
        metadata={
            "name": "Timing",
            "type": "Element",
        }
    )
    log_f0: Optional[LogF0] = field(
        default=None,
        metadata={
            "name": "LogF0",
            "type": "Element",
        }
    )
    c0: Optional[C0] = field(
        default=None,
        metadata={
            "name": "C0",
            "type": "Element",
        }
    )
    vib_amp: Optional[VibAmp] = field(
        default=None,
        metadata={
            "name": "VibAmp",
            "type": "Element",
        }
    )
    vib_frq: Optional[VibFrq] = field(
        default=None,
        metadata={
            "name": "VibFrq",
            "type": "Element",
        }
    )


@dataclass
class Svss:
    class Meta:
        name = "SVSS"

    version: Optional[str] = field(
        default=None,
        metadata={
            "name": "Version",
            "type": "Attribute",
        }
    )
    dictionary: Optional[Dictionary] = field(
        default=None,
        metadata={
            "name": "Dictionary",
            "type": "Element",
        }
    )
    sound_sources: Optional[SoundSources] = field(
        default=None,
        metadata={
            "name": "SoundSources",
            "type": "Element",
        }
    )


@dataclass
class Generation:
    author: Optional[Author] = field(
        default=None,
        metadata={
            "name": "Author",
            "type": "Element",
        }
    )
    tts: Optional[Tts] = field(
        default=None,
        metadata={
            "name": "TTS",
            "type": "Element",
        }
    )
    svss: Optional[Svss] = field(
        default=None,
        metadata={
            "name": "SVSS",
            "type": "Element",
        }
    )


@dataclass
class Song:
    version: Optional[float] = field(
        default=None,
        metadata={
            "name": "Version",
            "type": "Attribute",
        }
    )
    tempo: Optional[Tempo] = field(
        default=None,
        metadata={
            "name": "Tempo",
            "type": "Element",
        }
    )
    beat: Optional[Beat] = field(
        default=None,
        metadata={
            "name": "Beat",
            "type": "Element",
        }
    )
    score: Optional[Score] = field(
        default=None,
        metadata={
            "name": "Score",
            "type": "Element",
        }
    )
    parameter: Optional[Parameter] = field(
        default=None,
        metadata={
            "name": "Parameter",
            "type": "Element",
        }
    )


@dataclass
class Unit:
    version: Optional[float] = field(
        default=None,
        metadata={
            "name": "Version",
            "type": "Attribute",
        }
    )
    id: Optional[object] = field(
        default=None,
        metadata={
            "name": "Id",
            "type": "Attribute",
        }
    )
    category: Optional[str] = field(
        default=None,
        metadata={
            "name": "Category",
            "type": "Attribute",
        }
    )
    group: Optional[str] = field(
        default=None,
        metadata={
            "name": "Group",
            "type": "Attribute",
        }
    )
    start_time: Optional[XmlTime] = field(
        default=None,
        metadata={
            "name": "StartTime",
            "type": "Attribute",
        }
    )
    duration: Optional[XmlTime] = field(
        default=None,
        metadata={
            "name": "Duration",
            "type": "Attribute",
        }
    )
    cast_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "CastId",
            "type": "Attribute",
        }
    )
    language: Optional[str] = field(
        default=None,
        metadata={
            "name": "Language",
            "type": "Attribute",
        }
    )
    song: Optional[Song] = field(
        default=None,
        metadata={
            "name": "Song",
            "type": "Element",
        }
    )
    file_path: Optional[str] = field(
        default=None,
        metadata={
            "name": "FilePath",
            "type": "Attribute",
        }
    )


@dataclass
class Units:
    unit: List[Unit] = field(
        default_factory=list,
        metadata={
            "name": "Unit",
            "type": "Element",
        }
    )


@dataclass
class Scene:
    id: Optional[object] = field(
        default=None,
        metadata={
            "name": "Id",
            "type": "Attribute",
        }
    )
    timeline: Optional[Timeline] = field(
        default=None,
        metadata={
            "name": "Timeline",
            "type": "Element",
        }
    )
    talk_editor: Optional[TalkEditor] = field(
        default=None,
        metadata={
            "name": "TalkEditor",
            "type": "Element",
        }
    )
    song_editor: Optional[SongEditor] = field(
        default=None,
        metadata={
            "name": "SongEditor",
            "type": "Element",
        }
    )
    units: Optional[Units] = field(
        default=None,
        metadata={
            "name": "Units",
            "type": "Element",
        }
    )
    groups: Optional[Groups] = field(
        default=None,
        metadata={
            "name": "Groups",
            "type": "Element",
        }
    )
    sound_setting: Optional[SoundSetting] = field(
        default=None,
        metadata={
            "name": "SoundSetting",
            "type": "Element",
        }
    )


@dataclass
class Sequence:
    id: Optional[object] = field(
        default=None,
        metadata={
            "name": "Id",
            "type": "Attribute",
        }
    )
    scene: Optional[Scene] = field(
        default=None,
        metadata={
            "name": "Scene",
            "type": "Element",
        }
    )


@dataclass
class CeVIOCreativeStudioProject:
    code: Optional[str] = field(
        default=None,
        metadata={
            "name": "Code",
            "type": "Attribute",
        },
    )
    generation: Optional[Generation] = field(
        default=None,
        metadata={
            "name": "Generation",
            "type": "Element",
        },
    )
    sequence: Optional[Sequence] = field(
        default=None,
        metadata={
            "name": "Sequence",
            "type": "Element",
        },
    )
