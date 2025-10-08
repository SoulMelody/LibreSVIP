import pathlib
from importlib.resources import files

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .lrc_generator import LrcGenerator
from .options import OutputOptions
from .template import render_lrc


class LrcConverter(plugin_base.WriteOnlyConverterMixin, plugin_base.SVSConverter):
    output_option_cls = OutputOptions
    info = plugin_base.FormatProviderPluginInfo.load_from_string(
        content=(files(__package__) / "lrc.yapsy-plugin").read_text(encoding="utf-8"),
    )
    _alias_ = "lrc"
    _version_ = "1.0.0"

    @classmethod
    def dump(cls, path: pathlib.Path, project: Project, options: plugin_base.OptionsDict) -> None:
        options_obj = cls.output_option_cls(**options)
        lrc_model = LrcGenerator(options_obj).generate_project(project)
        render_lrc(lrc_model, path)
