__package__ = "libresvip.plugins.y77"
import pathlib

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .model import Y77Project
from .options import InputOptions, OutputOptions
from .y77_generator import Y77Generator
from .y77_parser import Y77Parser


class Y77Converter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        y77_project = Y77Project.parse_file(path)
        return Y77Parser(options).parse_project(y77_project)

    def dump(
        self, path: pathlib.Path, project: Project, options: OutputOptions
    ) -> None:
        y77_project = Y77Generator(options).generate_project(project)
        path.write_text(y77_project.json(by_alias=True), encoding="utf-8")
