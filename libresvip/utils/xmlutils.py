import io
from typing import TYPE_CHECKING, Optional
from xml.sax import saxutils

if TYPE_CHECKING:
    from collections.abc import Callable


class EchoGenerator(saxutils.XMLGenerator):
    # from https://code.activestate.com/recipes/84516-using-the-sax2-lexicalhandler-interface/

    def __init__(
        self,
        out: Optional[io.IOBase] = None,
        encoding: str = "iso-8859-1",
        short_empty_elements: bool = False,
    ) -> None:
        super().__init__(out, encoding, short_empty_elements)
        self._in_entity = 0
        self._in_cdata = 0
        self._write: Callable[[str], None]

    def characters(self, content: str) -> None:
        if self._in_entity:
            return
        elif self._in_cdata:
            self._write(content)
        else:
            super().characters(content)

    # -- LexicalHandler interface

    def comment(self, content: str) -> None:
        self._write(f"<!--{content!r}-->")

    def start_dtd(self, name: str, public_id: str, system_id: str) -> None:
        self._write(f"<!DOCTYPE {name}")
        if public_id:
            self._write(
                f" PUBLIC {saxutils.quoteattr(public_id)} {saxutils.quoteattr(system_id)}",
            )
        elif system_id:
            self._write(f" SYSTEM {saxutils.quoteattr(system_id)}")

    def end_dtd(self) -> None:
        self._write(">\n")

    def start_entity(self, name: str) -> None:
        self._write(f"&{name};")
        self._in_entity = 1

    def end_entity(self, name: str) -> None:
        self._in_entity = 0

    def start_cdata(self) -> None:
        self._write("<![CDATA[")
        self._in_cdata = 1

    def end_cdata(self) -> None:
        self._write("]]>")
        self._in_cdata = 0
