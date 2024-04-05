import io
import pathlib
import zipfile

from libresvip.core.compat import json
from libresvip.extension import base as plugin_base
from libresvip.model.base import Project
from libresvip.model.reset_time_axis import reset_time_axis

from .model import VogenProject
from .options import InputOptions, OutputOptions
from .vogen_generator import VogenGenerator
from .vogen_parser import VogenParser


class VogenConverter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        with zipfile.ZipFile(io.BytesIO(path.read_bytes()), "r") as zf:
            proj_text = zf.read("chart.json")
        vogen_project = VogenProject.model_validate_json(proj_text)
        return VogenParser(options).parse_project(vogen_project)

    def dump(self, path: pathlib.Path, project: Project, options: OutputOptions) -> None:
        if len(project.song_tempo_list) != 1:
            project = reset_time_axis(project, options.tempo)
        vogen_project = VogenGenerator(options).generate_project(project)
        proj_text = json.dumps(vogen_project.model_dump(by_alias=True), separators=(",", ":"))
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as zf:
            zf.writestr("chart.json", proj_text)
        path.write_bytes(buffer.getvalue())
