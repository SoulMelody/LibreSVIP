import io
import pathlib

import mido_fix as mido

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .options import InputOptions, OutputOptions
from .vsq_generator import VsqGenerator
from .vsq_parser import VsqParser


class VocaloidSequenceConverter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        vsq_file = mido.MidiFile(
            file=io.BytesIO(path.read_bytes()),
            charset=options.lyric_encoding,
            clip=True,
        )
        return VsqParser(
            options=options,
        ).parse_project(vsq_file)

    def dump(self, path: pathlib.Path, project: Project, options: OutputOptions) -> None:
        vsq_file = VsqGenerator(
            options=options,
        ).generate_project(project)
        buffer = io.BytesIO()
        vsq_file.save(file=buffer)
        path.write_bytes(buffer.getvalue())
