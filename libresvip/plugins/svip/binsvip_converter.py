__package__ = "libresvip.plugins.svip"
import pathlib

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .binsvip_generator import BinarySvipGenerator
from .binsvip_parser import BinarySvipParser
from .msnrbf.svip_reader import SvipReader
from .msnrbf.svip_writer import SvipWriter
from .options import BinarySvipVersion, InputOptions, OutputOptions


class SvipConverter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        with SvipReader() as reader:
            version, xs_project = reader.read(path)
            return BinarySvipParser().parse_project(version, xs_project)

    def dump(
        self, path: pathlib.Path, project: Project, options: OutputOptions
    ) -> None:
        if options is None:
            options = OutputOptions()
        ver_enum = options.version
        if ver_enum == BinarySvipVersion.SVIP7_0_0:
            project.version = "SVIP7.0.0"
        elif ver_enum == BinarySvipVersion.AUTO:
            if project.version != "SVIP0.0.0":
                pass
            else:
                project.version = "SVIP6.0.0"
        elif ver_enum == BinarySvipVersion.SVIP6_0_0:
            project.version = "SVIP6.0.0"
        elif ver_enum == BinarySvipVersion.COMPAT:
            project.version = "SVIP0.0.0"
        else:
            raise Exception("Unexpected enum value")
        with SvipWriter() as registry:
            version, xs_project = BinarySvipGenerator(options=options).generate_project(
                project
            )
            registry.write(path, version, xs_project)
