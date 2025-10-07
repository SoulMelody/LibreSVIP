import pathlib
from importlib.resources import files

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .dv_generator import DeepVocalGenerator
from .dv_parser import DeepVocalParser
from .model import dv_project_struct
from .options import InputOptions, OutputOptions


class DeepVocalConverter(plugin_base.SVSConverter):
    input_option_cls = InputOptions
    output_option_cls = OutputOptions
    info = plugin_base.FormatProviderPluginInfo.load_from_string(
        content=(files(__package__) / "dv.yapsy-plugin").read_text(encoding="utf-8"),
    )
    _alias_ = "dv"
    _version_ = "1.0.0"

    @classmethod
    def load(cls, path: pathlib.Path, options: plugin_base.OptionsDict) -> Project:
        options_obj = cls.input_option_cls(**options)
        parser = DeepVocalParser(options_obj)
        dv_project = dv_project_struct.parse(path.read_bytes())
        return parser.parse_project(dv_project)

    @classmethod
    def dump(cls, path: pathlib.Path, project: Project, options: plugin_base.OptionsDict) -> None:
        options_obj = cls.output_option_cls(**options)
        dv_project = DeepVocalGenerator(options_obj).generate_project(project)
        dv_content = dv_project_struct.build(dv_project)
        path.write_bytes(dv_content)
