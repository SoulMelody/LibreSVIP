import pathlib
from importlib.resources import files

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project
from libresvip.utils.binary.midi import MIDIFile

from .options import InputOptions, OutputOptions
from .vsq_generator import VsqGenerator
from .vsq_parser import VsqParser


class VocaloidSequenceConverter(plugin_base.SVSConverter):
    input_option_cls = InputOptions
    output_option_cls = OutputOptions
    info = plugin_base.FormatProviderPluginInfo.load_from_string(
        (files(__package__) / "vsq.yapsy-plugin").read_text(encoding="utf-8"),
    )
    _alias_ = "vsq"
    _version_ = "1.0.0"

    @classmethod
    def load(cls, path: pathlib.Path, options: plugin_base.OptionsDict) -> Project:
        options_obj = cls.input_option_cls(**options)
        vsq_file = MIDIFile.parse(path.read_bytes())
        return VsqParser(
            options=options_obj,
        ).parse_project(vsq_file)

    @classmethod
    def dump(cls, path: pathlib.Path, project: Project, options: plugin_base.OptionsDict) -> None:
        options_obj = cls.output_option_cls(**options)
        vsq_file = VsqGenerator(
            options=options_obj,
        ).generate_project(project)
        path.write_bytes(MIDIFile.build(vsq_file))
