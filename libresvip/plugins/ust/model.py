from typing import Any, Literal

import tatsu
from pydantic import BaseModel, Field
from tatsu.grammars import Grammar
from tatsu.objectmodel import Node
from tatsu.walkers import NodeWalker

from .constants import MAX_ACCEPTED_BPM


def get_ust_grammar() -> Grammar:
    return tatsu.compile(
        """
        @@grammar::Ust
        @@whitespace :: None

        ust_project::ust_project
            =
            header:[ust_header]
            setting_section:ust_setting_section
            tracks:{ust_track}* {newline}* $;
        ust_header::ust_header
            =
            "[#VERSION]" newline
            "UST Version" ["="] ust_version:float
            [newline "Charset" "=" charset:value] ;
        ust_setting_section::ust_setting_section
            = [newline]
            "[#SETTING]"
            setting_lines:{newline ust_setting_line}* ;
        ust_setting_line::ust_setting_line
            =
            (key:"UstVersion" "=" value:float)
            | (key:"Tempo" "=" value:value)
            | (key:"TimeSignatures" "=" value:(ust_time_signature {"," ust_time_signature}*) [","])
            | (key:"Tracks" "=" value:int)
            | (key:?"Project(Name)?" "=" value:value)
            | (key:"VoiceDir" "=" value:value)
            | (key:"OutFile" "=" value:value)
            | (key:"CacheDir" "=" value:value)
            | (key:"Tool1" "=" value:value)
            | (key:"Tool2" "=" value:value)
            | (key:"Mode2" "=" value:bool)
            | (key:"Autoren" "=" value:bool)
            | (key:"MapFirst" "=" value:bool)
            | (key:"Flags" "=" value:value)
            | (key:"Charset" "=" value:value) ;
        ust_time_signature::ust_time_signature
            =
            "(" numerator:int
            "/" denominator:int
            "/" bar_index:int ")" ;
        ust_track
            = notes:{ust_note}* [newline ust_track_end] ;
        ust_note::ust_note
            =
            newline head:ust_note_head
            attrs:{newline ust_note_attr {" "}*}* ;
        ust_note_head
            = "[#" note_type:?"(\\d+|PREV|NEXT|INSERT|DELETE)" "]" ;
        ust_track_end
            = "[#TRACKEND]" ;
        utau_pitch_bend_mode::utau_pitch_bend_mode
            = "s" | "r" | "j" | "null" | () ;
        ust_pitch_bend_type
            = "5" | "OldData" ;
        ust_note_attr
            =
            (key:"Length" "=" value:float)
            | (key:"Duration" "=" value:float)
            | (key:"Lyric" "=" value:value)
            | (key:"NoteNum" "=" value:int)
            | (key:"Delta" "=" value:int)
            | (key:"PreUtterance" "=" value:value)
            | (key:"VoiceOverlap" "=" value:float)
            | (key:"Intensity" "=" value:float)
            | (key:?"Modulation|Moduration" "=" value:float)
            | (key:"StartPoint" "=" value:float)
            | (key:"Envelope" "=" value:ust_envelope)
            | (key:"Tempo" "=" value:value)
            | (key:"Velocity" "=" value:float)
            | (key:"Label" "=" value:value)
            | (key:"Flags" "=" value:value)
            | (key:"PBType" "=" value:ust_pitch_bend_type)
            | (key:"PBStart" "=" value:float)
            | (key:?"Piches|Pitches|PitchBend" "=" value:(int {"," int}*) )
            | (key:"PBS" "=" value:(optional_float {?";|," optional_float}*))
            | (key:"PBW" "=" value:(optional_float {"," optional_float}*))
            | (key:"PBY" "=" value:(optional_float {"," optional_float}*))
            | (key:"VBR" "=" value:(optional_float {"," optional_float}*))
            | (key:"PBM" "=" value:(utau_pitch_bend_mode {"," utau_pitch_bend_mode}*))
            | (key:"stptrim" "=" value:float)
            | (key:"layer" "=" value:int)
            | (key:"@preuttr" "=" value:float)
            | (key:"@overlap" "=" value:float)
            | (key:"@stpoint" "=" value:float)
            | (key:"@filename" "=" value:value)
            | (key:"@alias" "=" value:value)
            | (key:"@cache" "=" value:value)
            | (key:/\\$?[^=\r\n]+/ "=" value:value)
            | (!(ust_note_head | ust_track_end) key:() value:value) ;
        ust_envelope::ust_envelope
            = p1:float "," p2:float "," p3:float "," v1:float "," v2:float "," v3:float "," v4:float
            (
                ",%," p4:[float] ["," p5:[float] ["," v5:[float]]] |
                ",," p4:float |
                ",%" |
                other_points:{"," float}*
            ) ;
        value = /[^\r\n]*/ ;
        newline = /\r?\n/ ;
        bool::bool = "1" | "0" | "True" | "False" ;
        optional_float::optional_float = float | "null" | () ;
        float::float = /[-]?(?:(?:\\d+(?:\\.\\d*)?)|(?:\\.\\d+))(?:[eE][-+]?\\d+)?/ ;
        int::int = /[-]?[0-9]+/ ;
        """,
        asmodel=True,
    )


UTAUPitchBendMode = Literal["s", "r", "j", ""]

UTAUPitchBendType = Literal["OldData", "5"]

OptionalFloat = float | Literal[""]


class UtauNoteVibrato(BaseModel):
    length: float  # percentage of the note's length
    period: float  # milliSec
    depth: float = 0  # cent
    fade_in: float = 0  # percentage of the vibrato's length
    fade_out: float = 0  # percentage of the vibrato's length
    phase_shift: float = 0  # percentage of period
    shift: float = 0  # percentage of depth


class UTAUEnvelope(BaseModel):
    p1: float
    p2: float
    p3: float
    v1: float
    v2: float
    v3: float
    v4: float
    p4: float | None = None
    p5: float | None = None
    v5: float | None = None
    other_points: list[float] | None = None


class UTAUNote(BaseModel):
    note_type: str
    length: int
    lyric: str
    note_num: int
    duration: int | None = None
    delta: int | None = None
    pre_utterance: str | None = None
    label: str | None = None
    flags: str | None = None
    envelope: UTAUEnvelope | None = None
    voice_overlap: float | None = None
    intensity: float | None = None
    modulation: float | None = None
    start_point: float | None = None
    tempo: float | None = None
    velocity: float | None = None
    pitchbend_start: float | None = None
    pitchbend_type: UTAUPitchBendType | None = None
    pitch_bend_points: list[int] = Field(default_factory=list)
    pbs: list[OptionalFloat] = Field(default_factory=list)
    pbw: list[OptionalFloat] = Field(default_factory=list)
    pby: list[OptionalFloat] = Field(default_factory=list)
    pbm: list[UTAUPitchBendMode] = Field(default_factory=list)
    vbr: UtauNoteVibrato | None = None
    stp_trim: float | None = None
    layer: int | None = None
    at_preutterance: float | None = None
    at_overlap: float | None = None
    at_start_point: float | None = None
    sample_filename: str | None = None
    alias: str | None = None
    cache_location: str | None = None


class UTAUTrack(BaseModel):
    notes: list[UTAUNote] = Field(default_factory=list)


class UTAUTimeSignature(BaseModel):
    numerator: int
    denominator: int
    bar_index: int


class UTAUProject(BaseModel):
    ust_version: float | None = 1.2
    project_name: str = "New Project"
    track_count: int = 1
    pitch_mode2: bool = False
    charset: str | None = None
    tempo: float | None = None
    voice_dir: str | None = None
    out_file: str | None = None
    cache_dir: str | None = None
    tool1: str | None = None
    tool2: str | None = None
    flags: str | None = None
    autoren: bool | None = None
    map_first: bool | None = None
    time_signatures: list[UTAUTimeSignature] = Field(default_factory=list)
    track: list[UTAUTrack] = Field(default_factory=list)


class UstWalker(NodeWalker):
    def walk_ust_project(self, node: Node) -> bool:
        pending_metadata: dict[str, Any] = {"track": []}
        if node.header is not None:
            pending_metadata["ust_version"] = node.header.ust_version
            pending_metadata["charset"] = node.header.charset
        for each in node.setting_section.setting_lines:
            line = each[1]
            match line.key:
                case "Tempo":
                    if (tempo_value := self.tempo2bpm(line.value)) < MAX_ACCEPTED_BPM:
                        pending_metadata["tempo"] = tempo_value
                case "UstVersion":
                    pending_metadata["ust_version"] = line.value
                case "Tracks":
                    pending_metadata["track_count"] = line.value
                case "Project" | "ProjectName":
                    pending_metadata["project_name"] = line.value
                case "Mode2":
                    pending_metadata["pitch_mode2"] = self.walk(line.value)
                case "VoiceDir":
                    pending_metadata["voice_dir"] = line.value
                case "OutFile":
                    pending_metadata["out_file"] = line.value
                case "CacheDir":
                    pending_metadata["cache_dir"] = line.value
                case "Tool1":
                    pending_metadata["tool1"] = line.value
                case "Tool2":
                    pending_metadata["tool2"] = line.value
                case "Autoren":
                    pending_metadata["autoren"] = self.walk(line.value)
                case "MapFirst":
                    pending_metadata["map_first"] = self.walk(line.value)
                case "Flags":
                    pending_metadata["flags"] = line.value
                case "TimeSignatures":
                    values = self.walk(line.value)
                    pending_metadata["time_signatures"] = [
                        values[0],
                        *(each[1] for each in values[1]),
                    ]
        for track in node.tracks:
            if ust_track := self.walk(track):
                pending_metadata["track"].append(ust_track)
        return UTAUProject(**pending_metadata)

    def walk_ust_time_signature(self, node: Node) -> UTAUTimeSignature:
        return UTAUTimeSignature(
            numerator=node.numerator, denominator=node.denominator, bar_index=node.bar_index
        )

    def walk_ust_envelope(self, node: Node) -> UTAUEnvelope:
        extra_kwargs = {}
        if hasattr(node, "p4"):
            extra_kwargs["p4"] = node.p4
        if hasattr(node, "p5"):
            extra_kwargs["p5"] = node.p5
        if hasattr(node, "v5"):
            extra_kwargs["v5"] = node.v5
        if hasattr(node, "other_points"):
            extra_kwargs["other_points"] = [i[1] for i in node.other_points]
        return UTAUEnvelope(
            p1=node.p1,
            p2=node.p2,
            p3=node.p3,
            v1=node.v1,
            v2=node.v2,
            v3=node.v3,
            v4=node.v4,
            **extra_kwargs,
        )

    #     return envelope
    @staticmethod
    def tempo2bpm(tempo: str) -> float:
        return float(tempo.replace(",", "."))

    def walk_optional_float(self, node: Node) -> OptionalFloat:
        return node.ast if isinstance(node.ast, float) else ""

    def walk_utau_pitch_bend_mode(self, node: Node) -> UTAUPitchBendMode:
        return node.ast if node.ast in ["s", "r", "j"] else ""

    def walk_ust_track(self, node: Node) -> UTAUTrack | None:
        if ust_notes := [self.walk(i) for i in node.notes]:
            return UTAUTrack(notes=ust_notes)

    def walk_ust_note(self, node: Node) -> UTAUNote:
        pending_note_attrs = {}
        pending_note_attrs["note_type"] = node.head.note_type
        for each in node.attrs:
            attr = each[1]
            match attr.key:
                case "Length":
                    pending_note_attrs["length"] = attr.value
                case "Lyric":
                    pending_note_attrs["lyric"] = attr.value
                case "NoteNum":
                    pending_note_attrs["note_num"] = attr.value
                case "Tempo":
                    pending_note_attrs["tempo"] = self.tempo2bpm(attr.value)
                case "PBType":
                    pending_note_attrs["pitchbend_type"] = attr.value
                case "PBStart":
                    pending_note_attrs["pitchbend_start"] = attr.value
                case "Modulation" | "Moduration":
                    pending_note_attrs["modulation"] = attr.value
                case "Envelope":
                    pending_note_attrs["envelope"] = self.walk(attr.value)
                case "Flags":
                    pending_note_attrs["flags"] = attr.value
                case "Intensity":
                    pending_note_attrs["intensity"] = attr.value
                case "Velocity":
                    pending_note_attrs["velocity"] = attr.value
                case "PreUtterance":
                    pending_note_attrs["pre_utterance"] = attr.value
                case "StartPoint":
                    pending_note_attrs["start_point"] = attr.value
                case "Delta":
                    pending_note_attrs["delta"] = attr.value
                case "Duration":
                    pending_note_attrs["duration"] = attr.value
                case "VoiceOverlap":
                    pending_note_attrs["voice_overlap"] = attr.value
                case "Label":
                    pending_note_attrs["label"] = attr.value
                case "Piches" | "Pitches" | "PitchBend":
                    pending_note_attrs["pitch_bend_points"] = [
                        attr.value[0],
                        *(i[1] for i in attr.value[1]),
                    ]
                case "PBS" | "PBM" | "PBW" | "PBY":
                    pending_note_attrs[attr.key.lower()] = [
                        self.walk(attr.value[0]),
                        *(self.walk(i[1]) for i in attr.value[1]),
                    ]
                case "VBR":
                    vibrato_kwargs = {
                        "length": self.walk(attr.value[0]),
                    }
                    for i, v in enumerate(attr.value[1]):
                        value = self.walk(v[1])
                        if isinstance(value, float):
                            if i == 0:
                                vibrato_kwargs["period"] = value
                            elif i == 1:
                                vibrato_kwargs["depth"] = value
                            elif i == 2:
                                vibrato_kwargs["fade_in"] = value
                            elif i == 3:
                                vibrato_kwargs["fade_out"] = value
                            elif i == 4:
                                vibrato_kwargs["phase_shift"] = value
                            elif i == 5:
                                vibrato_kwargs["shift"] = value
                    pending_note_attrs["vibrato"] = UtauNoteVibrato(**vibrato_kwargs)
                case "stptrim":
                    pending_note_attrs["stp_trim"] = attr.value
                case "layer":
                    pending_note_attrs["layer"] = attr.value
                case "@preuttr":
                    pending_note_attrs["at_preutterance"] = attr.value
                case "@overlap":
                    pending_note_attrs["at_overlap"] = attr.value
                case "@stpoint":
                    pending_note_attrs["at_start_point"] = attr.value
                case "@filename":
                    pending_note_attrs["sample_filename"] = attr.value
                case "@alias":
                    pending_note_attrs["alias"] = attr.value
                case "@cache":
                    pending_note_attrs["cache_location"] = attr.value
                # case _:
                #     print(f"Unknown attr: {attr.key} = {attr.value}")
        return UTAUNote(**pending_note_attrs)
