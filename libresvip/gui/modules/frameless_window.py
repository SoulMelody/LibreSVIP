from typing import Optional

from PySide6.QtCore import QCoreApplication, QEvent, QObject, Qt
from PySide6.QtGui import QMouseEvent, QWindow
from PySide6.QtQml import QmlElement
from PySide6.QtQuick import QQuickWindow

from __feature__ import snake_case, true_property  # isort:skip # noqa: F401

QML_IMPORT_NAME = "FramelessWindow"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QmlElement
class FramelessWindow(QQuickWindow):
    def __init__(self, parent: Optional[QWindow] = None, border_width: int = 5) -> None:
        super().__init__(parent)
        self.flags: Qt.WindowType = (
            self.flags | Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window
        )
        self.border_width = border_width
        QCoreApplication.instance().install_event_filter(self)

    def event_filter(self, obj: QObject, event: QEvent) -> bool:
        et = event.type()
        if et not in [
            QMouseEvent.Type.MouseButtonPress,
            QMouseEvent.Type.MouseMove,
        ]:
            return False

        edges = Qt.Edge(0)
        pos = event.global_pos() - self.position()
        if pos.x() < self.border_width:
            edges |= Qt.Edge.LeftEdge
        if pos.x() >= self.width - self.border_width:
            edges |= Qt.Edge.RightEdge
        if pos.y() < self.border_width:
            edges |= Qt.Edge.TopEdge
        if pos.y() >= self.height - self.border_width:
            edges |= Qt.Edge.BottomEdge

        if et == QMouseEvent.Type.MouseMove and self.window_state() == Qt.WindowState.WindowNoState:
            if edges in (
                Qt.Edge.LeftEdge | Qt.Edge.TopEdge,
                Qt.Edge.RightEdge | Qt.Edge.BottomEdge,
            ):
                self.set_cursor(Qt.CursorShape.SizeFDiagCursor)
            elif edges in (
                Qt.Edge.RightEdge | Qt.Edge.TopEdge,
                Qt.Edge.LeftEdge | Qt.Edge.BottomEdge,
            ):
                self.set_cursor(Qt.CursorShape.SizeBDiagCursor)
            elif edges in (Qt.Edge.TopEdge, Qt.Edge.BottomEdge):
                self.set_cursor(Qt.CursorShape.SizeVerCursor)
            elif edges in (Qt.Edge.LeftEdge, Qt.Edge.RightEdge):
                self.set_cursor(Qt.CursorShape.SizeHorCursor)
            else:
                self.set_cursor(Qt.CursorShape.ArrowCursor)

        elif obj == self and et == QMouseEvent.Type.MouseButtonPress and edges:
            self.start_system_resize(edges)

        return False
