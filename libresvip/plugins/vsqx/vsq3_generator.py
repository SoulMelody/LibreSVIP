import dataclasses
import operator
from typing import Union, cast

from libresvip.core.lyric_phoneme.chinese import get_pinyin_series
from libresvip.core.lyric_phoneme.chinese.vocaloid_xsampa import pinyin2xsampa
from libresvip.core.lyric_phoneme.japanese import to_romaji
from libresvip.core.lyric_phoneme.japanese.vocaloid_xsampa import (
    legato_chars,
    romaji2xsampa,
)
from libresvip.core.tick_counter import shift_beat_list, skip_tempo_list
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.core.warning_types import show_warning
from libresvip.model.base import (
    InstrumentalTrack,
    Note,
    ParamCurve,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
)
from libresvip.utils.audio import audio_track_info
from libresvip.utils.translation import gettext_lazy as _

from .constants import (
    BPM_RATE,
    DEFAULT_CHINESE_PHONEME,
    DEFAULT_JAPANESE_PHONEME,
)
from .enums import VocaloidLanguage
from .model import (
    VocaloidStyleTypes,
    Vsq3,
    Vsq3MCtrl,
    Vsq3MonoTrack,
    Vsq3MonoUnit,
    Vsq3MusicalPart,
    Vsq3Note,
    Vsq3ParameterNames,
    Vsq3Singer,
    Vsq3StereoTrack,
    Vsq3StereoUnit,
    Vsq3Tempo,
    Vsq3TimeSig,
    Vsq3TypeParamAttr,
    Vsq3TypePhonemes,
    Vsq3VsTrack,
    Vsq3VsUnit,
    Vsq3VVoice,
    Vsq3WavPart,
)
from .options import OutputOptions
from .vocaloid_pitch import generate_for_vocaloid


@dataclasses.dataclass
class Vsq3Generator:
    options: OutputOptions
    first_bar_length: int = dataclasses.field(init=False)
    style_params: dict[str, Union[int, list[int]]] = dataclasses.field(init=False)
    time_synchronizer: TimeSynchronizer = dataclasses.field(init=False)

    def generate_project(self, project: Project) -> Vsq3:
        self.style_params = VocaloidStyleTypes().model_dump(by_alias=True)
        self.time_synchronizer = TimeSynchronizer(project.song_tempo_list)
        self.first_bar_length = round(project.time_signature_list[0].bar_length())
        vsqx = Vsq3()
        mixer = vsqx.mixer
        master_track = vsqx.master_track
        tick_prefix = int(project.time_signature_list[0].bar_length())
        master_track.time_sig = self.generate_time_signatures(
            project.time_signature_list, master_track.pre_measure
        )
        master_track.tempo = self.generate_tempos(project.song_tempo_list, tick_prefix)
        vsqx.v_voice_table.v_voice.append(
            Vsq3VVoice(
                comp_id=self.options.default_comp_id,
                v_voice_name=self.options.default_singer_name,
            )
        )
        vsqx.vs_track, mixer.vs_unit = self.generate_singing_tracks(
            [track for track in project.track_list if isinstance(track, SingingTrack)],
            tick_prefix,
        )
        if first_instrumental_track := next(
            (track for track in project.track_list if isinstance(track, InstrumentalTrack)),
            None,
        ):
            self.generate_instrumental_track(first_instrumental_track, vsqx, tick_prefix)
        return vsqx

    def generate_instrumental_track(
        self, track: InstrumentalTrack, vsqx: Vsq3, tick_prefix: int
    ) -> None:
        if (
            (track_info := audio_track_info(track.audio_file_path, only_wav=True)) is not None
            and track_info.sampling_rate == 44100
            and track_info.bit_depth == 16
        ):
            wav_part = Vsq3WavPart(
                part_name=track.title,
                file_path=track.audio_file_path,
                pos_tick=tick_prefix + track.offset,
                play_time=round(
                    self.time_synchronizer.get_actual_ticks_from_secs_offset(
                        track.offset, track_info.duration / 1000
                    )
                )
                - track.offset,
                sample_rate=track_info.sampling_rate,
                sample_reso=track_info.bit_depth,
                channels=track_info.channel_s,
            )
            if track_info.channel_s == 1:
                vsqx.mixer.mono_unit = Vsq3MonoUnit(
                    mute=int(track.mute),
                    solo=int(track.solo),
                )
                vsqx.mono_track = Vsq3MonoTrack(wav_part=[wav_part])
            elif track_info.channel_s == 2:
                vsqx.mixer.stereo_unit = Vsq3StereoUnit(
                    mute=int(track.mute),
                    solo=int(track.solo),
                )
                vsqx.stereo_track = Vsq3StereoTrack(wav_part=[wav_part])

    def generate_singing_tracks(
        self, track_list: list[SingingTrack], tick_prefix: int
    ) -> tuple[list[Vsq3VsTrack], list[Vsq3VsUnit]]:
        vs_track_list = []
        vs_unit_list = []
        if not len(track_list):
            track_list.append(SingingTrack(title="Track"))
        elif self.options.default_lang_id not in [
            VocaloidLanguage.SIMPLIFIED_CHINESE,
            VocaloidLanguage.JAPANESE,
        ]:
            show_warning(
                _(
                    'Phonemes of all notes were set to "la". Please use "Lyrics" -> "Convert Phonemes" in the menu of VOCALOID3 to reset them.'
                )
            )
        for track_index, track in enumerate(track_list):
            vsqx_track = Vsq3VsTrack(
                vs_track_no=track_index,
                track_name=track.title,
            )
            if track.note_list:
                musical_part = Vsq3MusicalPart(
                    pos_tick=tick_prefix,
                    play_time=track.note_list[-1].end_pos if track.note_list else 0,
                    note=self.generate_notes(track.note_list),
                    singer=[Vsq3Singer(v_bs=self.options.default_lang_id)],
                )
                musical_part.part_style.attr.extend(
                    Vsq3TypeParamAttr(
                        type_param_attr_id=param_name,
                        value=cast(int, param_value),
                    )
                    for param_name, param_value in self.style_params.items()
                    if param_value is not None
                )
                if pitch := self.generate_pitch(track.edited_params.pitch, track.note_list):
                    musical_part.m_ctrl = pitch
                vsqx_track.musical_part = [musical_part]
            vsqx_unit = Vsq3VsUnit(
                vs_track_no=track_index,
                mute=int(track.mute),
                solo=int(track.solo),
            )
            vs_track_list.append(vsqx_track)
            vs_unit_list.append(vsqx_unit)
        return vs_track_list, vs_unit_list

    def generate_tempos(self, song_tempos: list[SongTempo], tick_prefix: int) -> list[Vsq3Tempo]:
        song_tempos = skip_tempo_list(song_tempos, tick_prefix)
        return [
            Vsq3Tempo(
                pos_tick=song_tempo.position,
                bpm=int(song_tempo.bpm * BPM_RATE),
            )
            for song_tempo in song_tempos
        ]

    def generate_time_signatures(
        self, time_signatures: list[TimeSignature], measure_prefix: int
    ) -> list[Vsq3TimeSig]:
        time_signatures = shift_beat_list(time_signatures, measure_prefix)
        return [
            Vsq3TimeSig(
                pos_mes=time_signature.bar_index,
                nume=time_signature.numerator,
                denomi=time_signature.denominator,
            )
            for time_signature in time_signatures
        ]

    def generate_notes(self, notes: list[Note]) -> list[Vsq3Note]:
        note_list = []
        for note in notes:
            vsqx_note = Vsq3Note(
                pos_tick=note.start_pos,
                dur_tick=note.length,
                note_num=note.key_number,
                lyric=note.lyric,
            )
            vsqx_note.note_style.attr.extend(
                Vsq3TypeParamAttr(
                    type_param_attr_id=param_name,
                    value=cast(int, param_value),
                )
                for param_name, param_value in self.style_params.items()
                if param_value is not None
            )
            if note.lyric in legato_chars:
                vsqx_note.phnms = Vsq3TypePhonemes(value="-")
            elif self.options.default_lang_id == VocaloidLanguage.SIMPLIFIED_CHINESE:
                vsqx_note.lyric = " ".join(
                    get_pinyin_series([note.lyric], filter_non_chinese=False)
                )
                vsqx_note.phnms = Vsq3TypePhonemes(
                    value=pinyin2xsampa.get(vsqx_note.lyric, DEFAULT_CHINESE_PHONEME),
                )
            elif self.options.default_lang_id == VocaloidLanguage.JAPANESE:
                vsqx_note.phnms = Vsq3TypePhonemes(
                    value=romaji2xsampa.get(
                        to_romaji(cast(str, vsqx_note.lyric)),
                        DEFAULT_JAPANESE_PHONEME,
                    ),
                )
            else:
                vsqx_note.phnms = Vsq3TypePhonemes(value=DEFAULT_CHINESE_PHONEME)
            note_list.append(vsqx_note)
        return note_list

    def generate_pitch(self, pitch: ParamCurve, notes: list[Note]) -> list[Vsq3MCtrl]:
        music_controls: list[Vsq3MCtrl] = []
        if pitch_raw_data := generate_for_vocaloid(
            pitch, notes, self.first_bar_length, self.time_synchronizer
        ):
            music_controls.extend(
                Vsq3MCtrl(
                    pos_tick=pbs_event.pos,
                    attr=Vsq3TypeParamAttr(
                        type_param_attr_id=Vsq3ParameterNames.PBS.value,
                        value=pbs_event.value,
                    ),
                )
                for pbs_event in pitch_raw_data.pbs
            )
            music_controls.extend(
                Vsq3MCtrl(
                    pos_tick=pit_event.pos,
                    attr=Vsq3TypeParamAttr(
                        type_param_attr_id=Vsq3ParameterNames.PIT.value,
                        value=pit_event.value,
                    ),
                )
                for pit_event in pitch_raw_data.pit
            )
            music_controls.sort(key=operator.attrgetter("pos_tick"))
        return music_controls
