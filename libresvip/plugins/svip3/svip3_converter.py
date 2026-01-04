import pathlib
from importlib.resources import files

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .model import Svip3Project
from .options import InputOptions, OutputOptions
from .svip3_generator import Svip3Generator
from .svip3_parser import Svip3Parser


class Svip3Converter(plugin_base.SVSConverter):
    input_option_cls = InputOptions
    output_option_cls = OutputOptions
    info = plugin_base.FormatProviderPluginInfo.load_from_string(
        (files(__package__) / "svip3.yapsy-plugin").read_text(encoding="utf-8"),
    )
    _alias_ = "svip3"
    _version_ = "0.0.1"

    @classmethod
    def load(cls, path: pathlib.Path, options: plugin_base.OptionsDict) -> Project:
        options_obj = cls.input_option_cls(**options)
        svip3_project = Svip3Project().parse(path.read_bytes())
        return Svip3Parser(options_obj).parse_project(svip3_project)

    @classmethod
    def dump(cls, path: pathlib.Path, project: Project, options: plugin_base.OptionsDict) -> None:
        options_obj = cls.output_option_cls(**options)
        svip3_project = Svip3Generator(options_obj).generate_project(project)
        path.write_bytes(bytes(svip3_project))
