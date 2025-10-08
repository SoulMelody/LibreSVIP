import pathlib

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project
from libresvip.utils.binary.midi import MIDIFile

from .options import InputOptions, OutputOptions
from .vsq_generator import VsqGenerator
from .vsq_parser import VsqParser


class VocaloidSequenceConverter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        vsq_file = MIDIFile.parse(path.read_bytes())
        return VsqParser(
            options=options,
        ).parse_project(vsq_file)

    def dump(self, path: pathlib.Path, project: Project, options: OutputOptions) -> None:
        vsq_file = VsqGenerator(
            options=options,
        ).generate_project(project)
        path.write_bytes(MIDIFile.build(vsq_file))
