import dataclasses
import operator
from typing import Any, TypeAlias

from libresvip.core.constants import TICKS_IN_BEAT
from libresvip.core.lyric_phoneme.japanese import to_romaji
from libresvip.core.lyric_phoneme.japanese.vocaloid_xsampa import (
    legato_chars,
    romaji2xsampa,
)
from libresvip.core.time_sync import TimeSynchronizer
from libresvip.model.base import (
    Note,
    ParamCurve,
    Project,
    SingingTrack,
    SongTempo,
    TimeSignature,
    Track,
)
from libresvip.model.reset_time_axis import limit_bars
from libresvip.utils.binary.midi import bpm2tempo

from .constants import DEFAULT_PHONEME
from .options import OutputOptions
from .vocaloid_pitch import generate_for_vocaloid

MidiMessage: TypeAlias = dict[str, Any]


@dataclasses.dataclass
class VsqGenerator:
    options: OutputOptions
    synchronizer: TimeSynchronizer = dataclasses.field(init=False)
    first_bar_length: int = dataclasses.field(init=False)
    time_signatures: list[TimeSignature] = dataclasses.field(init=False)

    @property
    def tick_rate(self) -> float:
        return TICKS_IN_BEAT / self.options.ticks_per_beat

    def generate_project(self, project: Project) -> dict[str, Any]:
        project = limit_bars(project, 4096)
        self.synchronizer = TimeSynchronizer(project.song_tempo_list)
        mido_obj: dict[str, Any] = {
            "type": 1,
            "ticks_per_beat": self.options.ticks_per_beat,
        }
        self.first_bar_length = int(
            project.time_signature_list[0].bar_length(self.options.ticks_per_beat)
        )
        self.time_signatures = project.time_signature_list
        tracks: list[list[MidiMessage]] = []
        master_track: list[MidiMessage] = [
            {
                "time": 0,
                "__next": 0xFF,
                "status": 0xFF,
                "detail": {
                    "type": "meta",
                    "event_type": 0x03,
                    "data": {
                        "type": "track_name",
                        "name": "Master Track".encode(self.options.lyric_encoding, "replace"),
                    },
                },
            }
        ]
        self.generate_tempos(master_track, project.song_tempo_list)
        self.generate_time_signatures(master_track, project.time_signature_list)
        master_track.append(
            {
                "time": master_track[-1]["time"] if master_track else 0,
                "__next": 0xFF,
                "status": 0xFF,
                "detail": {
                    "type": "meta",
                    "event_type": 0x2F,
                    "data": {"type": "end_of_track"},
                },
            }
        )
        master_track.sort(key=operator.itemgetter("time"))
        tracks.append(master_track)
        tracks.extend(self.generate_tracks(project.track_list))
        self._convert_cumulative_to_delta(tracks)
        mido_obj["tracks"] = tracks
        return mido_obj

    @staticmethod
    def _convert_cumulative_to_delta(tracks: list[list[MidiMessage]]) -> None:
        for track in tracks:
            tick = 0
            for event in track:
                tick, event["time"] = event["time"], event["time"] - tick

    def generate_tempos(
        self, master_track: list[MidiMessage], song_tempo_list: list[SongTempo]
    ) -> None:
        master_track.extend(
            {
                "time": round(tempo.position / self.tick_rate),
                "__next": 0xFF,
                "status": 0xFF,
                "detail": {
                    "type": "meta",
                    "event_type": 0x51,
                    "data": {
                        "type": "set_tempo",
                        "tempo": bpm2tempo(tempo.bpm),
                    },
                },
            }
            for tempo in song_tempo_list
        )

    def generate_time_signatures(
        self,
        master_track: list[MidiMessage],
        time_signature_list: list[TimeSignature],
    ) -> None:
        ticks = 0
        prev_time_signature = None
        for time_signature in time_signature_list:
            if prev_time_signature is not None:
                ticks += round(
                    prev_time_signature.bar_length(self.options.ticks_per_beat)
                    * (time_signature.bar_index - prev_time_signature.bar_index)
                )
            master_track.append(
                {
                    "time": ticks,
                    "__next": 0xFF,
                    "status": 0xFF,
                    "detail": {
                        "type": "meta",
                        "event_type": 0x58,
                        "data": {
                            "type": "time_signature",
                            "numerator": time_signature.numerator,
                            "denominator": time_signature.denominator,
                            "clocks_per_click": 24,
                            "notated_32nd_notes_per_quarter": 8,
                        },
                    },
                }
            )
            prev_time_signature = time_signature

    def generate_tracks(self, tracks: list[Track]) -> list[list[MidiMessage]]:
        mido_tracks = []
        singing_tracks = [
            track
            for track in tracks
            if isinstance(track, SingingTrack) and len(track.note_list) > 0
        ]
        for i, track in enumerate(singing_tracks):
            if (mido_track := self.generate_track(track, i, len(singing_tracks))) is not None:
                mido_tracks.append(mido_track)
        return mido_tracks

    def generate_track(
        self, track: SingingTrack, track_index: int, tracks_count: int
    ) -> list[MidiMessage] | None:
        track_text = self.generate_track_text(track, track_index, tracks_count)
        mido_track = list[MidiMessage]()
        while len(track_text) != 0:
            event_id = len(mido_track)
            event_id_str = str(event_id).zfill(4)
            header = f"DM:{event_id_str}:"
            available_length = 0x7F - len(header)
            mido_track.append(
                {
                    "time": 0,
                    "__next": 0xFF,
                    "status": 0xFF,
                    "detail": {
                        "type": "meta",
                        "event_type": 0x01,
                        "data": {
                            "type": "text",
                            "text": (header + track_text[:available_length]).encode(
                                self.options.lyric_encoding, "replace"
                            ),
                        },
                    },
                }
            )
            track_text = track_text[available_length:]
        mido_track.append(
            {
                "time": 0,
                "__next": 0xFF,
                "status": 0xFF,
                "detail": {
                    "type": "meta",
                    "event_type": 0x2F,
                    "data": {"type": "end_of_track"},
                },
            }
        )
        return mido_track

    def generate_track_text(
        self,
        track: SingingTrack,
        track_index: int,
        tracks_count: int,
        measure_prefix: int = 1,
    ) -> str:
        notes_lines = []
        lyrics_lines = []
        tick_prefix = self.first_bar_length
        tick_lists = [note.start_pos + tick_prefix for note in track.note_list]
        for i, note in enumerate(track.note_list, start=1):
            number = str(i)
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
            lyric = note.lyric
            xsampa = (
                "-"
                if lyric in legato_chars
                else romaji2xsampa.get(to_romaji(lyric), DEFAULT_PHONEME)
            )
            lyrics_lines.extend(
                [
                    f"[h#{number.zfill(4)}]",
                    f"""L0="{lyric}","{xsampa}",0.000000,64,0,0""",
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
                result.extend([f"Feder{i}=0", f"Panpot{i}=0", f"Mute{i}=0", f"Solo{i}=0"])
        result.extend(["[EventList]", "0=ID#0000"])
        result.extend(
            f"{tick}=ID#{str(index).zfill(4)}" for index, tick in enumerate(tick_lists, start=1)
        )
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
            self.generate_pitch_text(track.edited_params.pitch, tick_prefix, track.note_list)
        )
        return "\n".join(result)

    def generate_pitch_text(
        self, pitch: ParamCurve, tick_prefix: int, note_list: list[Note]
    ) -> list[str]:
        result = []
        if pitch_raw_data := generate_for_vocaloid(
            pitch, note_list, self.time_signatures, self.first_bar_length, self.synchronizer
        ):
            if len(pitch_raw_data.pit):
                result.append("[PitchBendBPList]")
                result.extend(f"{pit.pos + tick_prefix}={pit.value}" for pit in pitch_raw_data.pit)
            if len(pitch_raw_data.pbs):
                result.append("[PitchBendSensBPList]")
                result.extend(f"{pbs.pos + tick_prefix}={pbs.value}" for pbs in pitch_raw_data.pbs)
        return result
