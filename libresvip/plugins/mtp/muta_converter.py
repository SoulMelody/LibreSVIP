import pathlib

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .model import muta_project_struct
from .muta_parser import MutaParser
from .options import InputOptions, OutputOptions


class MutaConverter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        muta_project = muta_project_struct.parse(path.read_bytes())
        return MutaParser(options).parse_project(muta_project)

    def dump(
        self, path: pathlib.Path, project: Project, options: OutputOptions
    ) -> None:
        raise NotImplementedError
