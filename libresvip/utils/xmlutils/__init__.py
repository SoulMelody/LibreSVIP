from typing import Any

try:
    from lxml.etree import CDATA
    from xsdata.formats.dataclass.serializers.writers.lxml import (
        LxmlEventWriter,
    )

    class DefaultXmlWriter(LxmlEventWriter):
        def set_cdata(self, data: Any) -> None:
            self.flush_start(False)
            self.handler._element_stack[-1].text = CDATA(data=data)

except ImportError:
    from xml.sax.saxutils import XMLGenerator

    from xsdata.formats.dataclass.serializers.writers.native import (
        XmlEventWriter,
    )

    from .native import EchoGenerator

    class DefaultXmlWriter(XmlEventWriter):  # type: ignore[no-redef]
        def build_handler(self) -> XMLGenerator:
            return EchoGenerator(
                out=self.output,
                encoding=self.config.encoding,
                short_empty_elements=True,
            )

        def set_cdata(self, data: Any) -> None:
            self.flush_start(False)
            self.handler.start_cdata()
            super().set_data(data)
            self.handler.end_cdata()
