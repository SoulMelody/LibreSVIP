import pathlib
from importlib.resources import files

import cbor2

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .model import TuneLabProject
from .options import InputOptions, OutputOptions
from .tunelab_generator import TuneLabGenerator
from .tunelab_parser import TuneLabParser


class TuneLabXConverter(plugin_base.SVSConverter):
    input_option_cls = InputOptions
    output_option_cls = OutputOptions
    info = plugin_base.FormatProviderPluginInfo.load_from_string(
        content=(files(__package__) / "tlpx.yapsy-plugin").read_text(encoding="utf-8"),
    )
    _alias_ = "tlpx"
    _version_ = "0.1.0"

    @classmethod
    def load(cls, path: pathlib.Path, options: plugin_base.OptionsDict) -> Project:
        options_obj = cls.input_option_cls(**options)
        tlp_project = TuneLabProject.model_validate(cbor2.loads(path.read_bytes()))
        return TuneLabParser(options_obj).parse_project(tlp_project)

    @classmethod
    def dump(cls, path: pathlib.Path, project: Project, options: plugin_base.OptionsDict) -> None:
        options_obj = cls.output_option_cls(**options)
        tlp_project = TuneLabGenerator(options_obj).generate_project(project)
        path.write_bytes(cbor2.dumps(tlp_project.model_dump(mode="json", by_alias=True)))
