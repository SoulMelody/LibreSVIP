import pathlib

from libresvip.core.compat import json
from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .model import S5pProject
from .options import InputOptions, OutputOptions
from .synthv_editor_generator import SynthVEditorGenerator
from .synthv_editor_parser import SynthVEditorParser


class SynthVEditorConverter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        s5p_project = S5pProject.model_validate_json(
            path.read_bytes().decode("utf-8"), context={"path": path}
        )
        return SynthVEditorParser(options).parse_project(s5p_project)

    def dump(self, path: pathlib.Path, project: Project, options: OutputOptions) -> None:
        s5p_project = SynthVEditorGenerator(options).generate_project(project)
        path.write_bytes(
            json.dumps(
                s5p_project.model_dump(mode="json", by_alias=True, exclude_none=True),
                separators=(",", ":"),
            ).encode("utf-8"),
        )
