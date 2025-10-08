import pathlib

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project
from libresvip.utils.binary.midi import MIDIFile

from .midi_generator import MidiGenerator
from .midi_parser import MidiParser
from .options import InputOptions, OutputOptions


class MidiConverter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        midi_file = MIDIFile.parse(path.read_bytes())
        return MidiParser(
            options=options,
        ).parse_project(midi_file)

    def dump(self, path: pathlib.Path, project: Project, options: OutputOptions) -> None:
        midi_file = MidiGenerator(
            options=options,
        ).generate_project(project)
        path.write_bytes(MIDIFile.build(midi_file))
