import pathlib
from importlib.resources import files
from typing import TYPE_CHECKING, Any

from xsdata.formats.dataclass.serializers.config import SerializerConfig
from xsdata_pydantic.bindings import XmlParser, XmlSerializer

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project
from libresvip.utils.xmlutils import DefaultXmlWriter

from .models.enums import VsqxVersion
from .models.vsqx3 import VSQ3_NS
from .models.vsqx4 import VSQ4_NS
from .options import InputOptions, OutputOptions
from .vsq3_generator import Vsq3Generator
from .vsq4_generator import Vsq4Generator
from .vsqx_parser import VsqxParser

if TYPE_CHECKING:
    from .model import Vsqx


class VocaloidXMLWriter(DefaultXmlWriter):
    def set_data(self, data: Any) -> None:
        if (
            isinstance(data, str)
            and self.pending_tag
            and len(self.pending_tag) > 1
            and self.pending_tag[1]
            in (
                "y",
                "p",
                "id",
                "id2",
                "auxID",
                "compID",
                "stylePluginID",
                "vstPluginID",
                "name",
                "partName",
                "seqName",
                "stylePluginName",
                "trackName",
                "vVoiceName",
                "vstPluginName",
                "filePath",
                "content",
                "phnmStr",
                "vender",
                "comment",
                "version",
            )
        ):
            super().set_cdata(data)
        else:
            super().set_data(data)

    def start_document(self) -> None:
        if self.config.xml_declaration:
            self.output.write(
                f'<?xml version="{self.config.xml_version}" encoding="{self.config.encoding}" standalone="no"?>\n'
            )


class VsqxConverter(plugin_base.SVSConverter):
    input_option_cls = InputOptions
    output_option_cls = OutputOptions
    info = plugin_base.FormatProviderPluginInfo.load_from_string(
        (files(__package__) / "vsqx.yapsy-plugin").read_text(encoding="utf-8"),
    )
    _alias_ = "vsqx"
    _version_ = "1.0.0"

    @classmethod
    def load(cls, path: pathlib.Path, options: plugin_base.OptionsDict) -> Project:
        options_obj = cls.input_option_cls.model_validate(options)
        xml_parser = XmlParser()
        vsqx_proj: Vsqx = xml_parser.from_bytes(path.read_bytes())
        return VsqxParser(options_obj, path).parse_project(vsqx_proj)

    @classmethod
    def dump(cls, path: pathlib.Path, project: Project, options: plugin_base.OptionsDict) -> None:
        options_obj = cls.output_option_cls.model_validate(options)
        vsqx_generator_class: type[Vsq3Generator | Vsq4Generator]
        if options_obj.vsqx_version == VsqxVersion.VSQ3:
            vsqx_generator_class = Vsq3Generator
            vsqx_namespace = VSQ3_NS
        else:
            vsqx_generator_class = Vsq4Generator
            vsqx_namespace = VSQ4_NS
        vsqx_proj = vsqx_generator_class(options_obj).generate_project(project)
        xml_serializer = XmlSerializer(
            config=SerializerConfig(
                pretty_print=options_obj.pretty_xml,
                pretty_print_indent="\t",
                schema_location=f"{vsqx_namespace} vsq{options_obj.vsqx_version.value}.xsd",
            ),
            writer=VocaloidXMLWriter,
        )
        path.write_bytes(
            xml_serializer.render(vsqx_proj, ns_map={None: vsqx_namespace}).encode("utf-8")
        )
