from qtpy.QtCore import QCoreApplication, QEvent, Qt
from qtpy.QtGui import QMouseEvent
from qtpy.QtQuick import QQuickWindow


class FramelessWindow(QQuickWindow):
    def __init__(self, parent=None, border_width: int = 5):
        super().__init__(parent)
        self.setFlags(
            self.flags() | Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window
        )
        self.border_width = border_width
        QCoreApplication.instance().installEventFilter(self)

    def eventFilter(self, obj, event: QEvent):
        et = event.type()
        if et != QMouseEvent.Type.MouseButtonPress and et != QMouseEvent.Type.MouseMove:
            return False

        edges = Qt.Edge(0)
        pos = event.globalPos() - self.position()
        if pos.x() < self.border_width:
            edges |= Qt.Edge.LeftEdge
        if pos.x() >= self.width() - self.border_width:
            edges |= Qt.Edge.RightEdge
        if pos.y() < self.border_width:
            edges |= Qt.Edge.TopEdge
        if pos.y() >= self.height() - self.border_width:
            edges |= Qt.Edge.BottomEdge

        if (
            et == QMouseEvent.Type.MouseMove
            and self.windowState() == Qt.WindowState.WindowNoState
        ):
            if edges in (
                Qt.Edge.LeftEdge | Qt.Edge.TopEdge,
                Qt.Edge.RightEdge | Qt.Edge.BottomEdge,
            ):
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
            elif edges in (
                Qt.Edge.RightEdge | Qt.Edge.TopEdge,
                Qt.Edge.LeftEdge | Qt.Edge.BottomEdge,
            ):
                self.setCursor(Qt.CursorShape.SizeBDiagCursor)
            elif edges in (Qt.Edge.TopEdge, Qt.Edge.BottomEdge):
                self.setCursor(Qt.CursorShape.SizeVerCursor)
            elif edges in (Qt.Edge.LeftEdge, Qt.Edge.RightEdge):
                self.setCursor(Qt.CursorShape.SizeHorCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)

        elif obj == self and et == QMouseEvent.Type.MouseButtonPress and edges:
            self.startSystemResize(edges)

        return False
