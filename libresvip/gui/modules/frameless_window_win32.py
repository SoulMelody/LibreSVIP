import ctypes
from ctypes.wintypes import HWND, MSG, POINT, RECT, UINT

import win32api
import win32con
import win32gui
from qtpy.QtCore import QObject, QPoint, QRect, Qt
from qtpy.QtGui import QCursor, QMouseEvent
from qtpy.QtQuick import QQuickItem, QQuickWindow
from qtpy.QtWidgets import QApplication


class MARGINS(ctypes.Structure):
    _fields_ = [
        ("cxLeftWidth", ctypes.c_int),
        ("cxRightWidth", ctypes.c_int),
        ("cyTopHeight", ctypes.c_int),
        ("cyBottomHeight", ctypes.c_int),
    ]


class MinMaxInfo(ctypes.Structure):
    _fields_ = [
        ("ptReserved", POINT),
        ("ptMaxSize", POINT),
        ("ptMaxPosition", POINT),
        ("ptMinTrackSize", POINT),
        ("ptMaxTrackSize", POINT),
    ]


class PWindowPos(ctypes.Structure):
    _fields_ = [
        ("hWnd", HWND),
        ("hwndInsertAfter", HWND),
        ("x", ctypes.c_int),
        ("y", ctypes.c_int),
        ("cx", ctypes.c_int),
        ("cy", ctypes.c_int),
        ("flags", UINT),
    ]


class NCCalcSizeParams(ctypes.Structure):
    _fields_ = [("rgrc", RECT * 3), ("lppos", ctypes.POINTER(PWindowPos))]


class Win32FramelessWindow(QQuickWindow):
    def __init__(self, parent: QObject = None, border_width: int = 5):
        super().__init__(parent)
        self.setFlags(
            self.flags()
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Window
            | Qt.WindowType.WindowMinMaxButtonsHint
        )
        self.border_width = border_width
        self.monitor_info = None
        self.maximize_btn = None
        self.maximize_btn_hovered = False
        hwnd = self.winId()
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)

        win32gui.SetWindowLong(
            hwnd,
            win32con.GWL_STYLE,
            style
            | win32con.WS_MAXIMIZEBOX
            | win32con.WS_CAPTION
            | win32con.CS_DBLCLKS
            | win32con.WS_THICKFRAME,
        )

        style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        style &= ~win32con.WS_EX_LAYERED
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, style)
        self.add_shadow_effect()

    @staticmethod
    def is_composition_enabled() -> bool:
        b_result = ctypes.c_int(0)
        ctypes.windll.dwmapi.DwmIsCompositionEnabled(ctypes.byref(b_result))
        return bool(b_result.value)

    def add_shadow_effect(self) -> None:
        if not self.is_composition_enabled():
            return

        dwmapi = ctypes.windll.dwmapi

        hwnd = self.winId()
        margins = MARGINS(-1, -1, -1, -1)
        dwmapi.DwmExtendFrameIntoClientArea(hwnd, ctypes.byref(margins))

    def monitor_nccalcsize(self, msg: MSG) -> None:
        monitor = win32api.MonitorFromWindow(
            msg.hWnd, win32con.MONITOR_DEFAULTTOPRIMARY
        )
        if monitor is None and not self.monitor_info:
            return
        elif monitor is not None:
            self.monitor_info = win32api.GetMonitorInfo(monitor)

        params = ctypes.cast(msg.lParam, ctypes.POINTER(NCCalcSizeParams)).contents
        (
            params.rgrc[0].left,
            params.rgrc[0].top,
            params.rgrc[0].right,
            params.rgrc[0].bottom,
        ) = self.monitor_info["Work"][:4]

    @staticmethod
    def is_window_maximized(hwnd: int) -> bool:
        if not (window_placement := win32gui.GetWindowPlacement(hwnd)):
            return False
        return window_placement[1] == win32con.SW_MAXIMIZE

    def nativeEvent(self, event_type: bytes, message: int) -> tuple[bool, int]:
        if self.maximize_btn is None:
            self.maximize_btn = self.findChild(QQuickItem, "maximizeButton")
        if event_type == b"windows_generic_MSG":
            msg = MSG.from_address(message.__int__())

            if msg.message == win32con.WM_NCHITTEST and self.border_width is not None:
                pos = QCursor.pos()
                x_pos = pos.x() - self.x()
                y_pos = pos.y() - self.y()
                w, h = self.width(), self.height()
                lx = x_pos < self.border_width
                rx = x_pos > w - self.border_width
                ty = y_pos < self.border_width
                by = y_pos > h - self.border_width
                if not self.is_window_maximized(msg.hWnd):
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
                    top_left = self.maximize_btn.mapToGlobal(QPoint(0, 0))
                    rect = QRect(
                        top_left.x() - self.x(),
                        top_left.y() - self.y(),
                        self.maximize_btn.width(),
                        self.maximize_btn.height(),
                    )
                    if rect.contains(x_pos, y_pos):
                        QApplication.sendEvent(
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
                        QApplication.sendEvent(
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
                x_pos = pos.x() - self.x()
                y_pos = pos.y() - self.y()
                if self.maximize_btn is not None:
                    top_left = self.maximize_btn.mapToGlobal(QPoint(0, 0))
                    rect = QRect(
                        top_left.x() - self.x(),
                        top_left.y() - self.y(),
                        self.maximize_btn.width(),
                        self.maximize_btn.height(),
                    )
                    if rect.contains(x_pos, y_pos):
                        QApplication.sendEvent(
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
                x_pos = pos.x() - self.x()
                y_pos = pos.y() - self.y()
                if self.maximize_btn is not None:
                    top_left = self.maximize_btn.mapToGlobal(QPoint(0, 0))
                    rect = QRect(
                        top_left.x() - self.x(),
                        top_left.y() - self.y(),
                        self.maximize_btn.width(),
                        self.maximize_btn.height(),
                    )
                    if rect.contains(x_pos, y_pos):
                        QApplication.sendEvent(
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
                if self.is_window_maximized(msg.hWnd):
                    self.monitor_nccalcsize(msg)
                return True, 0
            elif msg.message == win32con.WM_GETMINMAXINFO:
                if self.is_window_maximized(msg.hWnd):
                    window_rect = win32gui.GetWindowRect(msg.hWnd)
                    if not window_rect:
                        return False, 0

                    monitor = win32api.MonitorFromRect(window_rect)
                    if not monitor:
                        return False, 0

                    self.monitor_info = win32api.GetMonitorInfo(monitor)
                    monitor_rect = self.monitor_info["Monitor"]
                    work_area = self.monitor_info["Work"]

                    info = ctypes.cast(msg.lParam, ctypes.POINTER(MinMaxInfo)).contents

                    info.ptMaxSize.x = work_area[2] - work_area[0]
                    info.ptMaxSize.y = work_area[3] - work_area[1]
                    info.ptMaxTrackSize.x = info.ptMaxSize.x
                    info.ptMaxTrackSize.y = info.ptMaxSize.y

                    info.ptMaxPosition.x = abs(window_rect[0] - monitor_rect[0])
                    info.ptMaxPosition.y = abs(window_rect[1] - monitor_rect[1])
                    return True, 1
        return False, 0
