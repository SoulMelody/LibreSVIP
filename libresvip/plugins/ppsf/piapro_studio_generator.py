import dataclasses

from libresvip.core.lyric_phoneme.japanese import to_romaji
from libresvip.core.lyric_phoneme.japanese.vocaloid_xsampa import (
    legato_chars,
    romaji2xsampa,
)
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    InstrumentalTrack,
    Note,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
    Track,
)
from libresvip.utils.audio import audio_track_info

from .model import (
    PpsfAudioTrackEvent,
    PpsfAudioTrackItem,
    PpsfCurveType,
    PpsfDvlTrackEvent,
    PpsfDvlTrackItem,
    PpsfEventTrack,
    PpsfFileAudioData,
    PpsfMeter,
    PpsfMeters,
    PpsfMuteflag,
    PpsfNote,
    PpsfProject,
    PpsfRegion,
    PpsfSyllable,
    PpsfTempo,
    PpsfTempos,
)
from .options import OutputOptions


@dataclasses.dataclass
class PiaproStudioGenerator:
    options: OutputOptions
    first_bar_length: int = dataclasses.field(init=False)
    time_synchronizer: TimeSynchronizer = dataclasses.field(init=False)

    def generate_project(self, project: Project) -> PpsfProject:
        self.first_bar_length = int(project.time_signature_list[0].bar_length())
        self.time_synchronizer = TimeSynchronizer(project.song_tempo_list)
        ppsf_project = PpsfProject()
        ppsf_project.ppsf.project.meter = self.generate_time_signatures(project.time_signature_list)
        ppsf_project.ppsf.project.tempo = self.generate_tempos(project.song_tempo_list)
        ppsf_project.ppsf.project.dvl_track = self.generate_singing_tracks(
            project.track_list,
            ppsf_project.ppsf.gui_settings.track_editor.event_tracks,
        )
        ppsf_project.ppsf.project.audio_track = self.generate_instrumental_tracks(
            project.track_list,
            ppsf_project.ppsf.gui_settings.track_editor.event_tracks,
        )
        ppsf_project.ppsf.gui_settings.project_length = self.first_bar_length
        for event_track in ppsf_project.ppsf.gui_settings.track_editor.event_tracks:
            for region in event_track.regions:
                ppsf_project.ppsf.gui_settings.project_length = max(
                    ppsf_project.ppsf.gui_settings.project_length,
                    region.position + region.length + self.first_bar_length,
                )
        return ppsf_project

    def generate_time_signatures(self, time_signatures: list[TimeSignature]) -> PpsfMeters:
        ppsf_meters = PpsfMeters()
        if len(time_signatures):
            ppsf_meters.const.nume = time_signatures[0].numerator
            ppsf_meters.const.denomi = time_signatures[0].denominator
        if len(time_signatures) > 1:
            ppsf_meters.use_sequence = True
            ppsf_meters.sequence = [
                PpsfMeter(
                    nume=time_signature.numerator,
                    denomi=time_signature.denominator,
                    measure=time_signature.bar_index,
                )
                for time_signature in time_signatures[1:]
            ]
        return ppsf_meters

    def generate_tempos(self, tempos: list[SongTempo]) -> PpsfTempos:
        ppsf_tempos = PpsfTempos()
        if len(tempos):
            ppsf_tempos.const = round(tempos[0].bpm * 10000)
        if len(tempos) > 1:
            ppsf_tempos.use_sequence = True
            ppsf_tempos.sequence = [
                PpsfTempo(
                    value=round(tempo.bpm * 10000),
                    tick=tempo.position,
                    curve_type=PpsfCurveType.BORDER,
                )
                for tempo in tempos[1:]
            ]
        return ppsf_tempos

    def generate_singing_tracks(
        self, tracks: list[Track], event_tracks: list[PpsfEventTrack]
    ) -> list[PpsfDvlTrackItem]:
        dvl_tracks = []
        for track in tracks:
            if isinstance(track, SingingTrack):
                mute_flag = PpsfMuteflag.NONE
                if track.mute:
                    mute_flag = PpsfMuteflag.MUTE
                elif track.solo:
                    mute_flag = PpsfMuteflag.SOLO
                event_track = PpsfEventTrack(
                    index=len(event_tracks),
                    track_type=4,
                    mute_solo=mute_flag,
                    notes=[],
                    nt_envelope_preset_id=2,
                )
                track_events, event_track.notes = self.generate_notes(track.note_list)
                event_track.regions.append(
                    PpsfRegion(
                        auto_expand_left=True,
                        auto_expand_right=True,
                        position=0,
                        length=(track_events[-1].pos + track_events[-1].length)
                        if len(track_events)
                        else 0,
                    )
                )
                dvl_tracks.append(PpsfDvlTrackItem(name=track.title, events=track_events))
                event_tracks.append(event_track)
        return dvl_tracks

    def generate_instrumental_tracks(
        self, tracks: list[Track], event_tracks: list[PpsfEventTrack]
    ) -> list[PpsfAudioTrackItem]:
        audio_tracks = []
        for track in tracks:
            if (
                isinstance(track, InstrumentalTrack)
                and (track_info := audio_track_info(track.audio_file_path, only_wav=True))
                is not None
            ):
                offset = self.time_synchronizer.get_actual_secs_from_ticks(track.offset)
                tick_length = round(
                    self.time_synchronizer.get_actual_ticks_from_secs(
                        offset + track_info.duration / 1000
                    )
                    - track.offset
                )
                audio_track = PpsfAudioTrackItem(
                    name=track.title,
                    events=[
                        PpsfAudioTrackEvent(
                            tick_length=tick_length,
                            tick_pos=track.offset,
                            file_audio_data=PpsfFileAudioData(file_path=track.audio_file_path),
                        )
                    ],
                )
                audio_tracks.append(audio_track)
                mute_flag = PpsfMuteflag.NONE
                if track.mute:
                    mute_flag = PpsfMuteflag.MUTE
                elif track.solo:
                    mute_flag = PpsfMuteflag.SOLO
                event_tracks.append(
                    PpsfEventTrack(
                        index=len(event_tracks),
                        track_type=1,
                        mute_solo=mute_flag,
                        regions=[
                            PpsfRegion(
                                length=tick_length,
                                position=track.offset,
                                audio_event_index=0,
                            )
                        ],
                    )
                )
        return audio_tracks

    def generate_notes(self, notes: list[Note]) -> tuple[list[PpsfDvlTrackEvent], list[PpsfNote]]:
        track_events = []
        ppsf_notes = []
        for i, note in enumerate(notes):
            track_events.append(
                PpsfDvlTrackEvent(
                    note_number=note.key_number,
                    pos=note.start_pos,
                    length=note.length,
                    lyric=note.lyric,
                    symbols="-"
                    if note.lyric in legato_chars
                    else romaji2xsampa.get(to_romaji(note.lyric), "4 a"),
                )
            )
            ppsf_notes.append(
                PpsfNote(
                    region_index=0,
                    event_index=i,
                    length=note.length,
                    syllables=[
                        PpsfSyllable(
                            lyric_text=note.lyric,
                            symbols_text="-"
                            if note.lyric in legato_chars
                            else romaji2xsampa.get(to_romaji(note.lyric), "4 a"),
                        )
                    ],
                )
            )
        return track_events, ppsf_notes
