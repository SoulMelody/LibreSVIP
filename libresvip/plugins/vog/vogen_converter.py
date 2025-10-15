import io
import pathlib
from importlib.resources import files

from upath import UPath

from libresvip.core.compat import json
from libresvip.extension import base as plugin_base
from libresvip.model.base import Project
from libresvip.model.reset_time_axis import reset_time_axis

from .model import VogenProject
from .options import InputOptions, OutputOptions
from .vogen_generator import VogenGenerator
from .vogen_parser import VogenParser


class VogenConverter(plugin_base.SVSConverter):
    input_option_cls = InputOptions
    output_option_cls = OutputOptions
    info = plugin_base.FormatProviderPluginInfo.load_from_string(
        content=(files(__package__) / "vog.yapsy-plugin").read_text(encoding="utf-8"),
    )
    _alias_ = "vog"
    _version_ = "1.0.0"

    @classmethod
    def load(cls, path: pathlib.Path, options: plugin_base.OptionsDict) -> Project:
        options_obj = cls.input_option_cls(**options)
        zip_path = UPath("zip://", fo=io.BytesIO(path.read_bytes()), mode="r")
        proj_text = (zip_path / "chart.json").read_bytes()
        vogen_project = VogenProject.model_validate_json(proj_text)
        return VogenParser(options_obj).parse_project(vogen_project)

    @classmethod
    def dump(cls, path: pathlib.Path, project: Project, options: plugin_base.OptionsDict) -> None:
        options_obj = cls.output_option_cls(**options)
        if len(project.song_tempo_list) != 1:
            project = reset_time_axis(project, options_obj.tempo)
        vogen_project = VogenGenerator(options_obj).generate_project(project)
        proj_text = json.dumps(vogen_project.model_dump(by_alias=True), separators=(",", ":"))
        buffer = io.BytesIO()
        zip_path = UPath("zip://", fo=buffer, mode="w")
        (zip_path / "chart.json").write_text(proj_text, encoding="utf-8")
        path.write_bytes(buffer.getvalue())
