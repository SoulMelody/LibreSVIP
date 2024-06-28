import pathlib
from typing import TYPE_CHECKING, Any, Union

from xsdata.formats.dataclass.serializers.config import SerializerConfig
from xsdata_pydantic.bindings import XmlParser, XmlSerializer

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project
from libresvip.utils.xmlutils import DefaultXmlWriter

from .enums import VsqxVersion
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


class VsqxConverter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        xml_parser = XmlParser()
        vsqx_proj: Vsqx = xml_parser.from_bytes(path.read_bytes())
        return VsqxParser(options, path).parse_project(vsqx_proj)

    def dump(self, path: pathlib.Path, project: Project, options: OutputOptions) -> None:
        vsqx_generator_class: type[Union[Vsq3Generator, Vsq4Generator]]
        if options.vsqx_version == VsqxVersion.VSQ3:
            vsqx_generator_class = Vsq3Generator
            vsqx_namespace = VSQ3_NS
        else:
            vsqx_generator_class = Vsq4Generator
            vsqx_namespace = VSQ4_NS
        vsqx_proj = vsqx_generator_class(options).generate_project(project)
        xml_serializer = XmlSerializer(
            config=SerializerConfig(
                pretty_print=options.pretty_xml,
                pretty_print_indent="\t",
                schema_location=f"{vsqx_namespace} vsq{options.vsqx_version.value}.xsd",
            ),
            writer=VocaloidXMLWriter,
        )
        path.write_bytes(
            xml_serializer.render(vsqx_proj, ns_map={None: vsqx_namespace}).encode("utf-8")
        )
