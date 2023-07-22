import pathlib
from typing import Any, TextIO

from xsdata.formats.dataclass.parsers.xml import XmlParser
from xsdata.formats.dataclass.serializers.writers import XmlEventWriter
from xsdata.formats.dataclass.serializers.xml import SerializerConfig, XmlSerializer

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project
from libresvip.utils import EchoGenerator

from .model import Vsqx
from .models.vsqx4 import VSQ4_NS
from .options import InputOptions, OutputOptions
from .vsqx_generator import VsqxGenerator
from .vsqx_parser import VsqxParser


class VocaloidXMLWriter(XmlEventWriter):
    def __init__(self, config: SerializerConfig, output: TextIO, ns_map: dict):
        super().__init__(config, output, ns_map)
        self.handler = EchoGenerator(
            out=self.output, encoding=self.config.encoding, short_empty_elements=True
        )

    def set_data(self, data: Any):
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
                "vstPluginName" "filePath",
                "content",
                "phnmStr",
                "vender",
                "comment",
                "version",
            )
        ):
            self.flush_start(False)
            self.handler._finish_pending_start_element()
            self.handler.start_cdata()
            super().set_data(data)
            self.handler.end_cdata()
        else:
            super().set_data(data)

    def start_document(self):
        if self.config.xml_declaration:
            self.output.write(f'<?xml version="{self.config.xml_version}"')
            self.output.write(f' encoding="{self.config.encoding}" standalone="no"?>\n')


class VsqxConverter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        xml_parser = XmlParser()
        vsqx_proj: Vsqx = xml_parser.from_bytes(path.read_bytes())
        return VsqxParser(options).parse_project(vsqx_proj)

    def dump(
        self, path: pathlib.Path, project: Project, options: OutputOptions
    ) -> None:
        vsqx_proj = VsqxGenerator(options).generate_project(project)
        xml_serializer = XmlSerializer(
            config=SerializerConfig(
                pretty_print=options.pretty_xml,
                pretty_print_indent="\t",
                schema_location=f"{VSQ4_NS} vsq4.xsd",
            ),
            writer=VocaloidXMLWriter,
        )
        path.write_text(
            xml_serializer.render(vsqx_proj, ns_map={None: VSQ4_NS}), encoding="utf-8"
        )
