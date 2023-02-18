__package__ = "libresvip.plugins.ds"

import pathlib

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .diffsinger_parser import DiffSingerParser
from .model import DsProject
from .options import InputOptions, OutputOptions


class DiffSingerConverter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        ds_project = DsProject.parse_file(path)
        return DiffSingerParser(options).parse_project(ds_project)

    def dump(
        self, path: pathlib.Path, project: Project, options: OutputOptions
    ) -> None:
        pass
