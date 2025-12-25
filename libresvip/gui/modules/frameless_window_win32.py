# mypy: disable-error-code="attr-defined"
import ctypes
from ctypes.wintypes import HWND, LPARAM, MSG, POINT, RECT, UINT
from typing import SupportsInt

from PySide6.QtCore import QByteArray, QPoint, QRect, Qt, Slot
from PySide6.QtGui import QCursor, QGuiApplication, QMouseEvent, QWindow
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


class PWINDOWPOS(ctypes.Structure):
    _fields_ = (
        ("hWnd", HWND),
        ("hwndInsertAfter", HWND),
        ("x", ctypes.c_int),
        ("y", ctypes.c_int),
        ("cx", ctypes.c_int),
        ("cy", ctypes.c_int),
        ("flags", UINT),
    )


class NCCALCSIZEPARAMS(ctypes.Structure):
    _fields_ = (("rgrc", RECT * 3), ("lppos", ctypes.POINTER(PWINDOWPOS)))


class WINDOWPLACEMENT(ctypes.Structure):
    _fields_ = (
        ("length", UINT),
        ("flags", UINT),
        ("showCmd", UINT),
        ("ptMinPosition", POINT),
        ("ptMaxPosition", POINT),
        ("rcNormalPosition", RECT),
    )


class APPBARDATA(ctypes.Structure):
    _fields_ = (
        ("cbSize", UINT),
        ("hWnd", HWND),
        ("uCallbackMessage", UINT),
        ("uEdge", UINT),
        ("rc", RECT),
        ("lParam", LPARAM),
    )


def is_maximized(hwnd: int) -> bool:
    wp = WINDOWPLACEMENT()
    wp.length = ctypes.sizeof(WINDOWPLACEMENT)
    ctypes.windll.user32.GetWindowPlacement(hwnd, ctypes.byref(wp))
    return wp.showCmd == win32con.SIZE_MAXIMIZED


@QmlElement
class FramelessWindow(QQuickWindow):
    def __init__(self, parent: QWindow | None = None, border_width: int = 5) -> None:
        super().__init__(parent)
        self.flags: Qt.WindowType = (
            self.flags
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Window
            | Qt.WindowType.WindowMinMaxButtonsHint
        )
        self.border_width = border_width
        self.maximize_btn: QQuickItem | None = None
        self.maximize_btn_hovered = False
        self.set_borderless()
        screen_geometry = self.screen().available_geometry
        self.set_position(
            (screen_geometry.width() - 1200) // 2,
            (screen_geometry.height() - 800) // 2,
        )

    @Slot()
    def start_system_move(self) -> None:
        ctypes.windll.user32.ReleaseCapture()
        ctypes.windll.user32.SendMessageW(
            self.hwnd, win32con.WM_SYSCOMMAND, win32con.SC_MOVE + win32con.HTCAPTION, 0
        )

    @Slot()
    def click_maximize_btn(self) -> None:
        if self.visibility != QQuickWindow.Visibility.Maximized:
            ctypes.windll.user32.SendMessageW(
                self.hwnd, win32con.WM_SYSCOMMAND, win32con.SC_MAXIMIZE, 0
            )
        else:
            ctypes.windll.user32.SendMessageW(
                self.hwnd, win32con.WM_SYSCOMMAND, win32con.SC_RESTORE, 0
            )

    @Slot()
    def click_minimize_btn(self) -> None:
        ctypes.windll.user32.SendMessageW(
            self.hwnd, win32con.WM_SYSCOMMAND, win32con.SC_MINIMIZE, 0
        )

    @property
    def hwnd(self) -> int:
        return self.win_id()

    @property
    def is_composition_enabled(self) -> bool:
        b_result = ctypes.c_int(0)
        ctypes.windll.dwmapi.DwmIsCompositionEnabled(ctypes.byref(b_result))
        return bool(b_result.value)

    def get_resize_border_thickness(self, frame: int) -> int:
        device_pixel_ratio = self.screen().device_pixel_ratio
        result = ctypes.windll.user32.GetSystemMetrics(
            frame
        ) + ctypes.windll.user32.GetSystemMetrics(win32con.SM_CXPADDEDBORDER)
        if result > 0:
            return result
        thickness = 8 if self.is_composition_enabled else 4
        return round(thickness * device_pixel_ratio)

    def set_borderless(self) -> None:
        hwnd = self.hwnd
        user32 = ctypes.windll.user32

        style = user32.GetWindowLongPtrW(hwnd, win32con.GWL_STYLE)
        style &= ~win32con.WS_SYSMENU
        user32.SetWindowLongPtrW(
            hwnd,
            win32con.GWL_STYLE,
            style
            | win32con.WS_MAXIMIZEBOX
            | win32con.WS_CAPTION
            | win32con.CS_DBLCLKS
            | win32con.WS_THICKFRAME,
        )

    def add_dwm_effect(self) -> SupportsInt | None:
        if not self.is_composition_enabled:
            return None

        dwmapi = ctypes.windll.dwmapi

        margins = MARGINS(-1, -1, -1, -1)
        return dwmapi.DwmExtendFrameIntoClientArea(self.hwnd, ctypes.byref(margins))

    def native_event(
        self, event_type: QByteArray | bytes | bytearray | memoryview, message: SupportsInt
    ) -> object:
        if self.maximize_btn is None:
            self.maximize_btn = self.find_child(QQuickItem, "maximizeButton")
        if event_type == b"windows_generic_MSG":
            msg = MSG.from_address(int(message))
            if msg.hWnd is None:
                return False

            if msg.message == win32con.WM_NCHITTEST and self.border_width is not None:
                if msg.hWnd == self.hwnd:
                    bw = (
                        0
                        if self.visibility == QQuickWindow.Visibility.Maximized
                        else self.border_width
                    )
                    cursor_pos = QCursor.pos()
                    point = self.map_from_global(cursor_pos)
                    lx = point.x() < bw
                    rx = point.x() > self.width - bw
                    top_y = point.y() < bw
                    bottom_y = point.y() > self.height - bw
                    if self.visibility != QQuickWindow.Visibility.Maximized:
                        if lx and top_y:
                            return True, win32con.HTTOPLEFT
                        elif rx and bottom_y:
                            return True, win32con.HTBOTTOMRIGHT
                        elif rx and top_y:
                            return True, win32con.HTTOPRIGHT
                        elif lx and bottom_y:
                            return True, win32con.HTBOTTOMLEFT
                        elif top_y:
                            return True, win32con.HTTOP
                        elif bottom_y:
                            return True, win32con.HTBOTTOM
                        elif lx:
                            return True, win32con.HTLEFT
                        elif rx:
                            return True, win32con.HTRIGHT
                    if self.maximize_btn is not None:
                        top_left = self.maximize_btn.map_from_global(cursor_pos)
                        rect = QRect(
                            0,
                            0,
                            self.maximize_btn.width,
                            self.maximize_btn.height,
                        )
                        if rect.contains(top_left.to_point()):
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
                client_rect = ctypes.cast(
                    msg.lParam, ctypes.POINTER(NCCALCSIZEPARAMS)
                ).contents.rgrc[0]
                if is_maximized(msg.hWnd) and msg.wParam:
                    ty = self.get_resize_border_thickness(win32con.SM_CYSIZEFRAME)
                    client_rect.top += ty
                    client_rect.bottom -= ty
                    tx = self.get_resize_border_thickness(win32con.SM_CXSIZEFRAME)
                    client_rect.left += tx
                    client_rect.right -= tx
                    abd = APPBARDATA()
                    ctypes.memset(ctypes.byref(abd), 0, ctypes.sizeof(abd))
                    abd.cbSize = ctypes.sizeof(APPBARDATA)
                    taskbar_state = ctypes.windll.shell32.SHAppBarMessage(
                        win32con.ABM_GETSTATE, ctypes.byref(abd)
                    )
                    if taskbar_state & win32con.ABS_AUTOHIDE:
                        edge = -1
                        abd2 = APPBARDATA()
                        ctypes.memset(ctypes.byref(abd2), 0, ctypes.sizeof(abd2))
                        abd2.cbSize = ctypes.sizeof(APPBARDATA)
                        abd2.hWnd = ctypes.windll.user32.FindWindowW("Shell_TrayWnd", None)
                        if abd2.hWnd:
                            window_monitor = ctypes.windll.user32.MonitorFromWindow(
                                msg.hWnd, win32con.MONITOR_DEFAULTTONEAREST
                            )
                            if window_monitor:
                                taskbar_monitor = ctypes.windll.user32.MonitorFromWindow(
                                    abd2.hWnd, win32con.MONITOR_DEFAULTTONEAREST
                                )
                                if taskbar_monitor and taskbar_monitor == window_monitor:
                                    ctypes.windll.shell32.SHAppBarMessage(
                                        win32con.ABM_GETTASKBARPOS, ctypes.byref(abd2)
                                    )
                                    edge = abd2.uEdge
                        top = edge == 1
                        bottom = edge == 3
                        left = edge == 0
                        right = edge == 2
                        if top:
                            client_rect.top += 1
                        elif bottom:
                            client_rect.bottom -= 1
                        elif left:
                            client_rect.left += 1
                        elif right:
                            client_rect.right -= 1
                        else:
                            client_rect.bottom -= 1
                return True, win32con.WVR_REDRAW if msg.wParam else 0
            elif msg.message == win32con.WM_ACTIVATE and (hr := self.add_dwm_effect()) is not None:
                return True, hr
        return super().native_event(event_type, message)

    def handle_mouse_event(self, msg: MSG) -> None:
        if self.maximize_btn is None:
            return
        cursor_pos = QCursor.pos()
        top_left = self.maximize_btn.map_from_global(cursor_pos)
        rect = QRect(
            0,
            0,
            self.maximize_btn.width,
            self.maximize_btn.height,
        )

        maximize_btn_hovered = rect.contains(top_left.to_point())
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
