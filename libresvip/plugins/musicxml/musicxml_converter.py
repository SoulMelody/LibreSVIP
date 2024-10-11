import io
import pathlib
import zipfile

from xsdata.formats.dataclass.parsers.config import ParserConfig
from xsdata.formats.dataclass.serializers.config import SerializerConfig
from xsdata_pydantic.bindings import XmlParser, XmlSerializer

from libresvip.extension import base as plugin_base
from libresvip.model.base import Project
from libresvip.utils.xmlutils import DefaultXmlWriter

from .models.container import Container
from .models.mxml4 import ScorePartwise
from .musicxml_generator import MusicXMLGenerator
from .musicxml_parser import MusicXMLParser
from .options import InputOptions, OutputOptions


class MusicXMLWriter(DefaultXmlWriter):
    def start_document(self) -> None:
        super().start_document()
        if self.config.xml_declaration:
            self.output.write(
                '<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">\n'
            )


class MusicXMLConverter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        content = path.read_bytes()
        xml_parser = XmlParser(config=ParserConfig(fail_on_unknown_properties=False))
        if content[:2] == b"PK":  # TODO: support mxl file extension
            with zipfile.ZipFile(io.BytesIO(content), "r") as zf:
                container_content = zf.read("META-INF/container.xml")
                container = xml_parser.from_bytes(container_content, Container)
                first_file = zf.read(container.rootfiles.rootfile[0].full_path)
                score = xml_parser.from_bytes(first_file, ScorePartwise)
        else:
            score = xml_parser.from_bytes(content, ScorePartwise)
        return MusicXMLParser(options).parse_project(score)

    def dump(self, path: pathlib.Path, project: Project, options: OutputOptions) -> None:
        score = MusicXMLGenerator(options).generate_project(project)
        xml_serializer = XmlSerializer(
            config=SerializerConfig(pretty_print=True), writer=MusicXMLWriter
        )
        path.write_bytes(xml_serializer.render(score).encode("utf-8"))
