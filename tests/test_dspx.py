from pathlib import Path
from typing import Literal

import pytest

from libresvip.model.base import Note, Project, SingingTrack, SongTempo, TimeSignature
from libresvip.plugins.dspx.dspx_converter import DspxConverter
from libresvip.plugins.dspx.dspx_generator import DspxGenerator
from libresvip.plugins.dspx.model_v1 import (
    AnchorNode,
    Param,
    ParamCurve,
    ParamCurveAnchor,
    ParamCurveFree,
)
from libresvip.plugins.dspx.options import OutputOptions, PitchImportMode
from libresvip.plugins.dspx.param_utils import ResolvedParam

SCALE = 8064000
CurveKind = Literal["free", "linear", "hermite"]


def make_curve(kind: CurveKind, values: list[int]) -> ParamCurve:
    if kind == "free":
        return ParamCurveFree(type="free", start=0, step=5, values=values)
    return ParamCurveAnchor(
        type="anchor",
        start=0,
        nodes=[AnchorNode(x=i * 5, y=value, interp=kind) for i, value in enumerate(values)],
    )


@pytest.mark.parametrize("kind", ["free", "linear", "hermite"])
@pytest.mark.parametrize(
    ("source", "transform", "expected"),
    [
        (2 * SCALE, SCALE // 4, 6400),
        (SCALE // 4, 2 * SCALE, 6400),
        (-SCALE // 2, -SCALE // 2, 0),
        (3780000, SCALE // 2, 6000),
        (0, SCALE // 2, 0),
    ],
)
def test_pitch_clamps_source_and_transform(
    kind: CurveKind, source: int, transform: int, expected: int
) -> None:
    parameter = Param(
        edited=[make_curve(kind, [source])],
        original=[make_curve(kind, [SCALE])],
        transform=[make_curve(kind, [transform])],
    )
    pitch = ResolvedParam(parameter, PitchImportMode.EDITED_AND_ORIGINAL)
    assert pitch.evaluate(0) == expected


@pytest.mark.parametrize("kind", ["free", "linear", "hermite"])
@pytest.mark.parametrize("field", ["edited", "original", "transform"])
def test_pitch_clamps_samples_before_interpolation(kind: CurveKind, field: str) -> None:
    parameter = Param(edited=[], original=[], transform=[])
    getattr(parameter, field).append(make_curve(kind, [2 * SCALE, 0]))
    if field == "transform":
        parameter.edited.append(make_curve(kind, [SCALE // 4, SCALE // 4]))
    pitch = ResolvedParam(parameter, PitchImportMode.EDITED_AND_ORIGINAL)
    assert pitch.evaluate(2) == pytest.approx(3840 if field == "transform" else 7680)


def test_missing_pitch_is_not_replaced_by_transform() -> None:
    parameter = Param(edited=[], original=[], transform=[make_curve("free", [SCALE])])
    assert ResolvedParam(parameter, PitchImportMode.EDITED_AND_ORIGINAL).evaluate(0) is None


def test_clamped_pitch_file_round_trip(tmp_path: Path) -> None:
    project = Project(
        song_tempo_list=[SongTempo()],
        time_signature_list=[TimeSignature()],
        track_list=[
            SingingTrack(note_list=[Note(start_pos=0, length=480, key_number=60, lyric="a")])
        ],
    )
    model = DspxGenerator(OutputOptions()).generate_project(project)
    clip = model.content.tracks[0].clips[0]
    assert clip.type == "singing"
    clip.params["pitch"] = Param(
        edited=[make_curve("free", [2 * SCALE] * 3)],
        original=[],
        transform=[make_curve("free", [SCALE // 4] * 3)],
    )
    source_path = tmp_path / "source.dspx"
    source_path.write_text(model.model_dump_json(by_alias=True), encoding="utf-8")
    imported = DspxConverter.load(source_path, {})
    track = imported.track_list[0]
    assert isinstance(track, SingingTrack)
    expected = [(1920, 6400), (1925, 6400), (1930, 6400)]
    assert [(p.x, p.y) for p in track.edited_params.pitch.points.root if p.y >= 0] == expected

    output_path = tmp_path / "roundtrip.dspx"
    DspxConverter.dump(output_path, imported, {})
    restored = DspxConverter.load(output_path, {})
    restored_track = restored.track_list[0]
    assert isinstance(restored_track, SingingTrack)
    assert [
        (p.x, p.y) for p in restored_track.edited_params.pitch.points.root if p.y >= 0
    ] == expected
