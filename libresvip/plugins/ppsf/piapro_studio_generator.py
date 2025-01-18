import dataclasses

from libresvip.core.lyric_phoneme.japanese import to_romaji
from libresvip.core.lyric_phoneme.japanese.vocaloid_xsampa import (
    legato_chars,
    romaji2xsampa,
)
from libresvip.core.time_interval import PiecewiseIntervalDict
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    InstrumentalTrack,
    Note,
    ParamCurve,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
    Track,
)
from libresvip.utils.audio import audio_track_info
from libresvip.utils.search import find_index

from .model import (
    PpsfAudioTrackEvent,
    PpsfAudioTrackItem,
    PpsfBaseSequence,
    PpsfCurvePoint,
    PpsfCurvePointSeq,
    PpsfCurveType,
    PpsfDvlTrackEvent,
    PpsfDvlTrackItem,
    PpsfEventTrack,
    PpsfFileAudioData,
    PpsfMeter,
    PpsfMeters,
    PpsfNote,
    PpsfParamPoint,
    PpsfProject,
    PpsfRegion,
    PpsfSeqParam,
    PpsfSyllable,
    PpsfTempo,
    PpsfTempos,
)
from .options import OutputOptions
from .ppsf_interval_dict import ppsf_key_interval_dict


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
                if track.mute:
                    mute_flag = -1
                elif track.solo:
                    mute_flag = 1
                else:
                    mute_flag = 0
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
                key_interval_dict = ppsf_key_interval_dict(track_events, event_track.notes)
                pitch_param, pitch_curve_point = self.generate_pitch(
                    track.edited_params.pitch, key_interval_dict, track.note_list
                )
                event_track.curve_points.append(pitch_curve_point)
                dvl_track = PpsfDvlTrackItem(
                    name=track.title, events=track_events, parameters=[pitch_param]
                )
                dvl_tracks.append(dvl_track)
                event_tracks.append(event_track)
        return dvl_tracks

    def generate_pitch(
        self, pitch: ParamCurve, key_interval_dict: PiecewiseIntervalDict, notes: list[Note]
    ) -> tuple[PpsfSeqParam, PpsfCurvePoint]:
        pitch_param = PpsfSeqParam()
        curve_point = PpsfCurvePoint(
            sub_track_category=7,
            sub_track_id=2,
        )
        pitch_param.base_sequence = PpsfBaseSequence(
            constant=0,
            name="pitch_bend",
            use_sequence=True,
        )
        in_pitch_part = False
        for point in pitch.points.root:
            pos = point.x - self.first_bar_length
            if point.y == -100:
                if (
                    point.x not in [-192000, 1073741823]
                    and in_pitch_part
                    and len(pitch_param.base_sequence.sequence)
                ):
                    pitch_param.base_sequence.sequence.append(
                        PpsfParamPoint(
                            curve_type=PpsfCurveType.BORDER,
                            pos=pitch_param.base_sequence.sequence[-1].pos,
                            value=pitch_param.base_sequence.sequence[-1].value,
                        )
                    )
                    curve_point.sequence.append(
                        PpsfCurvePointSeq(
                            border_type=7,
                            abs_value=-1,
                            edited_by_user=True,
                            region_index=-1,
                            note_index=-1,
                            seg_array_id=-1,
                        )
                    )
                    in_pitch_part = False
            elif (base_key := key_interval_dict.get(pos)) is not None:
                if not in_pitch_part:
                    pitch_param.base_sequence.sequence.append(
                        PpsfParamPoint(
                            curve_type=PpsfCurveType.BORDER,
                            pos=pos - 1,
                            value=0,
                        )
                    )
                    curve_point.sequence.append(
                        PpsfCurvePointSeq(
                            border_type=6,
                            abs_value=-1,
                            edited_by_user=True,
                            region_index=-1,
                            note_index=-1,
                            seg_array_id=-1,
                        )
                    )
                    in_pitch_part = True
                pitch_param.base_sequence.sequence.append(
                    PpsfParamPoint(
                        curve_type=PpsfCurveType.NORMAL,
                        pos=pos,
                        value=point.y - round(base_key * 100),
                    )
                )
                curve_point.sequence.append(
                    PpsfCurvePointSeq(
                        border_type=1,
                        abs_value=point.y,
                        edited_by_user=True,
                        region_index=-1,
                        note_index=find_index(
                            notes, lambda note: note.start_pos <= pos <= note.end_pos
                        ),
                        seg_array_id=-1,
                    )
                )
        return pitch_param, curve_point

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
                if track.mute:
                    mute_flag = -1
                elif track.solo:
                    mute_flag = 1
                else:
                    mute_flag = 0
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
