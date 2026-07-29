import pathlib
from importlib.resources import files

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .dspx_generator import DspxGenerator
from .dspx_io import ZSTD_AVAILABLE, dump_model, load_model
from .dspx_parser import DspxParser
from .options import InputOptions, OutputOptions


class DspxConverter(plugin_base.SVSConverter):
    input_option_cls = InputOptions
    output_option_cls = OutputOptions
    info = plugin_base.FormatProviderPluginInfo.load_from_string(
        content=(files(__package__) / "dspx.yapsy-plugin").read_text(encoding="utf-8"),
    )
    _alias_ = "dspx"
    _version_ = "1.0.0"
    _skipload_ = not ZSTD_AVAILABLE

    @classmethod
    def load(cls, path: pathlib.Path, options: plugin_base.OptionsDict) -> Project:
        model = load_model(path.read_bytes())
        return DspxParser(cls.input_option_cls(**options), path).parse_project(model)

    @classmethod
    def dump(cls, path: pathlib.Path, project: Project, options: plugin_base.OptionsDict) -> None:
        model = DspxGenerator(cls.output_option_cls(**options)).generate_project(project)
        path.write_bytes(dump_model(model))
