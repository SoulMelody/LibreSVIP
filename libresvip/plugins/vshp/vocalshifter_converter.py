import pathlib
from importlib.resources import files

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .model import VocalShifterProjectData
from .options import InputOptions
from .vocalshifter_parser import VocalShifterParser


class VocalShifterConverter(plugin_base.ReadOnlyConverterMixin, plugin_base.SVSConverter):
    input_option_cls = InputOptions
    info = plugin_base.FormatProviderPluginInfo.load_from_string(
        content=(files(__package__) / "vshp.yapsy-plugin").read_text(encoding="utf-8"),
    )
    _alias_ = "vshp"
    _version_ = "1.0.0"

    @classmethod
    def load(cls, path: pathlib.Path, options: plugin_base.OptionsDict) -> Project:
        options_obj = cls.input_option_cls(**options)
        vshp_proj = VocalShifterProjectData.parse_file(path)
        return VocalShifterParser(options_obj).parse_project(vshp_proj)
