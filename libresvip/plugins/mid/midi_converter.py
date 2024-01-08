import io
import pathlib

import mido_fix as mido

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .midi_generator import MidiGenerator
from .midi_parser import MidiParser
from .options import InputOptions, OutputOptions


class MidiConverter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        midi_file = mido.MidiFile(
            file=io.BytesIO(path.read_bytes()),
            charset=options.lyric_encoding,
            clip=True,
        )
        return MidiParser(
            options=options,
        ).parse_project(midi_file)

    def dump(self, path: pathlib.Path, project: Project, options: OutputOptions) -> None:
        midi_file = MidiGenerator(
            options=options,
        ).generate_project(project)
        buffer = io.BytesIO()
        midi_file.save(file=buffer)
        path.write_bytes(buffer.getvalue())
