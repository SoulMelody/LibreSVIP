import sys

from loguru import _defaults, _logger
from PySide6.QtCore import (
    QMessageLogContext,
    QtMsgType,
    qFormatLogMessage,
    qInstallMessageHandler,
    qSetMessagePattern,
)

qt_logger = _logger.Logger(
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
if _defaults.LOGURU_AUTOINIT and sys.stderr:
    qt_logger.add(
        sys.stderr,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{extra[prefix]}</cyan> - <level>{message}</level>"
        ),
    )
log_methods = {
    "info": qt_logger.info,
    "warning": qt_logger.warning,
    "critical": qt_logger.critical,
    "fatal": qt_logger.error,
    "debug": qt_logger.debug,
}


def qt_log_handler(message_type: QtMsgType, ctx: QMessageLogContext, message: str) -> None:
    msg_type, file_name, function, line, msg = qFormatLogMessage(message_type, ctx, message).split(
        "\n", maxsplit=5
    )
    message_prefix = (
        f"{file_name}:{line}" if function == "unknown" else f"{file_name}:{function}:{line}"
    )
    with qt_logger.contextualize(prefix=message_prefix):
        msg = msg.removeprefix(message_prefix).removeprefix(":9").removeprefix(": ")
        log_method = log_methods.get(msg_type, qt_logger.info)
        log_method(msg)


def enable_log_handler() -> None:
    qSetMessagePattern("%{type}\n%{file}\n%{function}\n%{line}\n%{message}")
    qInstallMessageHandler(qt_log_handler)
