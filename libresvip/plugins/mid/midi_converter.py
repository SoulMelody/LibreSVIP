__package__ = "libresvip.plugins.mid"

import mido

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .midi_generator import MidiGenerator
from .midi_parser import MidiParser
from .options import InputOptions, OutputOptions


class MidiConverter(plugin_base.SVSConverterBase):
    def load(self, path: str, options: InputOptions) -> Project:
        midi_file = mido.MidiFile(path)
        return MidiParser(
            options=options,
        ).decode_project(midi_file)

    def dump(self, path: str, project: Project, options: OutputOptions) -> None:
        midi_file = MidiGenerator(
            options=options,
        ).encode_project(project)
        midi_file.save(path)
