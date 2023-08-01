import io
import pathlib
import zipfile

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .model import PpsfProject
from .options import InputOptions, OutputOptions
from .piapro_studio_parser import PiaproStudioParser


class PiaproStudioConverter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        with zipfile.ZipFile(io.BytesIO(path.read_bytes()), "r") as zf:
            proj_text = zf.read("ppsf.json")
        ppsf_project = PpsfProject.model_validate_json(proj_text)
        return PiaproStudioParser(options).parse_project(ppsf_project)

    def dump(
        self, path: pathlib.Path, project: Project, options: OutputOptions
    ) -> None:
        raise NotImplementedError()
