# mypy: disable-error-code="attr-defined"
import ctypes
from ctypes.wintypes import MSG
from typing import Optional, SupportsInt

from PySide6.QtCore import QPoint, QRect, Qt
from PySide6.QtGui import QGuiApplication, QMouseEvent, QWindow
from PySide6.QtQml import QmlElement
from PySide6.QtQuick import QQuickItem, QQuickWindow

from __feature__ import snake_case, true_property  # isort:skip # noqa: F401

from . import win32_constants as win32con

QML_IMPORT_NAME = "FramelessWindow"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


class MARGINS(ctypes.Structure):
    _fields_ = (
        ("cxLeftWidth", ctypes.c_int),
        ("cxRightWidth", ctypes.c_int),
        ("cyTopHeight", ctypes.c_int),
        ("cyBottomHeight", ctypes.c_int),
    )


@QmlElement
class FramelessWindow(QQuickWindow):
    def __init__(self, parent: Optional[QWindow] = None, border_width: int = 5) -> None:
        super().__init__(parent)
        self.flags: Qt.WindowType = (
            self.flags
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Window
            | Qt.WindowType.WindowMinMaxButtonsHint
        )
        self.border_width = border_width
        self.maximize_btn: Optional[QQuickItem] = None
        self.maximize_btn_hovered = False
        self.set_borderless()
        screen_geometry = self.screen().available_geometry
        self.set_position(
            (screen_geometry.width() - 1200) // 2,
            (screen_geometry.height() - 800) // 2,
        )
        self.prev_visibility = None

    def get_point_from_lparam(self, l_param: int) -> tuple[int, int]:
        pixel_ratio = self.screen().device_pixel_ratio
        return (
            (ctypes.c_short(l_param & 0xFFFF).value) // pixel_ratio - self.x,
            (ctypes.c_short((l_param >> 16) & 0xFFFF).value) // pixel_ratio - self.y,
        )

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
            style
            | win32con.WS_MAXIMIZEBOX
            | win32con.WS_CAPTION
            | win32con.CS_DBLCLKS
            | win32con.WS_THICKFRAME,
        )

        style = user32.GetWindowLongW(hwnd, win32con.GWL_EXSTYLE)
        style &= ~win32con.WS_EX_LAYERED
        user32.SetWindowLongW(hwnd, win32con.GWL_EXSTYLE, style)

    def add_dwm_effect(self) -> Optional[SupportsInt]:
        if not self.is_composition_enabled:
            return None

        dwmapi = ctypes.windll.dwmapi

        margins = MARGINS(-1, -1, -1, -1)
        return dwmapi.DwmExtendFrameIntoClientArea(self.hwnd, ctypes.byref(margins))

    def native_event(self, event_type: bytes, message: SupportsInt) -> tuple[bool, SupportsInt]:
        if self.maximize_btn is None:
            self.maximize_btn = self.find_child(QQuickItem, "maximizeButton")
        if event_type == b"windows_generic_MSG":
            msg = MSG.from_address(int(message))

            if msg.message == win32con.WM_NCHITTEST and self.border_width is not None:
                if msg.hWnd == self.hwnd:
                    x_pos, y_pos = self.get_point_from_lparam(msg.lParam)
                    bw = (
                        0
                        if self.visibility == QQuickWindow.Visibility.Maximized
                        else self.border_width
                    )
                    lx = x_pos < bw
                    rx = x_pos > self.width - bw
                    ty = y_pos < bw
                    by = y_pos > self.height - bw
                    if lx and ty:
                        if self.visibility != QQuickWindow.Visibility.Maximized:
                            return True, win32con.HTTOPLEFT
                    elif rx and by:
                        if self.visibility != QQuickWindow.Visibility.Maximized:
                            return True, win32con.HTBOTTOMRIGHT
                    elif rx and ty:
                        if self.visibility != QQuickWindow.Visibility.Maximized:
                            return True, win32con.HTTOPRIGHT
                    elif lx and by:
                        if self.visibility != QQuickWindow.Visibility.Maximized:
                            return True, win32con.HTBOTTOMLEFT
                    elif ty:
                        if self.visibility != QQuickWindow.Visibility.Maximized:
                            return True, win32con.HTTOP
                    elif by:
                        if self.visibility != QQuickWindow.Visibility.Maximized:
                            return True, win32con.HTBOTTOM
                    elif lx:
                        if self.visibility != QQuickWindow.Visibility.Maximized:
                            return True, win32con.HTLEFT
                    elif rx and self.visibility != QQuickWindow.Visibility.Maximized:
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
                            return True, win32con.HTMAXBUTTON
            elif msg.message in [
                win32con.WM_NCMOUSEHOVER,
                win32con.WM_NCMOUSEMOVE,
                win32con.WM_NCMOUSELEAVE,
                win32con.WM_NCLBUTTONDOWN,
                win32con.WM_NCLBUTTONUP,
            ]:
                if self.maximize_btn is not None:
                    self.handle_mouse_event(msg)
            elif msg.message == win32con.WM_NCCALCSIZE:
                return True, win32con.WVR_REDRAW if msg.wParam else 0
            elif msg.message == win32con.WM_ACTIVATE:
                if (hr := self.add_dwm_effect()) is not None:
                    return True, hr
            elif msg.message == win32con.WM_SYSCOMMAND:
                if (
                    msg.wParam == win32con.SC_RESTORE
                    and self.visibility == QQuickWindow.Visibility.Minimized
                ):
                    if self.prev_visibility == QQuickWindow.Visibility.Maximized:
                        self.show_maximized()
                    else:
                        self.show_normal()
                    return True, 0
            elif msg.message == win32con.WM_SIZE and msg.wParam == win32con.SIZE_MINIMIZED:
                self.prev_visibility = self.visibility
        return super().native_event(event_type, message)

    def handle_mouse_event(self, msg: MSG) -> None:
        if self.maximize_btn is None:
            return
        x_pos, y_pos = self.get_point_from_lparam(msg.lParam)
        top_left = self.maximize_btn.map_to_global(QPoint(0, 0))
        rect = QRect(
            top_left.x() - self.x,
            top_left.y() - self.y,
            self.maximize_btn.width,
            self.maximize_btn.height,
        )

        maximize_btn_hovered = rect.contains(x_pos, y_pos)
        if maximize_btn_hovered:
            if msg.message == win32con.WM_NCLBUTTONDOWN:
                mouse_event_type = QMouseEvent.Type.MouseButtonPress
            elif msg.message == win32con.WM_NCLBUTTONUP:
                mouse_event_type = QMouseEvent.Type.MouseButtonRelease
            mouse_event_type = (
                QMouseEvent.Type.HoverMove
                if self.maximize_btn_hovered
                else QMouseEvent.Type.HoverEnter
            )
        else:
            mouse_event_type = QMouseEvent.Type.HoverLeave
        mouse_btn = (
            Qt.MouseButton.LeftButton
            if msg.message in [win32con.WM_NCLBUTTONDOWN, win32con.WM_NCLBUTTONUP]
            else Qt.MouseButton.NoButton
        )
        QGuiApplication.send_event(
            self.maximize_btn,
            QMouseEvent(
                mouse_event_type,
                QPoint(),
                mouse_btn,
                mouse_btn,
                Qt.KeyboardModifier.NoModifier,
            ),
        )
        self.maximize_btn_hovered = maximize_btn_hovered
