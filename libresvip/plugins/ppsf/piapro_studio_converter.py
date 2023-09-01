import io
import pathlib
import zipfile

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project, json_dumps, json_loads

from .model import PpsfProject
from .options import InputOptions, OutputOptions
from .piapro_studio_generator import PiaproStudioGenerator
from .piapro_studio_parser import PiaproStudioParser


class PiaproStudioConverter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        with zipfile.ZipFile(io.BytesIO(path.read_bytes()), "r") as zf:
            proj_text = zf.read("ppsf.json")
        ppsf_project = PpsfProject.model_validate(json_loads(proj_text))
        return PiaproStudioParser(options).parse_project(ppsf_project)

    def dump(
        self, path: pathlib.Path, project: Project, options: OutputOptions
    ) -> None:
        ppsf_project = PiaproStudioGenerator(options).generate_project(project)
        proj_text = json_dumps(
            ppsf_project.model_dump(
                by_alias=True,
                exclude_none=True,
                mode="json",
            ),
            ensure_ascii=False,
            separators=(", ", ": "),
        )
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as zf:
            zf.writestr("ppsf.json", proj_text)
        path.write_bytes(buffer.getvalue())
