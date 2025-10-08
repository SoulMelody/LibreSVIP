import pathlib
from importlib.resources import files

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .model import muta_project_struct
from .muta_generator import MutaGenerator
from .muta_parser import MutaParser
from .options import InputOptions, OutputOptions


class MutaConverter(plugin_base.SVSConverter):
    input_option_cls = InputOptions
    output_option_cls = OutputOptions
    info = plugin_base.FormatProviderPluginInfo.load_from_string(
        content=(files(__package__) / "mtp.yapsy-plugin").read_text(encoding="utf-8"),
    )
    _alias_ = "mtp"
    _version_ = "1.0.0"

    @classmethod
    def load(cls, path: pathlib.Path, options: plugin_base.OptionsDict) -> Project:
        options_obj = cls.input_option_cls(**options)
        muta_project = muta_project_struct.parse(path.read_bytes())
        return MutaParser(options_obj).parse_project(muta_project)

    @classmethod
    def dump(cls, path: pathlib.Path, project: Project, options: plugin_base.OptionsDict) -> None:
        options_obj = cls.output_option_cls(**options)
        muta_project = MutaGenerator(options_obj).generate_project(project)
        path.write_bytes(muta_project_struct.build(muta_project))
