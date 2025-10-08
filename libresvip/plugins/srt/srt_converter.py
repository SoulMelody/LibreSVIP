import pathlib
from importlib.resources import files

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .options import OutputOptions
from .srt_generator import SrtGenerator


class SrtConverter(plugin_base.WriteOnlyConverterMixin, plugin_base.SVSConverter):
    output_option_cls = OutputOptions
    info = plugin_base.FormatProviderPluginInfo.load_from_string(
        content=(files(__package__) / "srt.yapsy-plugin").read_text(encoding="utf-8"),
    )
    _alias_ = "srt"
    _version_ = "1.0.0"

    @classmethod
    def dump(cls, path: pathlib.Path, project: Project, options: plugin_base.OptionsDict) -> None:
        options_obj = cls.output_option_cls(**options)
        ssa_obj = SrtGenerator(options_obj).generate_project(project)
        path.write_bytes(ssa_obj.to_string("srt").encode(options_obj.encoding))
