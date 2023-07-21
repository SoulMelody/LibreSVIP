import pathlib

import regex as re
from xsdata.formats.dataclass.parsers.xml import XmlParser
from xsdata.formats.dataclass.serializers.xml import (
    SerializerConfig,
    XmlSerializer,
    default_writer,
)

# from xsdata_pydantic.bindings import XmlParser, XmlSerializer
from libresvip.extension import base as plugin_base
from libresvip.model.base import Project

from .model import VocalSharpProject
from .options import InputOptions, OutputOptions


class VocalSharpXMLWriter(default_writer()):
    def start_document(self):
        if self.config.xml_declaration:
            self.output.write(f'<?xml version="{self.config.xml_version}"')
            self.output.write(f' encoding="{self.config.encoding}" standalone="no"?>\n')


def strip_whitespace(matcher):
    first_tag = matcher.group(1)
    second_tag = matcher.group(2)
    if first_tag != second_tag:
        return f"</{first_tag}><{second_tag}>"
    else:
        return matcher.group()


def space_to_tab(matcher):
    spaces = matcher.group(1)
    return "\t" * (len(spaces) // 2) + "<"


class VocalSharpConverter(plugin_base.SVSConverterBase):
    def load(self, path: pathlib.Path, options: InputOptions) -> Project:
        raise NotImplementedError
        parser = XmlParser()
        parsed = parser.parse(path, VocalSharpProject)
        return parsed

    def dump(
        self, path: pathlib.Path, project: Project, options: OutputOptions
    ) -> None:
        raise NotImplementedError
        serializer = XmlSerializer(
            config=SerializerConfig(pretty_print=True),
            writer=VocalSharpXMLWriter,
        )
        xml_text = serializer.render(project)
        xml_text = re.sub(r"(<[a-zA-Z]>)\s+", r"\1", xml_text)
        xml_text = re.sub(r"\s+(</[a-zA-Z]>)", r"\1", xml_text)
        xml_text = re.sub(r"</([a-z])>\s+<([a-z])>", strip_whitespace, xml_text)
        xml_text = re.sub(
            r"<([Nn]ame|Singer|lyric|LSD|symbol|sample|path)>(.*?)<",
            r"<\1><![CDATA[\2]]><",
            xml_text,
        )
        xml_text = re.sub(
            r"<([Nn]ame|Singer|lyric|LSD|symbol|sample|path)/>",
            r"<\1><![CDATA[]]></\1>",
            xml_text,
        )
        xml_text = re.sub(r"^([ ]+)<", space_to_tab, xml_text, flags=re.MULTILINE)
        path.write_text(xml_text, encoding="utf-8")
