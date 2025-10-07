import pathlib
from importlib.resources import files

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .model import VxFile
from .options import InputOptions, OutputOptions
from .vx_beta_generator import VxBetaGenerator
from .vx_beta_parser import VxBetaParser


class VxBetaConverter(plugin_base.SVSConverter):
    input_option_cls = InputOptions
    output_option_cls = OutputOptions
    info = plugin_base.FormatProviderPluginInfo.load_from_string(
        content=(files(__package__) / "vxf.yapsy-plugin").read_text(encoding="utf-8"),
    )
    _alias_ = "vxf"
    _version_ = "3.0.2"

    @classmethod
    def load(cls, path: pathlib.Path, options: plugin_base.OptionsDict) -> Project:
        options_obj = cls.input_option_cls(**options)
        vx_file = VxFile.parse(path.read_bytes())
        return VxBetaParser(options_obj).parse_project(vx_file)

    @classmethod
    def dump(cls, path: pathlib.Path, project: Project, options: plugin_base.OptionsDict) -> None:
        options_obj = cls.output_option_cls(**options)
        vx_file = VxBetaGenerator(options_obj).generate_project(project)
        path.write_bytes(VxFile.build(vx_file))
