import dataclasses
from typing import Optional

from libresvip.core.lyric_phoneme.japanese.vocaloid_xsampa import legato_chars
from libresvip.model.base import (
    InstrumentalTrack,
    Note,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
)
from libresvip.model.point import Point

from .model import (
    PpsfAudioTrackItem,
    PpsfCurveType,
    PpsfDvlTrackEvent,
    PpsfDvlTrackItem,
    PpsfEventTrack,
    PpsfMeters,
    PpsfProject,
    PpsfTempos,
)
from .options import InputOptions
from .ppsf_interval_dict import ppsf_key_interval_dict


@dataclasses.dataclass
class PiaproStudioNTParser:
    options: InputOptions
    first_bar_ticks: int = dataclasses.field(init=False)

    def parse_project(self, ppsf_project: PpsfProject) -> Project:
        time_signatures = self.parse_time_signatures(ppsf_project.ppsf.project.meter)
        self.first_bar_ticks = round(time_signatures[0].bar_length())
        tempos = self.parse_tempos(ppsf_project.ppsf.project.tempo)
        singing_tracks = self.parse_singing_tracks(
            ppsf_project.ppsf.project.dvl_track,
            ppsf_project.ppsf.gui_settings.track_editor.event_tracks,
        )
        instrumental_tracks = self.parse_instrumental_tracks(ppsf_project.ppsf.project.audio_track)
        return Project(
            time_signature_list=time_signatures,
            song_tempo_list=tempos,
            track_list=singing_tracks + instrumental_tracks,
        )

    def parse_time_signatures(self, ppsf_meters: PpsfMeters) -> list[TimeSignature]:
        time_signatures: list[TimeSignature] = []
        first_time_signature = TimeSignature(
            numerator=ppsf_meters.const.nume,
            denominator=ppsf_meters.const.denomi,
        )
        if ppsf_meters.use_sequence:
            time_signatures.extend(
                TimeSignature(
                    numerator=meter.nume,
                    denominator=meter.denomi,
                    bar_index=meter.measure,
                )
                for meter in ppsf_meters.sequence
            )
        if not len(time_signatures) or time_signatures[0].bar_index != 0:
            time_signatures.insert(0, first_time_signature)
        return time_signatures

    def parse_tempos(self, ppsf_tempos: PpsfTempos) -> list[SongTempo]:
        tempos: list[SongTempo] = []
        first_tempo = SongTempo(bpm=ppsf_tempos.const / 10000, position=0)
        if ppsf_tempos.use_sequence:
            tempos.extend(
                SongTempo(bpm=tempo.value / 10000, position=tempo.tick)
                for tempo in ppsf_tempos.sequence
            )
        if not len(tempos) or tempos[0].position != 0:
            tempos.insert(0, first_tempo)
        return tempos

    def parse_instrumental_tracks(
        self, ppsf_audio_tracks: list[PpsfAudioTrackItem]
    ) -> list[InstrumentalTrack]:
        tracks = []
        if self.options.import_instrumental_track:
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
        self,
        ppsf_dvl_tracks: Optional[list[PpsfDvlTrackItem]],
        event_tracks: list[PpsfEventTrack],
    ) -> list[SingingTrack]:
        tracks = []
        if ppsf_dvl_tracks is not None:
            for track, event_track in zip(ppsf_dvl_tracks, event_tracks):
                singing_track = SingingTrack(
                    title=track.name,
                    ai_singer_name=track.singer.singer_name,
                    note_list=self.parse_notes(track.events),
                )
                for parameter in track.parameters:
                    if (
                        self.options.import_pitch
                        and parameter.base_sequence is not None
                        and parameter.base_sequence.name == "pitch_bend"
                    ):
                        key_interval_dict = ppsf_key_interval_dict(track.events, event_track.notes)
                        for point in parameter.base_sequence.sequence:
                            if point.curve_type == PpsfCurveType.BORDER and point.value == 0:
                                singing_track.edited_params.pitch.points.append(
                                    Point(
                                        x=point.pos + self.first_bar_ticks,
                                        y=-100,
                                    )
                                )
                            elif (base_key := key_interval_dict.get(point.pos)) is not None:
                                singing_track.edited_params.pitch.points.append(
                                    Point(
                                        x=point.pos + self.first_bar_ticks,
                                        y=point.value + round(base_key * 100),
                                    )
                                )
                tracks.append(singing_track)
        return tracks

    def parse_notes(self, ppsf_dvl_track_events: list[PpsfDvlTrackEvent]) -> list[Note]:
        return [
            Note(
                key_number=event.note_number,
                start_pos=event.pos,
                length=event.length,
                lyric="-" if event.lyric in legato_chars else event.lyric,
                pronunciation=event.symbols,
            )
            for event in ppsf_dvl_track_events
            if event.enabled
        ]
