from pydantic import Field

from libresvip.model.base import BaseModel

from .models.vsqx3 import MasterTrack as Vsq3MasterTrack
from .models.vsqx3 import MCtrl as Vsq3MCtrl
from .models.vsqx3 import Mixer as Vsq3Mixer
from .models.vsqx3 import MonoTrack as Vsq3MonoTrack
from .models.vsqx3 import MonoUnit as Vsq3MonoUnit
from .models.vsqx3 import MusicalPart as Vsq3MusicalPart
from .models.vsqx3 import Note as Vsq3Note
from .models.vsqx3 import NoteStyle as Vsq3NoteStyle
from .models.vsqx3 import ParameterNames as Vsq3ParameterNames
from .models.vsqx3 import PartStyle as Vsq3PartStyle
from .models.vsqx3 import Singer as Vsq3Singer
from .models.vsqx3 import StereoTrack as Vsq3StereoTrack
from .models.vsqx3 import StereoUnit as Vsq3StereoUnit
from .models.vsqx3 import Tempo as Vsq3Tempo
from .models.vsqx3 import TimeSig as Vsq3TimeSig
from .models.vsqx3 import TypeParamAttr as Vsq3TypeParamAttr
from .models.vsqx3 import TypePhonemes as Vsq3TypePhonemes
from .models.vsqx3 import Vsq3
from .models.vsqx3 import VsTrack as Vsq3VsTrack
from .models.vsqx3 import VsUnit as Vsq3VsUnit
from .models.vsqx3 import VVoice as Vsq3VVoice
from .models.vsqx3 import VVoiceTable as Vsq3VVoiceTable
from .models.vsqx3 import WavPart as Vsq3WavPart
from .models.vsqx4 import MasterTrack as Vsq4MasterTrack
from .models.vsqx4 import MCtrl as Vsq4MCtrl
from .models.vsqx4 import Mixer as Vsq4Mixer
from .models.vsqx4 import MonoTrack as Vsq4MonoTrack
from .models.vsqx4 import MonoUnit as Vsq4MonoUnit
from .models.vsqx4 import MusicalPart as Vsq4MusicalPart
from .models.vsqx4 import Note as Vsq4Note
from .models.vsqx4 import NoteStyle as Vsq4NoteStyle
from .models.vsqx4 import ParameterNames as Vsq4ParameterNames
from .models.vsqx4 import PartStyle as Vsq4PartStyle
from .models.vsqx4 import Singer as Vsq4Singer
from .models.vsqx4 import StereoTrack as Vsq4StereoTrack
from .models.vsqx4 import StereoUnit as Vsq4StereoUnit
from .models.vsqx4 import Tempo as Vsq4Tempo
from .models.vsqx4 import TimeSig as Vsq4TimeSig
from .models.vsqx4 import TypeParamAttr as Vsq4TypeParamAttr
from .models.vsqx4 import TypePhonemes as Vsq4TypePhonemes
from .models.vsqx4 import Vsq4
from .models.vsqx4 import VsTrack as Vsq4VsTrack
from .models.vsqx4 import VsUnit as Vsq4VsUnit
from .models.vsqx4 import VVoice as Vsq4VVoice
from .models.vsqx4 import VVoiceTable as Vsq4VVoiceTable
from .models.vsqx4 import WavPart as Vsq4WavPart

Vsqx = Vsq3 | Vsq4
VsqxMasterTrack = Vsq3MasterTrack | Vsq4MasterTrack
VsqxMCtrl = Vsq3MCtrl | Vsq4MCtrl
VsqxMixer = Vsq3Mixer | Vsq4Mixer
VsqxMonoTrack = Vsq3MonoTrack | Vsq4MonoTrack
VsqxMusicalPart = Vsq3MusicalPart | Vsq4MusicalPart
VsqxNote = Vsq3Note | Vsq4Note
VsqxNoteStyle = Vsq3NoteStyle | Vsq4NoteStyle
VsqxParameterNames = Vsq3ParameterNames | Vsq4ParameterNames
VsqxPartStyle = Vsq3PartStyle | Vsq4PartStyle
VsqxTypePhonemes = Vsq3TypePhonemes | Vsq4TypePhonemes
VsqxSinger = Vsq3Singer | Vsq4Singer
VsqxStereoTrack = Vsq3StereoTrack | Vsq4StereoTrack
VsqxStereoUnitList = list[Vsq3StereoUnit] | list[Vsq4StereoUnit]
VsqxMonoUnitList = list[Vsq3MonoUnit] | list[Vsq4MonoUnit]
VsqxWavUnitList = VsqxStereoUnitList | VsqxMonoUnitList
VsqxTempoList = list[Vsq3Tempo] | list[Vsq4Tempo]
VsqxTimeSigList = list[Vsq3TimeSig] | list[Vsq4TimeSig]
VsqxTypeParamAttr = Vsq3TypeParamAttr | Vsq4TypeParamAttr
VsqxVsTrackList = list[Vsq3VsTrack] | list[Vsq4VsTrack]
VsqxVsUnitList = list[Vsq3VsUnit] | list[Vsq4VsUnit]
VsqxVVoice = Vsq3VVoice | Vsq4VVoice
VsqxVVoiceTable = Vsq3VVoiceTable | Vsq4VVoiceTable
VsqxWavPartList = list[Vsq3WavPart] | list[Vsq4WavPart]


class VocaloidStyleTypes(BaseModel):
    accent: int = 50
    bend_depth: int = Field(0, alias="bendDep")
    bend_length: int = Field(0, alias="bendLen")
    decay: int = 50
    fall_portamento: int = Field(0, alias="fallPort")
    opening: int = 127
    rise_portamento: int = Field(0, alias="risePort")
    vibrato_length: int = Field(0, alias="vibLen")
    vibrato_type: int = Field(0, alias="vibType")
    vibrato_depth: list[int] | None = Field(None, alias="vibDep")
    vibrato_rate: list[int] | None = Field(None, alias="vibRate")


__all__ = [
    "VocaloidStyleTypes",
    "Vsq3",
    "Vsq3MCtrl",
    "Vsq3MasterTrack",
    "Vsq3Mixer",
    "Vsq3MonoTrack",
    "Vsq3MonoUnit",
    "Vsq3MusicalPart",
    "Vsq3Note",
    "Vsq3NoteStyle",
    "Vsq3ParameterNames",
    "Vsq3PartStyle",
    "Vsq3Singer",
    "Vsq3StereoTrack",
    "Vsq3StereoUnit",
    "Vsq3Tempo",
    "Vsq3TimeSig",
    "Vsq3TypeParamAttr",
    "Vsq3TypePhonemes",
    "Vsq3VVoice",
    "Vsq3VVoiceTable",
    "Vsq3VsTrack",
    "Vsq3VsUnit",
    "Vsq3WavPart",
    "Vsq4",
    "Vsq4MCtrl",
    "Vsq4MasterTrack",
    "Vsq4Mixer",
    "Vsq4MonoTrack",
    "Vsq4MonoUnit",
    "Vsq4MusicalPart",
    "Vsq4Note",
    "Vsq4NoteStyle",
    "Vsq4ParameterNames",
    "Vsq4PartStyle",
    "Vsq4Singer",
    "Vsq4StereoTrack",
    "Vsq4StereoUnit",
    "Vsq4Tempo",
    "Vsq4TimeSig",
    "Vsq4TypeParamAttr",
    "Vsq4TypePhonemes",
    "Vsq4VVoice",
    "Vsq4VVoiceTable",
    "Vsq4VsTrack",
    "Vsq4VsUnit",
    "Vsq4WavPart",
    "Vsqx",
    "VsqxMCtrl",
    "VsqxMasterTrack",
    "VsqxMixer",
    "VsqxMonoTrack",
    "VsqxMonoUnitList",
    "VsqxMusicalPart",
    "VsqxNote",
    "VsqxNoteStyle",
    "VsqxParameterNames",
    "VsqxPartStyle",
    "VsqxSinger",
    "VsqxStereoTrack",
    "VsqxStereoUnitList",
    "VsqxTempoList",
    "VsqxTimeSigList",
    "VsqxTypeParamAttr",
    "VsqxTypePhonemes",
    "VsqxVVoice",
    "VsqxVVoiceTable",
    "VsqxVsTrackList",
    "VsqxVsUnitList",
    "VsqxWavPartList",
    "VsqxWavUnitList",
]
