__package__ = "libresvip.plugins.ufdata"
import pathlib

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .model import UFData
from .options import InputOptions, OutputOptions
from .ufdata_generator import UFDataGenerator
from .ufdata_parser import UFDataParser


class UFDataConverter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        ufdata_project = UFData.parse_file(path)
        return UFDataParser(options).parse_project(ufdata_project)

    def dump(
        self, path: pathlib.Path, project: Project, options: OutputOptions
    ) -> None:
        ufdata_project = UFDataGenerator(options).generate_project(project)
        path.write_text(ufdata_project.json(by_alias=True))
