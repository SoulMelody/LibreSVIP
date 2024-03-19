import pathlib

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .dv_generator import DeepVocalGenerator
from .dv_parser import DeepVocalParser
from .model import dv_project_struct
from .options import InputOptions, OutputOptions


class DeepVocalConverter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        parser = DeepVocalParser(options)
        dv_project = dv_project_struct.parse(path.read_bytes())
        return parser.parse_project(dv_project)

    def dump(self, path: pathlib.Path, project: Project, options: OutputOptions) -> None:
        dv_project = DeepVocalGenerator(options).generate_project(project)
        dv_content = dv_project_struct.build(dv_project)
        path.write_bytes(dv_content)
