import pathlib
from importlib.resources import files

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project
from libresvip.utils.binary.midi import MIDIFile

from .midi_generator import MidiGenerator
from .midi_parser import MidiParser
from .options import InputOptions, OutputOptions


class MidiConverter(plugin_base.SVSConverter):
    input_option_cls = InputOptions
    output_option_cls = OutputOptions
    info = plugin_base.FormatProviderPluginInfo.load_from_string(
        content=(files(__package__) / "mid.yapsy-plugin").read_text(encoding="utf-8"),
    )
    _alias_ = "mid"
    _version_ = "1.0.0"

    @classmethod
    def load(cls, path: pathlib.Path, options: plugin_base.OptionsDict) -> Project:
        options_obj = cls.input_option_cls(**options)
        midi_file = MIDIFile.parse(path.read_bytes())
        return MidiParser(
            options=options_obj,
        ).parse_project(midi_file)

    @classmethod
    def dump(cls, path: pathlib.Path, project: Project, options: plugin_base.OptionsDict) -> None:
        options_obj = cls.output_option_cls(**options)
        midi_file = MidiGenerator(
            options=options_obj,
        ).generate_project(project)
        path.write_bytes(MIDIFile.build(midi_file))
