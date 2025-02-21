import dataclasses
import itertools
import operator

import more_itertools
from wanakana import PROLONGED_SOUND_MARK

from libresvip.core.tick_counter import (
    shift_beat_list,
    shift_tempo_list,
    skip_beat_list,
    skip_tempo_list,
)
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    Note,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
)

from .constants import OCTAVE_OFFSET, TICK_RATE
from .model import (
    VoiSonaMobilePointData,
    VoiSonaMobileProject,
    VoiSonaMobileStateInformation,
)
from .options import InputOptions
from .voisona_mobile_pitch import (
    VoiSonaMobileParamEvent,
    VoiSonaMobileTrackPitchData,
    pitch_from_voisona_track,
)


@dataclasses.dataclass
class VoiSonaMobileParser:
    options: InputOptions
    time_synchronizer: TimeSynchronizer = dataclasses.field(init=False)

    def parse_project(self, voisona_project: VoiSonaMobileProject) -> Project:
        time_signatures = []
        tempos = []
        tracks = []
        for track in voisona_project.mobile_singer:
            if parse_result := self.parse_singing_track(track.mobile_singer_data.state_information):
                singing_track, tempo_part, time_signature_part = parse_result
                tracks.append(singing_track)
                tempos.extend(tempo_part)
                time_signatures.extend(time_signature_part)
        tempos = self.merge_tempos(tempos)
        self.time_synchronizer = TimeSynchronizer(tempos)
        time_signatures = self.merge_time_signatures(time_signatures)
        return Project(
            time_signature_list=skip_beat_list(time_signatures, 0),
            song_tempo_list=skip_tempo_list(tempos, 0),
            track_list=tracks,
        )

    def merge_tempos(self, tempos: list[SongTempo]) -> list[SongTempo]:
        buckets = more_itertools.bucket(tempos, key=operator.attrgetter("position"))
        return [next(buckets[key]) for key in buckets] or [SongTempo()]

    def merge_time_signatures(self, time_signatures: list[TimeSignature]) -> list[TimeSignature]:
        buckets = more_itertools.bucket(time_signatures, key=operator.attrgetter("bar_index"))
        return [next(buckets[key]) for key in buckets] or [TimeSignature()]

    def parse_singing_track(
        self, state_information: VoiSonaMobileStateInformation
    ) -> tuple[SingingTrack, list[SongTempo], list[TimeSignature]] | None:
        if state_information.song is None:
            return None
        time_signatures = [
            TimeSignature(bar_index=0, numerator=4, denominator=4),
        ]
        prev_tick = 0
        tempos = []
        notes = []

        tick_prefix = int(time_signatures[0].bar_length())
        for song in state_information.song:
            for beat in song.beat:
                for time_node in beat.time:
                    tick = int(time_node.clock / TICK_RATE)
                    numerator = time_node.beats
                    denominator = time_node.beat_type

                    ticks_in_measure = time_signatures[-1].bar_length()
                    tick_diff = tick - prev_tick
                    measure_diff = tick_diff / ticks_in_measure
                    time_signatures.append(
                        TimeSignature(
                            bar_index=int(
                                time_signatures[-1].bar_index + measure_diff,
                            ),
                            numerator=numerator,
                            denominator=denominator,
                        )
                    )
                    prev_tick = tick
            for tempo in song.tempo:
                for tempo_node in tempo.sound:
                    tick = int(tempo_node.clock / TICK_RATE)
                    bpm = float(tempo_node.tempo)
                    tempos.append(SongTempo(position=tick, bpm=bpm))
            for score in song.score:
                for note_node in score.note:
                    pitch_octave = note_node.pitch_octave - OCTAVE_OFFSET
                    phoneme = None
                    if note_node.phoneme:
                        phoneme = note_node.phoneme.replace(",", " ")
                    notes.append(
                        Note(
                            key_number=note_node.pitch_step + pitch_octave * 12,
                            lyric="-"
                            if note_node.lyric == chr(PROLONGED_SOUND_MARK)
                            else note_node.lyric,
                            start_pos=(note_node.clock // TICK_RATE),
                            length=note_node.duration // TICK_RATE,
                            pronunciation=phoneme,
                        )
                    )
        tempos = shift_tempo_list(tempos, tick_prefix)
        voisona_track_pitch_data = None
        if state_information.parameter is not None:
            for parameter in state_information.parameter:
                if parameter.log_f0 is not None:
                    pitch_data_nodes = itertools.chain.from_iterable(
                        curve.data for curve in parameter.log_f0
                    )
                    vibrato_amplitude_nodes = itertools.chain.from_iterable(
                        curve.data for curve in parameter.vib_amp or []
                    )
                    vibrato_frequency_nodes = itertools.chain.from_iterable(
                        curve.data for curve in parameter.vib_frq or []
                    )
                    pitch_datas = [
                        pitch_data
                        for data_node in pitch_data_nodes
                        if (pitch_data := self.parse_param_data(data_node))
                    ]
                    vibrato_amplitude_data = [
                        vibrato_amplitude
                        for vibrato_amplitude_node in vibrato_amplitude_nodes
                        if (vibrato_amplitude := self.parse_param_data(vibrato_amplitude_node))
                    ]
                    vibrato_frequency_data = [
                        vibrato_frequency
                        for vibrato_frequency_node in vibrato_frequency_nodes
                        if (vibrato_frequency := self.parse_param_data(vibrato_frequency_node))
                    ]
                    voisona_track_pitch_data = VoiSonaMobileTrackPitchData(
                        events=pitch_datas,
                        tempos=tempos,
                        tick_prefix=tick_prefix,
                        vibrato_amplitude_events=vibrato_amplitude_data,
                        vibrato_frequency_events=vibrato_frequency_data,
                    )
        time_signatures = shift_beat_list(time_signatures, 1)
        singing_track = SingingTrack(note_list=notes)
        if (
            self.options.import_pitch
            and voisona_track_pitch_data is not None
            and (pitch := pitch_from_voisona_track(voisona_track_pitch_data)) is not None
        ):
            singing_track.edited_params.pitch = pitch
        return singing_track, tempos, time_signatures

    @staticmethod
    def parse_param_data(
        data_element: VoiSonaMobilePointData,
    ) -> VoiSonaMobileParamEvent | None:
        value = float(data_element.value)
        index = data_element.index or None
        repeat = data_element.repeat or None
        return VoiSonaMobileParamEvent(idx=index, repeat=repeat, value=value)
