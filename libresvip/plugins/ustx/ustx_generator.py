import dataclasses
import math
from collections.abc import MutableSequence
from typing import Optional, cast

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
    PitchPoint,
    UCurve,
    UNote,
    UPitch,
    URendererSettings,
    USTXProject,
    UTempo,
    UTimeSignature,
    UTrack,
    UVibrato,
    UVoicePart,
    UWavePart,
)
from .options import OpenUtauEnglishPhonemizerCompatibility, OutputOptions
from .util import BasePitchGenerator
from .utils import lyric_util


@dataclasses.dataclass
class UstxGenerator:
    options: OutputOptions

    def generate_project(self, os_project: Project) -> USTXProject:
        # 节拍
        ustx_time_signatures = [
            self.generate_time_signature(ts) for ts in os_project.time_signature_list
        ]
        if not ustx_time_signatures:
            ustx_time_signatures.append(UTimeSignature(0, 4, 4))
        first_bar_length = int(
            1920 * ustx_time_signatures[0].beat_per_bar / ustx_time_signatures[0].beat_unit
        )

        # 曲速
        tempos = [self.generate_tempo(x, first_bar_length) for x in os_project.song_tempo_list]
        if not tempos:
            tempos.append(UTempo())

        ustx_project = USTXProject(
            ustx_version="0.6",
            tempos=tempos,
            bpm=tempos[0].bpm,
            time_signatures=ustx_time_signatures,
            voice_parts=[],
            wave_parts=[],
        )

        ustx_project.tracks = []
        for track_no, os_track in enumerate(os_project.track_list):
            ustx_project.tracks.append(self.generate_track(os_track))
            if isinstance(os_track, SingingTrack):  # 合成音轨
                ustx_project.tracks[-1].singer = os_track.ai_singer_name
                ustx_project.voice_parts.append(
                    self.generate_voice_part(os_track, track_no, ustx_project, first_bar_length)
                )
            elif wav_part := self.generate_wave_part(os_track, track_no):  # 伴奏音轨
                ustx_project.wave_parts.append(wav_part)
        return ustx_project

    @staticmethod
    def generate_tempo(os_tempo: SongTempo, first_bar_length: int = 1920) -> UTempo:
        return UTempo(
            position=max(os_tempo.position - first_bar_length, 0),
            bpm=os_tempo.bpm,
        )

    @staticmethod
    def generate_time_signature(
        os_time_signature: TimeSignature,
    ) -> UTimeSignature:
        return UTimeSignature(
            bar_position=os_time_signature.bar_index,
            beat_per_bar=os_time_signature.numerator,
            beat_unit=os_time_signature.denominator,
        )

    @staticmethod
    def generate_track(os_track: Track) -> UTrack:
        return UTrack(
            track_name=os_track.title,
            singer="",
            phonemizer="OpenUtau.Core.DefaultPhonemizer",  # 默认音素器
            renderer_settings=URendererSettings(renderer="CLASSIC"),
            mute=os_track.mute,
            solo=os_track.solo,
            volume=math.log10(os_track.volume) * 10,  # 绝对音量转对数音量
        )

    def generate_voice_part(
        self,
        os_track: SingingTrack,
        track_no: int,
        ustx_project: USTXProject,
        first_bar_length: int,
    ) -> UVoicePart:
        ustx_voice_part = UVoicePart(name=os_track.title, track_no=track_no, position=0, notes=[])
        if not os_track.note_list:
            return ustx_voice_part
        # 转换音符
        ustx_voice_part.notes.extend(self.generate_notes(os_track.note_list))
        # 转换音高曲线
        self.generate_pitch(
            ustx_voice_part,
            ustx_project,
            cast(
                MutableSequence[tuple[int, int]],
                os_track.edited_params.pitch.points.root,
            ),
            first_bar_length,
        )

        return ustx_voice_part

    @staticmethod
    def generate_wave_part(os_track: InstrumentalTrack, track_no: int) -> Optional[UWavePart]:
        if track_info := audio_track_info(os_track.audio_file_path):
            return UWavePart(
                name=os_track.title,
                track_no=track_no,
                position=os_track.offset,
                relative_path=os_track.audio_file_path,
                file_duration_ms=track_info.duration,
            )

    def generate_notes(self, os_notes: list[Note]) -> list[UNote]:
        notes: list[UNote] = []
        last_note_end_pos = -480  # 上一个音符的结束时间
        last_note_key_number = 60  # 上一个音符的音高
        last_syllable_index = 1
        for i, os_note in enumerate(os_notes):
            snap_first = last_note_end_pos >= os_note.start_pos
            y0 = (last_note_key_number - os_note.key_number) * 10 if snap_first else 0
            lyric = lyric_util.get_symbol_removed_lyric(os_note.lyric)  # 去除标点符号
            if os_note.pronunciation:  # 如果有发音, 则用发音
                lyric = os_note.pronunciation
            if lyric == "-":  # OpenUTAU中的连音符为+
                lyric = "+"
            elif lyric == "+":
                if (
                    self.options.english_phonemizer_compatibility
                    == OpenUtauEnglishPhonemizerCompatibility.ARPA
                ):
                    last_syllable_index += 1
                    lyric = f"+{last_syllable_index}"
                else:
                    for j in range(i - 1, 0, -1):
                        if os_notes[j].lyric == "-":
                            notes[j].lyric = "+~"
                        else:
                            break
            elif (
                self.options.english_phonemizer_compatibility
                == OpenUtauEnglishPhonemizerCompatibility.ARPA
            ):
                last_syllable_index = 1
            if len(lyric) == 2 and lyric_util.is_punctuation(lyric[1]):  # 删除标点符号
                lyric = lyric[:1]
            notes.append(
                UNote(
                    position=os_note.start_pos,
                    duration=os_note.length,
                    tone=os_note.key_number,
                    lyric=lyric,
                    pitch=UPitch(
                        snap_first=snap_first,
                        data=[
                            PitchPoint(x=-40, y=y0, shape="io"),
                            PitchPoint(x=0, y=0, shape="io"),
                        ],
                    ),
                    vibrato=UVibrato(
                        length=0,
                        period=175,
                        depth=25,
                        in_value=10,
                        out=10,
                        shift=0,
                        drift=0,
                    ),
                )
            )
            last_note_end_pos = os_note.end_pos
            last_note_key_number = os_note.key_number
        return notes

    @staticmethod
    def generate_pitch(
        part: UVoicePart,
        project: USTXProject,
        os_pitch: MutableSequence[tuple[int, int]],
        first_bar_length: int,
    ) -> None:
        pitch_start = BasePitchGenerator.pitch_start
        pitch_interval = BasePitchGenerator.pitch_interval
        base_pitch = BasePitchGenerator(project).base_pitch(part)  # 生成基础音高线
        pitch_end_x = len(base_pitch) * pitch_interval + first_bar_length + 1

        # 如果os_pitch为空
        if not os_pitch:
            os_pitch = [(0, -1), (pitch_end_x, -1)]
        # 如果os_pitch末尾不完整
        if os_pitch[-1][0] < pitch_end_x:
            os_pitch.append((os_pitch[-1][0], -1))
            os_pitch.append((pitch_end_x, -1))

        os_pitch_pointer = 0  # 当前位于输入os_pitch的第几个采样点
        pitd = UCurve(abbr="pitd", xs=[], ys=[])
        for i in range(len(base_pitch)):
            time = (
                i * pitch_interval + pitch_start
            )  # 当前openutau采样点的时间, 以tick为单位, 从0开始
            while os_pitch[os_pitch_pointer + 1][0] <= time + first_bar_length:
                os_pitch_pointer += 1
            # 此时, os_pitch_pointer对应的位置恰好在time之前(或等于), 区间[os_pitch_pointer,os_pitch_pointer+1)包含time
            if os_pitch[os_pitch_pointer][1] < 0:  # 间断点
                pitd.xs.append(time)
                pitd.ys.append(0)
            else:  # 有实际曲线存在
                x1 = os_pitch[os_pitch_pointer][0] - first_bar_length
                x2 = os_pitch[os_pitch_pointer + 1][0] - first_bar_length
                y1 = os_pitch[os_pitch_pointer][1]
                y2 = os_pitch[os_pitch_pointer + 1][1]
                pitd.xs.append(time)
                pitd.ys.append(
                    round((y2 - y1) * (time - x1) / (x2 - x1) + y1 - int(base_pitch[i]))
                )  # 线性插值
        if not pitd.is_empty:
            part.curves.append(pitd)
