import dataclasses
import pathlib
import wave
from typing import Annotated, cast

from construct import Container

from libresvip.core.constants import DEFAULT_BPM, TICKS_IN_BEAT
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
from libresvip.model.vocaloid.controller_models import ControllerCurve, ControllerEvent
from libresvip.model.vocaloid.pitch_handler import PitchBendData, VocaloidPitchHandler
from libresvip.utils.binary.midi import DEFAULT_PITCH_BEND_SENSITIVITY, PITCH_MAX_VALUE

from .constants import (
    BGM_CHANNELS,
    BGM_SAMPLE_RATE,
    BGM_SAMPLE_WIDTH,
    DEFAULT_DENOMINATOR,
    DEFAULT_NUMERATOR,
    EFFECT_TYPE_PIT,
    TICKS_IN_WHOLE_NOTE,
    VSP_PIT_CENTER,
    VSP_PIT_RANGE,
)
from .model import VocalinaStudioProjectFile
from .options import InputOptions


def packed_to_linear(packed: dict[str, int], ticks_per_beat: int, beats_per_bar: int) -> int:
    return (
        packed["high"] * ticks_per_beat * beats_per_bar
        + packed["mid"] * ticks_per_beat
        + packed["low"]
    )


def _raw_packed_to_linear(raw_value: int, ticks_per_beat: int, beats_per_bar: int) -> int:
    low = raw_value & 0xFFF
    mid = (raw_value >> 12) & 0xF
    high = (raw_value >> 16) & 0xFFFF
    return high * ticks_per_beat * beats_per_bar + mid * ticks_per_beat + low


def _vsp_pit_to_vocaloid_pit(value: int) -> int:
    return round((value - VSP_PIT_CENTER) / VSP_PIT_RANGE * PITCH_MAX_VALUE)


@dataclasses.dataclass
class VspParser:
    options: InputOptions
    path: pathlib.Path = dataclasses.field(default_factory=lambda: pathlib.Path())

    def parse_project(
        self, vsp_project: Annotated[Container, VocalinaStudioProjectFile]
    ) -> Project:
        time_signatures = self.parse_time_signatures(vsp_project)
        tempos = self.parse_tempos(vsp_project)
        if time_signatures:
            numerator = time_signatures[0].numerator
            denominator = time_signatures[0].denominator
        else:
            numerator = DEFAULT_NUMERATOR
            denominator = DEFAULT_DENOMINATOR
        ticks_per_beat = TICKS_IN_WHOLE_NOTE // denominator
        first_bar_length = (
            round(time_signatures[0].bar_length()) if time_signatures else TICKS_IN_BEAT * 4
        )
        synchronizer = TimeSynchronizer(tempos)

        pit_by_track = self._extract_pit_curves(vsp_project, ticks_per_beat, numerator)
        track_list: list[Track] = list(
            self._parse_tracks(
                vsp_project,
                ticks_per_beat,
                numerator,
                time_signatures,
                first_bar_length,
                synchronizer,
                pit_by_track,
            )
        )

        if self.options.import_instrumental_track:
            bgm_track = self._parse_bgm(vsp_project)
            if bgm_track is not None:
                track_list.append(bgm_track)

        return Project(
            time_signature_list=time_signatures,
            song_tempo_list=tempos,
            track_list=track_list,
        )

    @staticmethod
    def parse_time_signatures(
        vsp_project: Annotated[Container, VocalinaStudioProjectFile],
    ) -> list[TimeSignature]:
        return [
            TimeSignature(
                bar_index=entry["tick"],
                numerator=entry["numerator"] or DEFAULT_NUMERATOR,
                denominator=entry["denominator"] or DEFAULT_DENOMINATOR,
            )
            for entry in vsp_project["time_signatures"]["data"]
        ]

    @staticmethod
    def parse_tempos(
        vsp_project: Annotated[Container, VocalinaStudioProjectFile],
    ) -> list[SongTempo]:
        return [
            SongTempo(
                position=entry["tick"],
                bpm=entry["tempo_value"] or DEFAULT_BPM,
            )
            for entry in vsp_project["tempos"]["data"]
        ]

    @staticmethod
    def _extract_pit_curves(
        vsp_project: Annotated[Container, VocalinaStudioProjectFile],
        ticks_per_beat: int,
        beats_per_bar: int,
    ) -> dict[int, list[ControllerEvent]]:
        pit_by_track: dict[int, list[ControllerEvent]] = {}
        for block in vsp_project["effects"]["data"]["blocks"]:
            if block["effect_type"] != EFFECT_TYPE_PIT:
                continue
            track_idx = block["track_index"]
            if track_idx > 0xFFF0:
                continue
            events = []
            for entry in block["entries"]:
                pos = _raw_packed_to_linear(entry["packed_value"], ticks_per_beat, beats_per_bar)
                raw_value = entry["bypass"]
                if raw_value >= 0x80000000:
                    raw_value -= 0x100000000
                pit = _vsp_pit_to_vocaloid_pit(raw_value)
                events.append(ControllerEvent(pos=pos, value=pit))
            pit_by_track[track_idx] = events
        return pit_by_track

    def _parse_tracks(
        self,
        vsp_project: Annotated[Container, VocalinaStudioProjectFile],
        ticks_per_beat: int,
        beats_per_bar: int,
        time_signatures: list[TimeSignature],
        first_bar_length: int,
        synchronizer: TimeSynchronizer,
        pit_by_track: dict[int, list[ControllerEvent]],
    ) -> list[SingingTrack]:
        tracks_data = vsp_project["tracks"]["data"]
        track_entries = tracks_data["tracks"]
        notes_data = vsp_project["notes"]["data"]

        track_notes_map: dict[int, list[dict[str, object]]] = {}
        for note in notes_data["notes"]:
            track_idx = cast("int", note["track_index"])
            if track_idx not in track_notes_map:
                track_notes_map[track_idx] = []
            track_notes_map[track_idx].append(note)

        singing_tracks = []
        for track_idx, track_entry in enumerate(track_entries):
            track_notes = track_notes_map.get(track_idx, [])
            note_list = []
            for note_entry in track_notes:
                packed_start = cast("dict[str, int]", note_entry["packed_start"])
                packed_end = cast("dict[str, int]", note_entry["packed_end"])
                start_pos = packed_to_linear(packed_start, ticks_per_beat, beats_per_bar)
                end_pos = packed_to_linear(packed_end, ticks_per_beat, beats_per_bar)
                note_list.append(
                    Note(
                        start_pos=start_pos,
                        length=end_pos - start_pos,
                        key_number=cast("int", note_entry["note_number"]),
                        lyric=cast("str", note_entry["lyrics"]),
                    )
                )
            volume_raw = track_entry["volume"]
            pan_raw = track_entry["pan"]
            singing_track = SingingTrack(
                title=track_entry["track_name"],
                ai_singer_name=track_entry["singer_name"],
                note_list=note_list,
                volume=volume_raw / 100.0,
                pan=(pan_raw - 50) / 50.0,
            )

            if self.options.import_pitch and note_list:
                pitch = self._parse_pitch(
                    track_idx,
                    note_list,
                    time_signatures,
                    first_bar_length,
                    synchronizer,
                    pit_by_track,
                )
                if pitch is not None:
                    singing_track.edited_params.pitch = pitch

            singing_tracks.append(singing_track)
        return singing_tracks

    def _parse_bgm(
        self, vsp_project: Annotated[Container, VocalinaStudioProjectFile]
    ) -> InstrumentalTrack | None:
        bgm_data = vsp_project["bgm"]["data"]
        raw_data: bytes = bgm_data["raw_data"]
        if not raw_data or not self.path.name or all(b == 0 for b in raw_data[:64]):
            return None

        audio_path = self.path.with_suffix(".wav")
        if (
            self.options.extract_audio
            and not hasattr(self.path, "protocol")
            and not audio_path.exists()
        ):
            with wave.open(str(audio_path), "wb") as wf:
                wf.setnchannels(BGM_CHANNELS)
                wf.setsampwidth(BGM_SAMPLE_WIDTH)
                wf.setframerate(BGM_SAMPLE_RATE)
                wf.writeframes(raw_data)

        if audio_path.exists():
            return InstrumentalTrack(
                title=self.path.stem,
                audio_file_path=str(audio_path),
            )
        return None

    @staticmethod
    def _parse_pitch(
        track_idx: int,
        note_list: list[Note],
        time_signatures: list[TimeSignature],
        first_bar_length: int,
        synchronizer: TimeSynchronizer,
        pit_by_track: dict[int, list[ControllerEvent]],
    ) -> ParamCurve | None:
        pit_events = pit_by_track.get(track_idx, [])
        if not pit_events:
            return None

        handler = VocaloidPitchHandler(
            synchronizer=synchronizer,
            note_list=note_list,
            time_signature_list=time_signatures,
            first_bar_length=first_bar_length,
        )
        pit_curve = ControllerCurve(
            name="pitch_bend",
            events=pit_events,
            default_value=0,
            min_value=-PITCH_MAX_VALUE - 1,
            max_value=PITCH_MAX_VALUE,
        )
        pbs_curve = ControllerCurve(
            name="pitch_bend_sens",
            events=[],
            default_value=DEFAULT_PITCH_BEND_SENSITIVITY,
            min_value=1,
            max_value=24,
        )
        pitch_data = PitchBendData(pit=pit_curve, pbs=pbs_curve)
        return handler.to_absolute_pitch([pitch_data], [0])
