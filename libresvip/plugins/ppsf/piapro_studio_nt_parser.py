import dataclasses
from typing import Optional

from libresvip.model.base import (
    InstrumentalTrack,
    Note,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
)

from .model import (
    PpsfAudioTrackItem,
    PpsfDvlTrackEvent,
    PpsfDvlTrackItem,
    PpsfMeters,
    PpsfProject,
    PpsfTempos,
)
from .options import InputOptions


@dataclasses.dataclass
class PiaproStudioNTParser:
    options: InputOptions

    def parse_project(self, ppsf_project: PpsfProject) -> Project:
        time_signatures = self.parse_time_signatures(ppsf_project.ppsf.project.meter)
        tempos = self.parse_tempos(ppsf_project.ppsf.project.tempo)
        singing_tracks = self.parse_singing_tracks(ppsf_project.ppsf.project.dvl_track)
        instrumental_tracks = self.parse_instrumental_tracks(
            ppsf_project.ppsf.project.audio_track
        )
        return Project(
            time_signature_list=time_signatures,
            song_tempo_list=tempos,
            track_list=singing_tracks + instrumental_tracks,
        )

    def parse_time_signatures(self, ppsf_meters: PpsfMeters) -> list[TimeSignature]:
        time_signatures = []
        first_time_signature = TimeSignature(
            numerator=ppsf_meters.const.nume,
            denominator=ppsf_meters.const.denomi,
        )
        if ppsf_meters.use_sequence:
            for meter in ppsf_meters.sequence:
                time_signatures.append(
                    TimeSignature(
                        numerator=meter.nume,
                        denominator=meter.denomi,
                        bar_index=meter.measure,
                    )
                )
        if not len(time_signatures) or time_signatures[0].bar_index != 0:
            time_signatures.insert(0, first_time_signature)
        return time_signatures

    def parse_tempos(self, ppsf_tempos: PpsfTempos) -> list[SongTempo]:
        tempos = []
        first_tempo = SongTempo(bpm=ppsf_tempos.const / 10000, position=0)
        if ppsf_tempos.use_sequence:
            for tempo in ppsf_tempos.sequence:
                tempos.append(SongTempo(bpm=tempo.value / 10000, position=tempo.tick))
        if not len(tempos) or tempos[0].position != 0:
            tempos.insert(0, first_tempo)
        return tempos

    def parse_instrumental_tracks(
        self, ppsf_audio_tracks: list[PpsfAudioTrackItem]
    ) -> list[InstrumentalTrack]:
        tracks = []
        for track in ppsf_audio_tracks:
            for i, event in enumerate(track.events):
                instrumental_track = InstrumentalTrack(
                    title=f"{track.name} {i + 1}",
                    audio_file_path=event.file_audio_data.file_path,
                    offset=event.tick_pos,
                )
                tracks.append(instrumental_track)
        return tracks

    def parse_singing_tracks(
        self, ppsf_dvl_tracks: Optional[list[PpsfDvlTrackItem]]
    ) -> list[SingingTrack]:
        tracks = []
        if ppsf_dvl_tracks is not None:
            for track in ppsf_dvl_tracks:
                singing_track = SingingTrack(
                    title=track.name,
                    ai_singer_name=track.singer.singer_name,
                    note_list=self.parse_notes(track.events),
                )
                tracks.append(singing_track)
        return tracks

    def parse_notes(self, ppsf_dvl_track_events: list[PpsfDvlTrackEvent]) -> list[Note]:
        return [
            Note(
                key_number=event.note_number,
                start_pos=event.pos,
                length=event.length,
                lyric=event.lyric,
                pronunciation=event.symbols,
            )
            for event in ppsf_dvl_track_events
            if event.enabled
        ]
