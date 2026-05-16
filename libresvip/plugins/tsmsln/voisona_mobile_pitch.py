from libresvip.core.time_interval import PiecewiseIntervalDict
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import ParamCurve, SongTempo
from libresvip.model.techno_speech_pitch import (
    TechnoSpeechParamEvent as VoiSonaMobileParamEvent,
)
from libresvip.model.techno_speech_pitch import (
    TechnoSpeechTrackPitchData as VoiSonaMobileTrackPitchData,
)
from libresvip.model.techno_speech_pitch import (
    build_param_interval_dict,
    build_wave_interval_dict,
    generate_for_techno_speech,
    pitch_from_techno_speech_track,
)


def pitch_from_voisona_track(data: VoiSonaMobileTrackPitchData) -> ParamCurve | None:
    return pitch_from_techno_speech_track(data)


def build_voisona_param_interval_dict(
    events: list[VoiSonaMobileParamEvent],
    synchronizer: TimeSynchronizer,
    tick_prefix: int,
) -> PiecewiseIntervalDict:
    return build_param_interval_dict(events, synchronizer, tick_prefix)


def build_voisona_wave_interval_dict(
    events: list[VoiSonaMobileParamEvent],
    synchronizer: TimeSynchronizer,
    tick_prefix: int,
) -> PiecewiseIntervalDict:
    return build_wave_interval_dict(events, synchronizer, tick_prefix)


def generate_for_voisona(
    pitch: ParamCurve,
    tempos: list[SongTempo],
    tick_prefix: int,
) -> VoiSonaMobileTrackPitchData | None:
    return generate_for_techno_speech(pitch, tempos, tick_prefix)
