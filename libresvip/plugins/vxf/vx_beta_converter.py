import pathlib

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .model import VxFile
from .options import InputOptions, OutputOptions
from .vx_beta_generator import VxBetaGenerator
from .vx_beta_parser import VxBetaParser


class VxBetaConverter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        vx_file = VxFile.parse(path.read_bytes())
        return VxBetaParser(options).parse_project(vx_file)

    def dump(self, path: pathlib.Path, project: Project, options: OutputOptions) -> None:
        vx_file = VxBetaGenerator(options).generate_project(project)
        path.write_bytes(VxFile.build(vx_file))
