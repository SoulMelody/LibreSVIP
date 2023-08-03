import dataclasses
import operator
from typing import Optional

import mido

from libresvip.core.constants import (
    DEFAULT_JAPANESE_LYRIC,
    DEFAULT_PHONEME,
    TICKS_IN_BEAT,
)
from libresvip.core.lyric_phoneme.japanese import is_kana, is_romaji
from libresvip.model.base import (
    Note,
    ParamCurve,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
    Track,
)

from .options import OutputOptions
from .vocaloid_pitch import generate_for_vocaloid


@dataclasses.dataclass
class VsqGenerator:
    options: OutputOptions

    @property
    def tick_rate(self) -> float:
        if self.options is not None:
            return TICKS_IN_BEAT / self.options.ticks_per_beat
        return 1

    def generate_project(self, project: Project) -> mido.MidiFile:
        mido_obj = mido.MidiFile(charset="latin1")
        mido_obj.ticks_per_beat = self.options.ticks_per_beat
        master_track = mido.MidiTrack()
        self.generate_tempos(master_track, project.song_tempo_list)
        self.generate_time_signatures(master_track, project.time_signature_list)
        master_track.sort(key=operator.attrgetter("time"))
        mido_obj.tracks.append(master_track)
        mido_obj.tracks.extend(self.generate_tracks(project.track_list))
        self._convert_cumulative_to_delta(mido_obj.tracks)
        return mido_obj

    @staticmethod
    def _convert_cumulative_to_delta(tracks: list[mido.MidiTrack]) -> None:
        for track in tracks:
            tick = 0
            for event in track:
                tick, event.time = event.time, event.time - tick

    def generate_tempos(
        self, master_track: mido.MidiTrack, song_tempo_list: list[SongTempo]
    ) -> None:
        for tempo in song_tempo_list:
            master_track.append(
                mido.MetaMessage(
                    "set_tempo",
                    tempo=mido.bpm2tempo(tempo.bpm),
                    time=round(tempo.position / self.tick_rate),
                )
            )

    def generate_time_signatures(
        self, master_track: mido.MidiTrack, time_signature_list: list[TimeSignature]
    ) -> None:
        prev_ticks = 0
        for time_signature in time_signature_list:
            master_track.append(
                mido.MetaMessage(
                    "time_signature",
                    numerator=time_signature.numerator,
                    denominator=time_signature.denominator,
                    time=prev_ticks,
                )
            )
            prev_ticks += round(
                time_signature.bar_index
                * self.options.ticks_per_beat
                * time_signature.numerator
            )

    def generate_tracks(self, tracks: list[Track]) -> list[mido.MidiTrack]:
        mido_tracks = []
        singing_tracks = [
            track
            for track in tracks
            if isinstance(track, SingingTrack) and len(track.note_list) > 0
        ]
        for i, track in enumerate(singing_tracks):
            if (
                mido_track := self.generate_track(track, i, len(singing_tracks))
            ) is not None:
                mido_tracks.append(mido_track)
        return mido_tracks

    def generate_track(
        self, track: SingingTrack, track_index: int, tracks_count: int
    ) -> Optional[mido.MidiTrack]:
        track_text = self.generate_track_text(track, track_index, tracks_count)
        track_text = track_text.encode("shift-jis", errors="ignore").decode("latin1")
        mido_track = mido.MidiTrack()
        while not len(track_text) == 0:
            event_id = len(mido_track)
            event_id_str = str(event_id).zfill(4)
            header = f"DM:{event_id_str}:"
            available_length = 0x7F - len(header)
            mido_track.append(
                mido.MetaMessage(
                    "text",
                    text=header + track_text[:available_length],
                    time=0,
                )
            )
            track_text = track_text[available_length:]
        mido_track.append(mido.MetaMessage("end_of_track"))
        return mido_track

    def generate_track_text(
        self,
        track: SingingTrack,
        track_index: int,
        tracks_count: int,
        tick_prefix: int = 0,
        measure_prefix: int = 0,
    ) -> str:
        notes_lines = []
        lyrics_lines = []
        tick_lists = [note.start_pos + tick_prefix for note in track.note_list]
        for i, note in enumerate(track.note_list):
            number = f"{i + 1}"
            notes_lines.extend(
                [
                    f"[ID#{number.zfill(4)}]",
                    "Type=Anote",
                    f"Length={note.length}",
                    f"Note#={note.key_number}",
                    "Dynamics=64",
                    "PMBendDepth=0",
                    "PMBendLength=0",
                    "PMbPortamentoUse=0",
                    "DEMdecGainRate=0",
                    "DEMaccent=0",
                    f"LyricHandle=h#{number.zfill(4)}",
                ]
            )
            lyric = (
                note.lyric
                if is_kana(note.lyric) or is_romaji(note.lyric)
                else DEFAULT_JAPANESE_LYRIC
            )
            lyrics_lines.extend(
                [
                    f"[h#{number.zfill(4)}]",
                    f"""L0="{lyric}","{note.pronunciation or DEFAULT_PHONEME}",0.000000,64,0,0""",
                ]
            )
        result = [
            "[Common]",
            "Version=DSB301",
            f"Name={track.title}",
            "Color=181,162,123",
            "DynamicsMode=1",
            "PlayMode=1",
        ]
        if track_index == 0:
            result.extend(
                [
                    "[Master]",
                    f"PreMeasure={measure_prefix}",
                    "[Mixer]",
                    "MasterFeder=0",
                    "MasterPanpot=0",
                    "MasterMute=0",
                    "OutputMode=0",
                    f"Tracks={tracks_count}",
                ]
            )
            for i in range(tracks_count):
                result.extend(
                    [f"Feder{i}=0", f"Panpot{i}=0", f"Mute{i}=0", f"Solo{i}=0"]
                )
        result.extend(["[EventList]", "0=ID#0000"])
        for index, tick in enumerate(tick_lists):
            result.append(f"{tick}=ID#{str(index + 1).zfill(4)}")
        result.extend(
            [
                f"{track.note_list[-1].end_pos + tick_prefix}=EOS",
                "[ID#0000]",
                "Type=Singer",
                "IconHandle=h#0000",
            ]
        )
        result.extend(notes_lines)
        result.extend(
            [
                "[h#0000]",
                "IconID=$07010000",
                f"IDS={track.ai_singer_name}",
                "Original=0",
                "Caption=",
                "Length=1",
                "Language=0",
                "Program=0",
            ]
        )
        result.extend(lyrics_lines)
        result.extend(
            self.generate_pitch_text(
                track.edited_params.pitch, tick_prefix, track.note_list
            )
        )
        return "\n".join(result)

    def generate_pitch_text(
        self, pitch: ParamCurve, tick_prefix: int, note_list: list[Note]
    ) -> list[str]:
        result = []
        if pitch_raw_data := generate_for_vocaloid(pitch, note_list):
            if len(pitch_raw_data.pit):
                result.append("[PitchBendBPList]")
                result.extend(
                    f"{pit.pos + tick_prefix}={pit.value}" for pit in pitch_raw_data.pit
                )
            if len(pitch_raw_data.pbs):
                result.append("[PitchBendSensBPList]")
                result.extend(
                    f"{pbs.pos + tick_prefix}={pbs.value}" for pbs in pitch_raw_data.pbs
                )
        return result
