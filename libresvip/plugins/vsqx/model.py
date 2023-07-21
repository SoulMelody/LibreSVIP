from typing import Union

from .models.vsqx3 import VSQ3_NS, Vsq3  # noqa: F401
from .models.vsqx3 import MasterTrack as Vsq3MasterTrack
from .models.vsqx3 import MCtrl as Vsq3MCtrl
from .models.vsqx3 import MonoTrack as Vsq3MonoTrack
from .models.vsqx3 import MusicalPart as Vsq3MusicalPart
from .models.vsqx3 import Note as Vsq3Note
from .models.vsqx3 import StereoTrack as Vsq3StereoTrack
from .models.vsqx3 import Tempo as Vsq3Tempo
from .models.vsqx3 import TimeSig as Vsq3TimeSig
from .models.vsqx3 import VsTrack as Vsq3VsTrack
from .models.vsqx3 import VVoice as Vsq3VVoice
from .models.vsqx3 import VVoiceTable as Vsq3VVoiceTable
from .models.vsqx3 import WavPart as Vsq3WavPart
from .models.vsqx4 import VSQ4_NS, Vsq4  # noqa: F401
from .models.vsqx4 import MasterTrack as Vsq4MasterTrack
from .models.vsqx4 import MCtrl as Vsq4MCtrl
from .models.vsqx4 import MonoTrack as Vsq4MonoTrack
from .models.vsqx4 import MusicalPart as Vsq4MusicalPart
from .models.vsqx4 import Note as Vsq4Note
from .models.vsqx4 import StereoTrack as Vsq4StereoTrack
from .models.vsqx4 import Tempo as Vsq4Tempo
from .models.vsqx4 import TimeSig as Vsq4TimeSig
from .models.vsqx4 import VsTrack as Vsq4VsTrack
from .models.vsqx4 import VVoice as Vsq4VVoice
from .models.vsqx4 import VVoiceTable as Vsq4VVoiceTable
from .models.vsqx4 import WavPart as Vsq4WavPart

Vsqx = Union[Vsq3, Vsq4]
VsqxMasterTrack = Union[Vsq3MasterTrack, Vsq4MasterTrack]
VsqxMCtrl = Union[Vsq3MCtrl, Vsq4MCtrl]
VsqxMonoTrack = Union[Vsq3MonoTrack, Vsq4MonoTrack]
VsqxMusicalPart = Union[Vsq3MusicalPart, Vsq4MusicalPart]
VsqxNote = Union[Vsq3Note, Vsq4Note]
VsqxStereoTrack = Union[Vsq3StereoTrack, Vsq4StereoTrack]
VsqxTempo = Union[Vsq3Tempo, Vsq4Tempo]
VsqxTimeSig = Union[Vsq3TimeSig, Vsq4TimeSig]
VsqxVsTrack = Union[Vsq3VsTrack, Vsq4VsTrack]
VsqxVVoice = Union[Vsq3VVoice, Vsq4VVoice]
VsqxVVoiceTable = Union[Vsq3VVoiceTable, Vsq4VVoiceTable]
VsqxWavPart = Union[Vsq3WavPart, Vsq4WavPart]
