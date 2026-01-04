import pathlib
from importlib.resources import files

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project
from libresvip.utils.translation import gettext_lazy as _

from .binsvip_generator import BinarySvipGenerator
from .binsvip_parser import BinarySvipParser
from .msnrbf.svip_reader import SvipReader
from .msnrbf.svip_writer import SvipWriter
from .options import BinarySvipVersion, InputOptions, OutputOptions


class SvipConverter(plugin_base.SVSConverter):
    input_option_cls = InputOptions
    output_option_cls = OutputOptions
    info = plugin_base.FormatProviderPluginInfo.load_from_string(
        content=(files(__package__) / "binsvip.yapsy-plugin").read_text(encoding="utf-8"),
    )
    _alias_ = "svip"
    _version_ = "1.0.0"

    @classmethod
    def load(cls, path: pathlib.Path, options: plugin_base.OptionsDict) -> Project:
        options_obj = cls.input_option_cls(**options)
        with SvipReader() as reader:
            version, xs_project = reader.read(path)
            return BinarySvipParser(options_obj).parse_project(version, xs_project)

    @classmethod
    def dump(cls, path: pathlib.Path, project: Project, options: plugin_base.OptionsDict) -> None:
        options_obj = cls.output_option_cls(**options)
        ver_enum = options_obj.version
        if ver_enum == BinarySvipVersion.SVIP7_0_0:
            project.version = "SVIP7.0.0"
        elif ver_enum == BinarySvipVersion.AUTO:
            if project.version == "SVIP0.0.0":
                project.version = "SVIP6.0.0"
        elif ver_enum == BinarySvipVersion.SVIP6_0_0:
            project.version = "SVIP6.0.0"
        elif ver_enum == BinarySvipVersion.COMPAT:
            project.version = "SVIP0.0.0"
        else:
            raise ValueError(_("Unexpected enum value"))
        with SvipWriter() as registry:
            version, xs_project = BinarySvipGenerator(options_obj).generate_project(project)
            registry.write(path, version, xs_project)
