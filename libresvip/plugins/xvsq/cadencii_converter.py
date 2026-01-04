import pathlib
from importlib.resources import files
from typing import TYPE_CHECKING

from xsdata.formats.dataclass.serializers.config import SerializerConfig
from xsdata_pydantic.bindings import XmlParser, XmlSerializer

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .cadencii_generator import CadenciiGenerator
from .cadencii_parser import CadenciiParser
from .options import InputOptions, OutputOptions

if TYPE_CHECKING:
    from .model import VsqFileEx


class CadenciiConverter(plugin_base.SVSConverter):
    input_option_cls = InputOptions
    output_option_cls = OutputOptions
    info = plugin_base.FormatProviderPluginInfo.load_from_string(
        content=(files(__package__) / "xvsq.yapsy-plugin").read_text(encoding="utf-8"),
    )
    _alias_ = "xvsq"
    _version_ = "1.0.0"

    @classmethod
    def load(cls, path: pathlib.Path, options: plugin_base.OptionsDict) -> Project:
        options_obj = cls.input_option_cls.model_validate(options)
        xml_parser = XmlParser()
        xvsq_proj: VsqFileEx = xml_parser.from_bytes(path.read_bytes())
        return CadenciiParser(options=options_obj).parse_project(xvsq_proj)

    @classmethod
    def dump(cls, path: pathlib.Path, project: Project, options: plugin_base.OptionsDict) -> None:
        options_obj = cls.output_option_cls.model_validate(options)
        xml_serializer = XmlSerializer(
            config=SerializerConfig(
                pretty_print=options_obj.pretty_xml,
                pretty_print_indent="\t",
            ),
        )
        xvsq_project = CadenciiGenerator(options=options_obj).generate_project(project)
        path.write_bytes(xml_serializer.render(xvsq_project).encode("utf-8"))
