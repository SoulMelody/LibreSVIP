import io
import pathlib
import zipfile

from libresvip.core.compat import json
from libresvip.core.exceptions import InvalidFileTypeError
from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .legacy_model import PpsfLegacyProject
from .model import PpsfProject
from .options import InputOptions, OutputOptions
from .piapro_studio_generator import PiaproStudioGenerator
from .piapro_studio_legacy_parser import PiaproStudioLegacyParser
from .piapro_studio_nt_parser import PiaproStudioNTParser


class PiaproStudioConverter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        content = path.read_bytes()
        if content[:2] == b"PK":
            with zipfile.ZipFile(io.BytesIO(content), "r") as zf:
                proj_text = zf.read("ppsf.json")
            ppsf_project = PpsfProject.model_validate_json(proj_text)
            return PiaproStudioNTParser(options).parse_project(ppsf_project)
        elif content[:4] == b"PPSF":
            ppsf_project = PpsfLegacyProject.parse(content)
            return PiaproStudioLegacyParser(options).parse_project(ppsf_project)
        else:
            msg = "Unrecognizable format"
            raise InvalidFileTypeError(msg)

    def dump(self, path: pathlib.Path, project: Project, options: OutputOptions) -> None:
        ppsf_project = PiaproStudioGenerator(options).generate_project(project)
        proj_text = json.dumps(
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
