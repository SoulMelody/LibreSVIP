import pathlib

from libresvip.core.compat import json
from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .model import SVProject
from .options import InputOptions, OutputOptions
from .synthv_generator import SynthVGenerator
from .synthv_parser import SynthVParser


class SynthVStudioConverter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        sv_content = (
            path.read_bytes().removesuffix(b"\x00").removeprefix("\ufeff".encode()).decode("utf-8")
        )
        sv_proj = SVProject.model_validate_json(sv_content, context={"path": path})
        if options.instant and sv_proj.instant_mode_enabled is not None:
            options.instant = sv_proj.instant_mode_enabled
        return SynthVParser(options=options).parse_project(sv_proj)

    def dump(self, path: pathlib.Path, project: Project, options: OutputOptions) -> None:
        sv_project = SynthVGenerator(
            options=options,
        ).generate_project(project)
        path.write_bytes(
            json.dumps(
                sv_project.model_dump(mode="json", by_alias=True, exclude_none=True),
                separators=(",", ":"),
            ).encode("utf-8")
            + b"\x00"
        )
