import sys

from loguru import _defaults, _logger
from PySide6.QtCore import QMessageLogContext, QtMsgType

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
    QtMsgType.QtInfoMsg: qt_logger.info,
    QtMsgType.QtWarningMsg: qt_logger.warning,
    QtMsgType.QtCriticalMsg: qt_logger.critical,
    QtMsgType.QtFatalMsg: qt_logger.error,
    QtMsgType.QtDebugMsg: qt_logger.debug,
}


def qt_log_handler(message_type: QtMsgType, ctx: QMessageLogContext, message: str) -> None:
    message_prefix = (
        f"{ctx.file}:{ctx.line}"
        if ctx.function is None
        else f"{ctx.file}:{ctx.function}:{ctx.line}"
    )
    with qt_logger.contextualize(prefix=message_prefix):
        message = message.removeprefix(f"{message_prefix}: ")
        log_method = log_methods.get(message_type, qt_logger.info)
        log_method(message)
