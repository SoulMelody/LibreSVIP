import pathlib

from libresvip.core.compat import json
from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .gjgj_generator import GjgjGenerator
from .gjgj_parser import GjgjParser
from .model import GjgjProject
from .options import InputOptions, OutputOptions


class GjgjConverter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        gjgj_project = GjgjProject.model_validate_json(path.read_bytes().decode("utf-8-sig"))
        return GjgjParser(options).parse_project(gjgj_project)

    def dump(self, path: pathlib.Path, project: Project, options: OutputOptions) -> None:
        gjgj_project = GjgjGenerator(options).generate_project(project)
        path.write_bytes(
            json.dumps(
                gjgj_project.model_dump(
                    mode="json",
                    exclude_none=True,
                    by_alias=True,
                ),
                ensure_ascii=False,
                separators=(",", ":"),
            ).encode("utf-8-sig")
        )
