__package__ = "libresvip.plugins.s5p"
import pathlib

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .model import S5pProject
from .options import InputOptions, OutputOptions
from .synthv_editor_generator import SynthVEditorGenerator
from .synthv_editor_parser import SynthVEditorParser


class SynthVEditorConverter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        s5p_project = S5pProject.parse_file(path)
        return SynthVEditorParser(options).parse_project(s5p_project)

    def dump(
        self, path: pathlib.Path, project: Project, options: OutputOptions
    ) -> None:
        s5p_project = SynthVEditorGenerator(options).generate_project(project)
        path.write_text(
            s5p_project.json(by_alias=True, separators=(",", ":"), exclude_none=True),
            encoding="utf-8",
        )
