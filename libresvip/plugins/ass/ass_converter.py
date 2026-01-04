import pathlib
from importlib.resources import files

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .ass_generator import AssGenerator
from .options import OutputOptions


class AssConverter(plugin_base.WriteOnlyConverterMixin, plugin_base.SVSConverter):
    output_option_cls = OutputOptions
    info = plugin_base.FormatProviderPluginInfo.load_from_string(
        content=(files(__package__) / "ass.yapsy-plugin").read_text(encoding="utf-8"),
    )
    _alias_ = "ass"
    _version_ = "0.0.1"

    @classmethod
    def dump(cls, path: pathlib.Path, project: Project, options: plugin_base.OptionsDict) -> None:
        options_obj = cls.output_option_cls.model_validate(options)
        ssa_obj = AssGenerator(options_obj).generate_project(project)
        path.write_bytes(ssa_obj.to_string("ass").encode(options_obj.encoding))
