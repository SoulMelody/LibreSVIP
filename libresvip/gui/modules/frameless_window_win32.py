import ctypes
from ctypes.wintypes import MSG
from typing import Optional

from PySide6.QtCore import QObject, QPoint, QRect, Qt
from PySide6.QtGui import QCursor, QGuiApplication, QMouseEvent
from PySide6.QtQml import QmlElement
from PySide6.QtQuick import QQuickItem, QQuickWindow

from __feature__ import snake_case, true_property  # isort:skip # noqa: F401

from . import win32_constants as win32con

QML_IMPORT_NAME = "FramelessWindow"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


class MARGINS(ctypes.Structure):
    _fields_ = [
        ("cxLeftWidth", ctypes.c_int),
        ("cxRightWidth", ctypes.c_int),
        ("cyTopHeight", ctypes.c_int),
        ("cyBottomHeight", ctypes.c_int),
    ]


@QmlElement
class FramelessWindow(QQuickWindow):
    def __init__(self, parent: QObject = None, border_width: int = 5):
        super().__init__(parent)
        self.flags = (
            self.flags
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Window
            | Qt.WindowType.WindowMinMaxButtonsHint
        )
        self.border_width = border_width
        self.maximize_btn = None
        self.maximize_btn_hovered = False
        self.set_borderless()
        screen_geometry = self.screen().available_geometry
        self.set_position(
            (screen_geometry.width() - 1200) // 2,
            (screen_geometry.height() - 800) // 2,
        )
        self.prev_visibility = None

    @property
    def hwnd(self) -> int:
        return self.win_id()

    @property
    def is_composition_enabled(self) -> bool:
        b_result = ctypes.c_int(0)
        ctypes.windll.dwmapi.DwmIsCompositionEnabled(ctypes.byref(b_result))
        return bool(b_result.value)

    def set_borderless(self) -> None:
        hwnd = self.hwnd
        user32 = ctypes.windll.user32

        style = user32.GetWindowLongW(hwnd, win32con.GWL_STYLE)

        user32.SetWindowLongW(
            hwnd,
            win32con.GWL_STYLE,
            style | win32con.CS_DBLCLKS | win32con.WS_THICKFRAME,
        )

        style = user32.GetWindowLongW(hwnd, win32con.GWL_EXSTYLE)
        style &= ~win32con.WS_EX_LAYERED
        user32.SetWindowLongW(hwnd, win32con.GWL_EXSTYLE, style)

    def add_shadow_effect(self) -> Optional[ctypes.HRESULT]:
        if not self.is_composition_enabled:
            return

        dwmapi = ctypes.windll.dwmapi

        margins = MARGINS(-1, -1, -1, -1)
        return dwmapi.DwmExtendFrameIntoClientArea(self.hwnd, ctypes.byref(margins))

    def native_event(self, event_type: bytes, message: int) -> tuple[bool, int]:
        if self.maximize_btn is None:
            self.maximize_btn: QQuickItem = self.find_child(
                QQuickItem, "maximizeButton"
            )
        if event_type == b"windows_generic_MSG":
            msg = MSG.from_address(message.__int__())

            if msg.message == win32con.WM_NCHITTEST and self.border_width is not None:
                if msg.hWnd == self.hwnd:
                    pos = QCursor.pos()
                    x_pos = pos.x() - self.x
                    y_pos = pos.y() - self.y
                    w, h = self.width, self.height
                    bw = (
                        0
                        if self.visibility == QQuickWindow.Visibility.Maximized
                        else self.border_width
                    )
                    lx = x_pos < bw
                    rx = x_pos > w - bw
                    ty = y_pos < bw
                    by = y_pos > h - bw
                    if not self.visibility == QQuickWindow.Visibility.Maximized:
                        if lx and ty:
                            return True, win32con.HTTOPLEFT
                        elif rx and by:
                            return True, win32con.HTBOTTOMRIGHT
                        elif rx and ty:
                            return True, win32con.HTTOPRIGHT
                        elif lx and by:
                            return True, win32con.HTBOTTOMLEFT
                        elif ty:
                            return True, win32con.HTTOP
                        elif by:
                            return True, win32con.HTBOTTOM
                        elif lx:
                            return True, win32con.HTLEFT
                        elif rx:
                            return True, win32con.HTRIGHT
                    if self.maximize_btn is not None:
                        top_left = self.maximize_btn.map_to_global(QPoint(0, 0))
                        rect = QRect(
                            top_left.x() - self.x,
                            top_left.y() - self.y,
                            self.maximize_btn.width,
                            self.maximize_btn.height,
                        )
                        if rect.contains(x_pos, y_pos):
                            QGuiApplication.send_event(
                                self.maximize_btn,
                                QMouseEvent(
                                    QMouseEvent.Type.HoverEnter,
                                    QPoint(),
                                    Qt.MouseButton.NoButton,
                                    Qt.MouseButton.NoButton,
                                    Qt.KeyboardModifier.NoModifier,
                                ),
                            )
                            self.maximize_btn_hovered = True
                            return True, win32con.HTMAXBUTTON
                        elif self.maximize_btn_hovered:
                            QGuiApplication.send_event(
                                self.maximize_btn,
                                QMouseEvent(
                                    QMouseEvent.Type.HoverLeave,
                                    QPoint(),
                                    Qt.MouseButton.NoButton,
                                    Qt.MouseButton.NoButton,
                                    Qt.KeyboardModifier.NoModifier,
                                ),
                            )
                            self.maximize_btn_hovered = False
            elif msg.message in [
                win32con.WM_NCLBUTTONDOWN,
                win32con.WM_NCLBUTTONDBLCLK,
            ]:
                pos = QCursor.pos()
                x_pos = pos.x() - self.x
                y_pos = pos.y() - self.y
                if self.maximize_btn is not None:
                    top_left = self.maximize_btn.map_to_global(QPoint(0, 0))
                    rect = QRect(
                        top_left.x() - self.x,
                        top_left.y() - self.y,
                        self.maximize_btn.width,
                        self.maximize_btn.height,
                    )
                    if rect.contains(x_pos, y_pos):
                        QGuiApplication.send_event(
                            self.maximize_btn,
                            QMouseEvent(
                                QMouseEvent.Type.MouseButtonPress,
                                QPoint(),
                                Qt.MouseButton.NoButton,
                                Qt.MouseButton.NoButton,
                                Qt.KeyboardModifier.NoModifier,
                            ),
                        )
                        return True, 0
            elif msg.message in [win32con.WM_NCLBUTTONUP, win32con.WM_NCRBUTTONUP]:
                pos = QCursor.pos()
                x_pos = pos.x() - self.x
                y_pos = pos.y() - self.y
                if self.maximize_btn is not None:
                    top_left = self.maximize_btn.map_to_global(QPoint(0, 0))
                    rect = QRect(
                        top_left.x() - self.x,
                        top_left.y() - self.y,
                        self.maximize_btn.width,
                        self.maximize_btn.height,
                    )
                    if rect.contains(x_pos, y_pos):
                        QGuiApplication.send_event(
                            self.maximize_btn,
                            QMouseEvent(
                                QMouseEvent.Type.MouseButtonRelease,
                                QPoint(),
                                Qt.MouseButton.NoButton,
                                Qt.MouseButton.NoButton,
                                Qt.KeyboardModifier.NoModifier,
                            ),
                        )
            elif msg.message == win32con.WM_NCCALCSIZE:
                return True, win32con.WVR_REDRAW if msg.wParam else 0
            elif msg.message == win32con.WM_ACTIVATE:
                if (hr := self.add_shadow_effect()) is not None:
                    return True, hr
            elif msg.message == win32con.WM_SYSCOMMAND:
                if msg.wParam == win32con.SC_RESTORE:
                    if self.visibility == QQuickWindow.Visibility.Minimized:
                        if self.prev_visibility == QQuickWindow.Visibility.Maximized:
                            self.show_maximized()
                        else:
                            self.show_normal()
                        return True, 0
            elif msg.message == win32con.WM_SIZE:
                if msg.wParam == win32con.SIZE_MINIMIZED:
                    self.prev_visibility = self.visibility
        return super().native_event(event_type, message)
