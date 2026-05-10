import pathlib
from importlib.resources import files

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .model import MikotoStudioSequenceFormat
from .msq_generator import MsqGenerator
from .msq_parser import MsqParser
from .options import InputOptions, OutputOptions


class MsqConverter(plugin_base.SVSConverter):
    input_option_cls = InputOptions
    output_option_cls = OutputOptions
    info = plugin_base.FormatProviderPluginInfo.load_from_string(
        content=(files(__package__) / "msq.yapsy-plugin").read_text(encoding="utf-8"),
    )
    _alias_ = "msq"
    _version_ = "1.0.0"

    @classmethod
    def load(cls, path: pathlib.Path, options: plugin_base.OptionsDict) -> Project:
        options_obj = cls.input_option_cls(**options)
        parser = MsqParser(options_obj)
        msq_project = MikotoStudioSequenceFormat.model_validate_json(
            path.read_text(encoding="utf-8")
        )
        return parser.parse_project(msq_project)

    @classmethod
    def dump(cls, path: pathlib.Path, project: Project, options: plugin_base.OptionsDict) -> None:
        options_obj = cls.output_option_cls(**options)
        generator = MsqGenerator(options_obj)
        msq_project = generator.generate_project(project)
        path.write_text(msq_project.model_dump_json(by_alias=True, indent=2), encoding="utf-8")
