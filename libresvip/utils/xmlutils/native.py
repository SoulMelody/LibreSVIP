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
        self._in_cdata = 0
        self._write: Callable[[str], None]
        self._finish_pending_start_element: Callable[[], None]

    def characters(self, content: str) -> None:
        if self._in_cdata:
            self._write(content)
        else:
            super().characters(content)

    def start_cdata(self) -> None:
        self._finish_pending_start_element()
        self._write("<![CDATA[")
        self._in_cdata = 1

    def end_cdata(self) -> None:
        self._write("]]>")
        self._in_cdata = 0
