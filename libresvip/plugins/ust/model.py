import ast
from typing import Any, Literal, Optional, Union

from parsimonious import Grammar, NodeVisitor
from parsimonious.nodes import Node
from pydantic import BaseModel, Field

from .constants import MAX_ACCEPTED_BPM

ust_grammar = Grammar(
    r"""
    ust_project =
        ust_header?
        ust_setting_section
        ust_track*
        newline*

    ust_header =
        "[#VERSION]"
        newline "UST Version" "="? float
        (newline "Charset" "=" value)?

    ust_setting_section =
        newline? "[#SETTING]"
        (newline ust_setting_line)*

    ust_time_signature =
        "(" int "/" int  "/" int ")"

    ust_setting_line =
        ("UstVersion" "=" float) /
        ("Tempo" "=" value) /
        ("TimeSignatures" "=" ust_time_signature ("," ust_time_signature)* ","?) /
        ("Tracks" "=" int) /
        (~"Project(Name)?" "=" value) /
        ("VoiceDir" "=" value) /
        ("OutFile" "=" value) /
        ("CacheDir" "=" value) /
        ("Tool1" "=" value) /
        ("Tool2" "=" value) /
        ("Mode2" "=" bool) /
        ("Autoren" "=" bool) /
        ("MapFirst" "=" bool) /
        ("Flags" "=" value)

    ust_track =
        ust_note*
        (newline ust_track_end)?

    ust_note =
        newline ust_note_head
        (newline ust_note_attr " "*)*

    ust_note_head =
        "[#" ~"(\\d+|PREV|NEXT|INSERT|DELETE)" "]"

    ust_track_end = "[#TRACKEND]"

    ust_tag_entry = ust_note_head / ust_track_end

    utau_pitch_bend_mode =
        "s" / "r" / "j" / "null" / ""

    ust_pitch_bend_type =
        "5" / "OldData"

    ust_note_attr =
        ("Length" "=" float) /
        ("Duration" "=" float) /
        ("Lyric" "=" value) /
        ("NoteNum" "=" int) /
        ("Delta" "=" int) /
        ("PreUtterance" "=" value) /
        ("VoiceOverlap" "=" float) /
        ("Intensity" "=" float) /
        (~"Modulation|Moduration" "=" float) /
        ("StartPoint" "=" float) /
        ("Envelope" "=" ust_envelope) /
        ("Tempo" "=" value) /
        ("Velocity" "=" float) /
        ("Label" "=" value) /
        ("Flags" "=" value) /
        ("PBType" "=" ust_pitch_bend_type) /
        ("PBStart" "=" float) /
        (~"Piches|Pitches|PitchBend" "=" int ("," int)* ) /
        ("PBS" "=" optional_float (~";|," optional_float)*) /
        ("PBW" "=" optional_float ("," optional_float)*) /
        ("PBY" "=" optional_float ("," optional_float)*) /
        ("VBR" "=" optional_float ("," optional_float)*) /
        ("PBM" "=" utau_pitch_bend_mode ("," utau_pitch_bend_mode)* ) /
        ("stptrim" "=" float) /
        ("layer" "=" int) /
        ("@preuttr" "=" float) /
        ("@overlap" "=" float) /
        ("@stpoint" "=" float) /
        ("@filename" "=" value) /
        ("@alias" "=" value) /
        ("@cache" "=" value) /
        (~"\\$?[^=\r\n]+" "=" value) /
        (!ust_tag_entry value)

    ust_envelope =
        float ("," float){6}
        (
            (",%," float ("," float ("," float)?)?) /
            (",," float) /
            ",%" /
            ("," float)*
        )

    value = ~"[^\r\n]*"
    newline = ~"\r?\n"
    bool = "1" / "0" / "True" / "False"
    optional_float = float / "null" / ""
    float = ((int frac?) / ("-"? frac)) (~"[eE][+-]?" digits)?
    int = "-"? ((digit1to9 digits) / digit)
    frac = "." digits
    digits = digit+
    digit1to9 = ~"[1-9]"
    digit = ~"[0-9]"
    """
)

UTAUPitchBendMode = Literal["s", "r", "j", ""]

UTAUPitchBendType = Literal["OldData", "5"]

OptionalFloat = Union[float, Literal[""]]


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
    p4: Optional[float] = None
    p5: Optional[float] = None
    v5: Optional[float] = None
    other_points: Optional[list[float]] = None


class UTAUNote(BaseModel):
    note_type: str
    length: int
    lyric: str
    note_num: int
    duration: Optional[int] = None
    delta: Optional[int] = None
    pre_utterance: Optional[str] = None
    label: Optional[str] = None
    flags: Optional[str] = None
    envelope: Optional[UTAUEnvelope] = None
    voice_overlap: Optional[float] = None
    intensity: Optional[float] = None
    modulation: Optional[float] = None
    start_point: Optional[float] = None
    tempo: Optional[float] = None
    velocity: Optional[float] = None
    pitchbend_start: Optional[float] = None
    pitchbend_type: Optional[UTAUPitchBendType] = None
    pitch_bend_points: list[int] = Field(default_factory=list)
    pbs: list[OptionalFloat] = Field(default_factory=list)
    pbw: list[OptionalFloat] = Field(default_factory=list)
    pby: list[OptionalFloat] = Field(default_factory=list)
    pbm: list[UTAUPitchBendMode] = Field(default_factory=list)
    vbr: Optional[UtauNoteVibrato] = None
    stp_trim: Optional[float] = None
    layer: Optional[int] = None
    at_preutterance: Optional[float] = None
    at_overlap: Optional[float] = None
    at_start_point: Optional[float] = None
    sample_filename: Optional[str] = None
    alias: Optional[str] = None
    cache_location: Optional[str] = None


class UTAUTrack(BaseModel):
    notes: list[UTAUNote] = Field(default_factory=list)


class UTAUTimeSignature(BaseModel):
    numerator: int
    denominator: int
    bar_index: int


class UTAUProject(BaseModel):
    ust_version: Optional[float] = 1.2
    project_name: str = "New Project"
    track_count: int = 1
    pitch_mode2: bool = False
    charset: Optional[str] = None
    tempo: Optional[float] = None
    voice_dir: Optional[str] = None
    out_file: Optional[str] = None
    cache_dir: Optional[str] = None
    tool1: Optional[str] = None
    tool2: Optional[str] = None
    flags: Optional[str] = None
    autoren: Optional[bool] = None
    map_first: Optional[bool] = None
    time_signatures: list[UTAUTimeSignature] = Field(default_factory=list)
    track: list[UTAUTrack] = Field(default_factory=list)


class UstVisitor(NodeVisitor):
    def __init__(self) -> None:
        super().__init__()
        self.pending_metadata: dict[str, Any] = {}
        self.pending_note_attrs: dict[str, Any] = {}
        self.pending_notes: list[UTAUNote] = []

    @staticmethod
    def tempo2bpm(tempo: str) -> float:
        return float(tempo.replace(",", "."))

    def visit_ust_project(self, node: Node, visited_children: list[Any]) -> UTAUProject:
        self.pending_metadata["track"] = [
            track for track in visited_children[2] if track is not None
        ]
        return UTAUProject(**self.pending_metadata)

    def visit_ust_header(self, node: Node, visited_children: list[Any]) -> None:
        self.pending_metadata["ust_version"] = visited_children[4]
        if isinstance(visited_children[-1], list):
            self.pending_metadata["charset"] = visited_children[-1][-1][-1]

    def visit_ust_setting_line(self, node: Node, visited_children: list[Any]) -> None:
        key = visited_children[0][0].text
        if key == "Tempo":
            if (tempo_value := self.tempo2bpm(visited_children[0][2])) < MAX_ACCEPTED_BPM:
                self.pending_metadata["tempo"] = tempo_value
        elif key == "UstVersion":
            self.pending_metadata["ust_version"] = visited_children[0][2]
        elif key == "Tracks":
            self.pending_metadata["track_count"] = visited_children[0][2]
        elif key in ("Project", "ProjectName"):
            self.pending_metadata["project_name"] = visited_children[0][2]
        elif key == "Mode2":
            self.pending_metadata["pitch_mode2"] = visited_children[0][2]
        elif key == "VoiceDir":
            self.pending_metadata["voice_dir"] = visited_children[0][2]
        elif key == "OutFile":
            self.pending_metadata["out_file"] = visited_children[0][2]
        elif key == "CacheDir":
            self.pending_metadata["cache_dir"] = visited_children[0][2]
        elif key == "Tool1":
            self.pending_metadata["tool1"] = visited_children[0][2]
        elif key == "Tool2":
            self.pending_metadata["tool2"] = visited_children[0][2]
        elif key == "Autoren":
            self.pending_metadata["autoren"] = visited_children[0][2]
        elif key == "MapFirst":
            self.pending_metadata["map_first"] = visited_children[0][2]
        elif key == "Flags":
            self.pending_metadata["flags"] = visited_children[0][2]
        elif key == "TimeSignatures":
            numerator, denominator, bar_index = visited_children[0][2][1::2]
            self.pending_metadata["time_signatures"] = [
                UTAUTimeSignature(
                    numerator=numerator,
                    denominator=denominator,
                    bar_index=bar_index,
                )
            ]
            for pair in visited_children[0][3]:
                numerator, denominator, bar_index = pair[1][1::2]
                self.pending_metadata["time_signatures"].append(
                    UTAUTimeSignature(
                        numerator=numerator,
                        denominator=denominator,
                        bar_index=bar_index,
                    )
                )

    def visit_ust_envelope(self, node: Node, visited_children: list[Any]) -> UTAUEnvelope:
        kwargs = {"p1": visited_children[0]}
        (
            kwargs["p2"],
            kwargs["p3"],
            kwargs["v1"],
            kwargs["v2"],
            kwargs["v3"],
            kwargs["v4"],
        ) = (pair[1] for pair in visited_children[1][:6])
        if isinstance(visited_children[2][0], list):
            if isinstance(visited_children[2][0][0], list):
                kwargs["other_points"] = [pair[1] for pair in visited_children[2][0]]
            elif visited_children[2][0][0].text == ",,":
                kwargs["p4"] = visited_children[2][0][1]
            elif visited_children[2][0][0].text == ",%,":
                kwargs["p4"] = visited_children[2][0][1]
                if isinstance(visited_children[2][0][2], list):
                    kwargs["p5"] = visited_children[2][0][2][0][1]
                    if isinstance(visited_children[2][0][2][0][2], list):
                        kwargs["v5"] = visited_children[2][0][2][0][2][0][1]
        return UTAUEnvelope(**kwargs)

    def visit_value(self, node: Node, visited_children: list[Any]) -> str:
        return node.text

    def visit_utau_pitch_bend_mode(self, node: Node, visited_children: list[Any]) -> str:
        return "" if node.text == "null" else node.text

    def visit_ust_pitch_bend_type(self, node: Node, visited_children: list[Any]) -> str:
        return node.text

    def visit_ust_note_attr(self, node: Node, visited_children: list[Any]) -> None:
        key = visited_children[0][0].text
        if key == "Length":
            self.pending_note_attrs["length"] = visited_children[0][2]
        elif key == "Lyric":
            self.pending_note_attrs["lyric"] = visited_children[0][2]
        elif key == "NoteNum":
            self.pending_note_attrs["note_num"] = visited_children[0][2]
        elif key == "Tempo":
            self.pending_note_attrs["tempo"] = self.tempo2bpm(visited_children[0][2])
        elif key == "PBType":
            self.pending_note_attrs["pitchbend_type"] = visited_children[0][2]
        elif key == "PBStart":
            self.pending_note_attrs["pitchbend_start"] = visited_children[0][2]
        elif key in ("Modulation", "Moduration"):
            self.pending_note_attrs["modulation"] = visited_children[0][2]
        elif key == "Envelope":
            self.pending_note_attrs["envelope"] = visited_children[0][2]
        elif key == "Flags":
            self.pending_note_attrs["flags"] = visited_children[0][2]
        elif key == "Intensity":
            self.pending_note_attrs["intensity"] = visited_children[0][2]
        elif key == "Velocity":
            self.pending_note_attrs["velocity"] = visited_children[0][2]
        elif key == "PreUtterance":
            self.pending_note_attrs["pre_utterance"] = visited_children[0][2]
        elif key == "StartPoint":
            self.pending_note_attrs["start_point"] = visited_children[0][2]
        elif key == "Delta":
            self.pending_note_attrs["delta"] = visited_children[0][2]
        elif key == "Duration":
            self.pending_note_attrs["duration"] = visited_children[0][2]
        elif key == "VoiceOverlap":
            self.pending_note_attrs["voice_overlap"] = visited_children[0][2]
        elif key == "Label":
            self.pending_note_attrs["label"] = visited_children[0][2]
        elif key in ("Piches", "Pitches", "PitchBend"):
            self.pending_note_attrs["pitch_bend_points"] = [visited_children[0][2]]
            if isinstance(visited_children[0][3], list):
                self.pending_note_attrs["pitch_bend_points"].extend(
                    [pair[1] for pair in visited_children[0][3]]
                )
        elif key in ("PBS", "PBM", "PBW", "PBY"):
            self.pending_note_attrs[key.lower()] = [visited_children[0][2]]
            if isinstance(visited_children[0][3], list):
                self.pending_note_attrs[key.lower()].extend(
                    [pair[1] for pair in visited_children[0][3]]
                )
        elif key == "VBR":
            vibrato_kwargs = {"length": visited_children[0][2]}
            for i, pair in enumerate(visited_children[0][3]):
                if isinstance(pair[1], float):
                    if i == 0:
                        vibrato_kwargs["period"] = pair[1]
                    elif i == 1:
                        vibrato_kwargs["depth"] = pair[1]
                    elif i == 2:
                        vibrato_kwargs["fade_in"] = pair[1]
                    elif i == 3:
                        vibrato_kwargs["fade_out"] = pair[1]
                    elif i == 4:
                        vibrato_kwargs["phase_shift"] = pair[1]
                    elif i == 5:
                        vibrato_kwargs["shift"] = pair[1]
            self.pending_note_attrs["vbr"] = UtauNoteVibrato(**vibrato_kwargs)
        elif key == "stptrim":
            self.pending_note_attrs["stp_trim"] = visited_children[0][2]
        elif key == "layer":
            self.pending_note_attrs["layer"] = visited_children[0][2]
        elif key == "@preuttr":
            self.pending_note_attrs["at_preutterance"] = visited_children[0][2]
        elif key == "@overlap":
            self.pending_note_attrs["at_overlap"] = visited_children[0][2]
        elif key == "@stpoint":
            self.pending_note_attrs["at_start_point"] = visited_children[0][2]
        elif key == "@filename":
            self.pending_note_attrs["sample_filename"] = visited_children[0][2]
        elif key == "@alias":
            self.pending_note_attrs["alias"] = visited_children[0][2]
        elif key == "@cache":
            self.pending_note_attrs["cache_location"] = visited_children[0][2]
        # else: # ignored

    def visit_ust_note_head(self, node: Node, visited_children: list[Any]) -> None:
        if len(self.pending_note_attrs):
            self.pending_notes.append(UTAUNote(**self.pending_note_attrs))
            self.pending_note_attrs = {}
        self.pending_note_attrs["note_type"] = visited_children[1].text

    def visit_ust_track(self, node: Node, visited_children: list[Any]) -> Optional[UTAUTrack]:
        if len(self.pending_note_attrs):
            self.pending_notes.append(UTAUNote(**self.pending_note_attrs))
            self.pending_note_attrs = {}
        if len(self.pending_notes):
            ust_track = UTAUTrack(notes=self.pending_notes)
            self.pending_notes = []
            return ust_track

    def visit_bool(self, node: Node, visited_children: list[Any]) -> bool:
        return ast.literal_eval(node.text)

    def visit_int(self, node: Node, visited_children: list[Any]) -> int:
        return int(node.text)

    def visit_float(self, node: Node, visited_children: list[Any]) -> float:
        return float(node.text)

    def visit_frac(self, node: Node, visited_children: list[Any]) -> float:
        return float(node.text)

    def visit_optional_float(self, node: Node, visited_children: list[Any]) -> OptionalFloat:
        return (
            visited_children[0]
            if len(visited_children) == 1 and isinstance(visited_children[0], float)
            else ""
        )

    def generic_visit(self, node: Node, visited_children: list[Any]) -> Any:
        return visited_children or node
