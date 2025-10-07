import pathlib
from importlib.resources import files

from libresvip.core.compat import json
from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .model import SVProject
from .options import InputOptions, OutputOptions, SVProjectVersionCompatibility
from .synthv_generator import SynthVGenerator
from .synthv_parser import SynthVParser


class SynthVStudioConverter(plugin_base.SVSConverter):
    input_option_cls = InputOptions
    output_option_cls = OutputOptions
    info = plugin_base.FormatProviderPluginInfo.load_from_string(
        (files(__package__) / "svp.yapsy-plugin").read_text(encoding="utf-8"),
    )
    _alias_ = "svp"
    _version_ = "1.11.2"

    @classmethod
    def load(cls, path: pathlib.Path, options: plugin_base.OptionsDict) -> Project:
        options_obj = cls.input_option_cls(**options)
        sv_content = (
            path.read_bytes().removesuffix(b"\x00").removeprefix("\ufeff".encode()).decode("utf-8")
        )
        sv_proj = SVProject.model_validate_json(sv_content, context={"path": path})
        if options_obj.instant and sv_proj.instant_mode_enabled is not None:
            options_obj.instant = sv_proj.instant_mode_enabled
        return SynthVParser(options_obj).parse_project(sv_proj)

    @classmethod
    def dump(cls, path: pathlib.Path, project: Project, options: plugin_base.OptionsDict) -> None:
        options_obj = cls.output_option_cls(**options)
        sv_project = SynthVGenerator(
            options=options_obj,
        ).generate_project(project)
        path.write_bytes(
            json.dumps(
                sv_project.model_dump(mode="json", by_alias=True, exclude_none=True),
                separators=(",", ":"),
            ).encode("utf-8")
            + (
                b""
                if options_obj.version_compatibility == SVProjectVersionCompatibility.ABOVE_2_0_0
                else b"\x00"
            )
        )
