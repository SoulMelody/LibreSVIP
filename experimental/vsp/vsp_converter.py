import pathlib
import struct
from importlib.resources import files

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .model import VocalinaStudioProjectFile
from .options import InputOptions, OutputOptions
from .vsp_generator import VspGenerator
from .vsp_parser import VspParser


class VspConverter(plugin_base.SVSConverter):
    input_option_cls = InputOptions
    output_option_cls = OutputOptions
    info = plugin_base.FormatProviderPluginInfo.load_from_string(
        content=(files(__package__) / "vsp.yapsy-plugin").read_text(encoding="utf-8"),
    )
    _alias_ = "vsp"
    _version_ = "1.0.0"

    @classmethod
    def load(cls, path: pathlib.Path, options: plugin_base.OptionsDict) -> Project:
        options_obj = cls.input_option_cls(**options)
        parser = VspParser(options_obj, path)
        vsp_project = VocalinaStudioProjectFile.parse(path.read_bytes())
        return parser.parse_project(vsp_project)

    @classmethod
    def dump(cls, path: pathlib.Path, project: Project, options: plugin_base.OptionsDict) -> None:
        options_obj = cls.output_option_cls(**options)
        vsp_project = VspGenerator(options_obj).generate_project(project)
        vsp_content = bytearray(VocalinaStudioProjectFile.build(vsp_project))
        struct.pack_into("<I", vsp_content, 8, len(vsp_content))
        path.write_bytes(vsp_content)
