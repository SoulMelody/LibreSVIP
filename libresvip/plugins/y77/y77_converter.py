import pathlib

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project, json_dumps, json_loads

from .model import Y77Project
from .options import InputOptions, OutputOptions
from .y77_generator import Y77Generator
from .y77_parser import Y77Parser


class Y77Converter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        y77_project = Y77Project.model_validate(json_loads(path.read_text("utf-8")))
        return Y77Parser(options).parse_project(y77_project)

    def dump(
        self, path: pathlib.Path, project: Project, options: OutputOptions
    ) -> None:
        y77_project = Y77Generator(options).generate_project(project)
        path.write_text(
            json_dumps(y77_project.model_dump(mode="json", by_alias=True)),
            encoding="utf-8",
        )
