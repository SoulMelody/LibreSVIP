import pathlib
from importlib.resources import files
from typing import TYPE_CHECKING

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .options import OutputOptions
from .svg_generator import SvgGenerator

if TYPE_CHECKING:
    from svg import SVG


class SvgConverter(plugin_base.WriteOnlyConverterMixin, plugin_base.SVSConverter):
    output_option_cls = OutputOptions
    info = plugin_base.FormatProviderPluginInfo.load_from_string(
        content=(files(__package__) / "svg.yapsy-plugin").read_text(encoding="utf-8"),
    )
    _alias_ = "svg"
    _version_ = "1.0.0"

    @classmethod
    def dump(cls, path: pathlib.Path, project: Project, options: plugin_base.OptionsDict) -> None:
        options_obj = cls.output_option_cls(**options)
        drawing: SVG = SvgGenerator(options_obj).generate_project(project)
        path.write_bytes(drawing.as_str().encode("utf-8"))
