import atexit
import io
from contextlib import ExitStack
from typing import Optional

from loguru import _logger
from typing_extensions import Self

warning_logger = _logger.Logger(
    core=_logger.Core(),
    exception=None,
    depth=0,
    record=False,
    lazy=False,
    colors=False,
    raw=False,
    capture=True,
    patchers=[],
    extra={},
)


def show_warning(message: str) -> None:
    warning_logger.warning(message)


class CatchWarnings:
    def __init__(self) -> None:
        self._handler_id = None
        self._exit_stack: Optional[ExitStack] = None
        self._output = io.StringIO()
        self.output = ""

    def __enter__(self) -> Self:
        self._handler_id = warning_logger.add(
            self._output,
            format="{extra[handler_id]}|{message}",
            level="WARNING",
        )
        with ExitStack() as exit_stack:
            exit_stack.enter_context(warning_logger.contextualize(handler_id=self._handler_id))
            self._exit_stack = exit_stack.pop_all()
        return self

    def __exit__(self, *args: object) -> None:
        msg_prefix = f"{self._handler_id}|"
        if self._handler_id is not None:
            self._exit_stack.close()
            warning_logger.remove(self._handler_id)
            self._handler_id = None
        self._output.seek(0)
        lines = self._output.readlines()
        self.output = "\n".join(
            line.removeprefix(msg_prefix).rstrip() for line in lines if line.startswith(msg_prefix)
        )


atexit.register(warning_logger.remove)
