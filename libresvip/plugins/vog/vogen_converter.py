__package__ = "libresvip.plugins.vog"
import pathlib
import zipfile

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .model import VogenProject
from .options import InputOptions, OutputOptions
from .vogen_generator import VogenGenerator
from .vogen_parser import VogenParser


class VogenConverter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        with zipfile.ZipFile(path, "r") as zf:
            proj_text = zf.read("chart.json")
        vogen_project = VogenProject.parse_raw(proj_text)
        return VogenParser(options).parse_project(vogen_project)

    def dump(
        self, path: pathlib.Path, project: Project, options: OutputOptions
    ) -> None:
        vogen_project = VogenGenerator(options).generate_project(project)
        proj_text = vogen_project.json(by_alias=True, separators=(",", ":"))
        with zipfile.ZipFile(path, "w") as zf:
            zf.writestr("chart.json", proj_text)
