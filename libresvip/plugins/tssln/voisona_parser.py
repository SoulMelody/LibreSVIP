import dataclasses
import operator
from typing import Optional

import more_itertools

from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    InstrumentalTrack,
    Note,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
)

from .constants import OCTAVE_OFFSET, TICK_RATE
from .model import VoiSonaAudioTrackItem, VoiSonaProject, VoiSonaSingingTrackItem
from .options import InputOptions


@dataclasses.dataclass
class VoiSonaParser:
    options: InputOptions
    time_synchronizer: TimeSynchronizer = dataclasses.field(init=False)

    def parse_project(self, voisona_project: VoiSonaProject) -> Project:
        time_signatures = []
        tempos = []
        tracks = []
        for track in voisona_project.tracks:
            for item in track.track:
                if isinstance(item, VoiSonaSingingTrackItem):
                    if parse_result := self.parse_singing_track(item):
                        track, tempo_part, time_signature_part = parse_result
                        tracks.append(track)
                        tempos.extend(tempo_part)
                        time_signatures.extend(time_signature_part)
        tempos = self.merge_tempos(tempos)
        self.time_synchronizer = TimeSynchronizer(tempos)
        for track in voisona_project.tracks:
            for item in track.track:
                if isinstance(item, VoiSonaAudioTrackItem):
                    for i, event in enumerate(item.audio_event):
                        tracks.append(
                            InstrumentalTrack(
                                title=f"{item.name} {i + 1}",
                                audio_file_path=event.path,
                                offset=int(
                                    self.time_synchronizer.get_actual_ticks_from_secs(
                                        event.offset
                                    )
                                ),
                            )
                        )
        time_signatures = self.merge_time_signatures(time_signatures)
        return Project(
            time_signature_list=time_signatures,
            song_tempo_list=tempos,
            track_list=tracks,
        )

    def merge_tempos(self, tempos: list[SongTempo]) -> list[SongTempo]:
        buckets = more_itertools.bucket(tempos, key=operator.attrgetter("position"))
        return [next(buckets[key]) for key in buckets] or [SongTempo()]

    def merge_time_signatures(
        self, time_signatures: list[TimeSignature]
    ) -> list[TimeSignature]:
        buckets = more_itertools.bucket(
            time_signatures, key=operator.attrgetter("bar_index")
        )
        return [next(buckets[key]) for key in buckets] or [TimeSignature()]

    def parse_singing_track(
        self, track: VoiSonaSingingTrackItem
    ) -> Optional[tuple[SingingTrack, list[SongTempo], list[TimeSignature]]]:
        if track.plugin_data.state_information.song is None:
            return None
        time_signatures = [
            TimeSignature(bar_index=0, numerator=4, denominator=4),
        ]
        prev_tick = 0
        tempos = []
        notes = []

        tick_prefix = -int(time_signatures[0].bar_length())
        for song in track.plugin_data.state_information.song:
            for beat in song.beat:
                for time_node in beat.time:
                    tick = time_node.clock // TICK_RATE
                    numerator = time_node.beats
                    denominator = time_node.beat_type

                    if (
                        tick is not None
                        and numerator is not None
                        and denominator is not None
                    ):
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
                    tick = tempo_node.clock // TICK_RATE - tick_prefix
                    bpm = (
                        float(tempo_node.tempo)
                        if tempo_node.tempo is not None
                        else None
                    )
                    if tick is not None and bpm is not None:
                        tempos.append(SongTempo(position=tick, bpm=bpm))
            for score in song.score:
                for note_node in score.note:
                    pitch_octave = note_node.pitch_octave - OCTAVE_OFFSET
                    notes.append(
                        Note(
                            key_number=note_node.pitch_step + pitch_octave * 12,
                            lyric=note_node.lyric,
                            start_pos=(note_node.clock // TICK_RATE),
                            length=note_node.duration // TICK_RATE,
                        )
                    )

        time_signatures = [
            time_signature.model_copy(
                update={"bar_index": time_signature.bar_index + 1}
            )
            for time_signature in time_signatures
        ]
        return SingingTrack(title=track.name, note_list=notes), tempos, time_signatures
