__package__ = "libresvip.plugins.gj"
import pathlib

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .gjgj_generator import GjgjGenerator
from .gjgj_parser import GjgjParser
from .model import GjgjProject
from .options import InputOptions, OutputOptions


class GjgjConverter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        gjgj_project = GjgjProject.parse_file(path, encoding="utf-8-sig")
        return GjgjParser(options).parse_project(gjgj_project)

    def dump(
        self, path: pathlib.Path, project: Project, options: OutputOptions
    ) -> None:
        gjgj_project = GjgjGenerator(options).generate_project(project)
        path.write_text(
            gjgj_project.json(
                by_alias=True,
                ensure_ascii=False,
                separators=(",", ":"),
                exclude_none=True,
            ),
            encoding="utf-8-sig",
        )
