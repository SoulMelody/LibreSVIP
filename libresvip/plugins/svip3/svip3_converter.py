import pathlib

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .model import Svip3Project
from .options import InputOptions, OutputOptions
from .svip3_generator import Svip3Generator
from .svip3_parser import Svip3Parser


class Svip3Converter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        svip3_project = Svip3Project.deserialize(path.read_bytes())
        return Svip3Parser(options).parse_project(svip3_project)

    def dump(self, path: pathlib.Path, project: Project, options: OutputOptions) -> None:
        svip3_project = Svip3Generator(options).generate_project(project)
        path.write_bytes(Svip3Project.serialize(svip3_project))
