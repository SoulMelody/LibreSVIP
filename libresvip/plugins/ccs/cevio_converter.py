import pathlib
from importlib.resources import files

from xsdata.formats.dataclass.parsers.config import ParserConfig
from xsdata.formats.dataclass.serializers.config import SerializerConfig
from xsdata_pydantic.bindings import XmlParser, XmlSerializer

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .cevio_generator import CeVIOGenerator
from .cevio_parser import CeVIOParser
from .model import CeVIOCreativeStudioProject
from .options import InputOptions, OutputOptions


class CeVIOConverter(plugin_base.SVSConverter):
    input_option_cls = InputOptions
    output_option_cls = OutputOptions
    info = plugin_base.FormatProviderPluginInfo.load_from_string(
        content=(files(__package__) / "ccs.yapsy-plugin").read_text(encoding="utf-8"),
    )
    _alias_ = "ccs"
    _version_ = "1.0.0"

    @classmethod
    def load(cls, path: pathlib.Path, options: plugin_base.OptionsDict) -> Project:
        options_obj = cls.input_option_cls.model_validate(options)
        ccs_project = XmlParser(config=ParserConfig(fail_on_unknown_properties=False)).from_bytes(
            path.read_bytes(), CeVIOCreativeStudioProject
        )
        return CeVIOParser(options_obj).parse_project(ccs_project)

    @classmethod
    def dump(
        cls,
        path: pathlib.Path,
        project: Project,
        options: plugin_base.OptionsDict,
    ) -> None:
        options_obj = cls.output_option_cls.model_validate(options)
        ccs_project = CeVIOGenerator(options_obj).generate_project(project)
        serializer = XmlSerializer(
            config=SerializerConfig(pretty_print=True),
        )
        xml_text = serializer.render(ccs_project)
        path.write_bytes(xml_text.encode("utf-8"))
