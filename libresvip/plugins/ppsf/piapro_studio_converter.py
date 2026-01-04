import io
import pathlib
from importlib.resources import files

from upath import UPath

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


class PiaproStudioConverter(plugin_base.SVSConverter):
    input_option_cls = InputOptions
    output_option_cls = OutputOptions
    info = plugin_base.FormatProviderPluginInfo.load_from_string(
        content=(files(__package__) / "ppsf.yapsy-plugin").read_text(encoding="utf-8"),
    )
    _alias_ = "ppsf"
    _version_ = "1.0.0"

    @classmethod
    def load(cls, path: pathlib.Path, options: plugin_base.OptionsDict) -> Project:
        options_obj = cls.input_option_cls(**options)
        content = path.read_bytes()
        if content[:2] == b"PK":
            zip_path = UPath("zip://", fo=io.BytesIO(content), mode="r")
            proj_text = (zip_path / "ppsf.json").read_bytes()
            ppsf_project = PpsfProject.model_validate_json(proj_text)
            return PiaproStudioNTParser(options_obj).parse_project(ppsf_project)
        elif content[:4] == b"PPSF":
            ppsf_project = PpsfLegacyProject.parse(content)
            return PiaproStudioLegacyParser(options_obj).parse_project(ppsf_project)
        else:
            msg = "Unrecognizable format"
            raise InvalidFileTypeError(msg)

    @classmethod
    def dump(cls, path: pathlib.Path, project: Project, options: plugin_base.OptionsDict) -> None:
        options_obj = cls.output_option_cls(**options)
        ppsf_project = PiaproStudioGenerator(options_obj).generate_project(project)
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
        zip_path = UPath("zip://", fo=buffer, mode="w")
        (zip_path / "ppsf.json").write_text(proj_text, encoding="utf-8")
        path.write_bytes(buffer.getvalue())
