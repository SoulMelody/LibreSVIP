__package__ = "libresvip.plugins.svp"

import pathlib

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .model import SVProject
from .options import InputOptions, OutputOptions
from .synthv_generator import SynthVGenerator
from .synthv_parser import SynthVParser


class SynthVStudioConverter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        if options is None:
            options = InputOptions()
        sv_content = path.read_text().strip("\x00")
        sv_proj = SVProject.parse_raw(sv_content)
        options.instant = options.instant and sv_proj.instant_mode_enabled
        return SynthVParser(options=options).parse_project(sv_proj)

    def dump(
        self, path: pathlib.Path, project: Project, options: OutputOptions
    ) -> None:
        if options is None:
            options = OutputOptions()
        sv_project = SynthVGenerator(
            options=options,
        ).generate_project(project)
        path.write_bytes(
            sv_project.json(
                by_alias=True, exclude_none=True, separators=(",", ":")
            ).encode()
            + b"\x00"
        )
