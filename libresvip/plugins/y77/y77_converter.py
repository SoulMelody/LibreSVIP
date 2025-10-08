import pathlib
from importlib.resources import files

from libresvip.core.compat import json
from libresvip.extension import base as plugin_base
from libresvip.model.base import Project
from libresvip.model.reset_time_axis import reset_time_axis

from .model import Y77Project
from .options import InputOptions, OutputOptions
from .y77_generator import Y77Generator
from .y77_parser import Y77Parser


class Y77Converter(plugin_base.SVSConverter):
    input_option_cls = InputOptions
    output_option_cls = OutputOptions
    info = plugin_base.FormatProviderPluginInfo.load_from_string(
        content=(files(__package__) / "y77.yapsy-plugin").read_text(encoding="utf-8"),
    )
    _alias_ = "y77"
    _version_ = "1.0.0"

    @classmethod
    def load(cls, path: pathlib.Path, options: plugin_base.OptionsDict) -> Project:
        options_obj = cls.input_option_cls(**options)
        y77_project = Y77Project.model_validate_json(path.read_bytes())
        return Y77Parser(options_obj).parse_project(y77_project)

    @classmethod
    def dump(cls, path: pathlib.Path, project: Project, options: plugin_base.OptionsDict) -> None:
        options_obj = cls.output_option_cls(**options)
        if len(project.song_tempo_list) != 1:
            project = reset_time_axis(project, options_obj.tempo)
        y77_project = Y77Generator(options_obj).generate_project(project)
        path.write_bytes(
            json.dumps(y77_project.model_dump(mode="json", by_alias=True)).encode("utf-8")
        )
