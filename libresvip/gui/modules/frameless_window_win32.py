import ctypes
from ctypes.wintypes import HWND, LPRECT, MSG, RECT, UINT, WPARAM
from typing import Optional

import win32api
import win32con
import win32gui
import win32print
from qtpy.QtCore import QObject, QPoint, QRect, Qt
from qtpy.QtGui import QCursor, QMouseEvent, QWindow
from qtpy.QtQuick import QQuickItem, QQuickWindow
from qtpy.QtWidgets import QApplication


class MARGINS(ctypes.Structure):
    _fields_ = [
        ("cxLeftWidth", ctypes.c_int),
        ("cxRightWidth", ctypes.c_int),
        ("cyTopHeight", ctypes.c_int),
        ("cyBottomHeight", ctypes.c_int),
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
        self.maximize_btn = None
        self.caption_label = None
        self.maximize_btn_hovered = False
        self.set_borderless()
        screen_geometry = self.screen().availableGeometry()
        self.setPosition(
            (screen_geometry.width() - 1200) // 2,
            (screen_geometry.height() - 800) // 2,
        )
        self.screenChanged.connect(self.on_screen_changed)

    def on_screen_changed(self) -> None:
        hwnd = self.winId()
        win32gui.SetWindowPos(
            hwnd,
            None,
            0,
            0,
            0,
            0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_FRAMECHANGED,
        )

    @property
    def is_composition_enabled(self) -> bool:
        b_result = ctypes.c_int(0)
        ctypes.windll.dwmapi.DwmIsCompositionEnabled(ctypes.byref(b_result))
        return bool(b_result.value)

    def set_borderless(self) -> None:
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

    def add_shadow_effect(self) -> Optional[ctypes.HRESULT]:
        if not self.is_composition_enabled:
            return

        dwmapi = ctypes.windll.dwmapi

        hwnd = self.winId()
        margins = MARGINS(-1, -1, -1, -1)
        return dwmapi.DwmExtendFrameIntoClientArea(hwnd, ctypes.byref(margins))

    @staticmethod
    def is_window_maximized(hwnd: int) -> bool:
        if not (window_placement := win32gui.GetWindowPlacement(hwnd)):
            return False
        return window_placement[1] == win32con.SW_MAXIMIZE

    def get_resize_border_thickness(self, hwnd: int, horizontal: bool = True) -> int:
        window = self.find_window(hwnd)
        if not window:
            return 0

        frame = win32con.SM_CXSIZEFRAME if horizontal else win32con.SM_CYSIZEFRAME
        result = self.get_system_metrics(
            hwnd, frame, horizontal
        ) + self.get_system_metrics(hwnd, 92, horizontal)

        if result > 0:
            return result

        thickness = 8 if self.is_composition_enabled else 4
        return round(thickness * window.devicePixelRatio())

    def get_system_metrics(self, hwnd: int, index: int, horizontal: bool = True) -> int:
        """get system metrics"""
        if not hasattr(ctypes.windll.user32, "GetSystemMetricsForDpi"):
            return win32api.GetSystemMetrics(index)

        dpi = self.get_dpi_for_window(hwnd, horizontal)
        return ctypes.windll.user32.GetSystemMetricsForDpi(index, dpi)

    def get_dpi_for_window(self, hwnd: int, horizontal: bool = True) -> int:
        if hasattr(ctypes.windll.user32, "GetDpiForWindow"):
            return ctypes.windll.user32.GetDpiForWindow(hwnd)

        if not (hdc := win32gui.GetDC(hwnd)):
            return 96

        dpi_x = win32print.GetDeviceCaps(hdc, win32con.LOGPIXELSX)
        dpi_y = win32print.GetDeviceCaps(hdc, win32con.LOGPIXELSY)
        win32gui.ReleaseDC(hwnd, hdc)
        if dpi_x > 0 and horizontal:
            return dpi_x
        elif dpi_y > 0 and not horizontal:
            return dpi_y

        return 96

    def find_window(self, hwnd: int) -> Optional[QWindow]:
        if not hwnd:
            return

        if not (windows := QApplication.topLevelWindows()):
            return

        hwnd = int(hwnd)
        for window in windows:
            if window and window.winId() == hwnd:
                return window

    def nativeEvent(self, event_type: bytes, message: int) -> tuple[bool, int]:
        if self.caption_label is None:
            self.caption_label = self.findChild(QQuickItem, "captionLabel")
        if self.maximize_btn is None:
            self.maximize_btn = self.findChild(QQuickItem, "maximizeButton")
        if event_type == b"windows_generic_MSG":
            msg = MSG.from_address(message.__int__())

            if msg.message == win32con.WM_NCHITTEST and self.border_width is not None:
                pos = QCursor.pos()
                x_pos = pos.x() - self.x()
                y_pos = pos.y() - self.y()
                w, h = self.width(), self.height()
                bw = 0 if self.is_window_maximized(msg.hWnd) else self.border_width
                lx = x_pos < bw
                rx = x_pos > w - bw
                ty = y_pos < bw
                by = y_pos > h - bw
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
                if self.caption_label is not None:
                    top_left = self.caption_label.mapToGlobal(QPoint(0, 0))
                    rect = QRect(
                        top_left.x() - self.x(),
                        top_left.y() - self.y(),
                        self.caption_label.width(),
                        self.caption_label.height(),
                    )
                    if rect.contains(x_pos, y_pos):
                        return True, win32con.HTCAPTION
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
                if (
                    msg.message == win32con.WM_NCRBUTTONUP
                    and msg.wParam == win32con.HTCAPTION
                ):
                    pos = QCursor.pos()
                    hwnd = self.winId()
                    if menu := ctypes.windll.user32.GetSystemMenu(hwnd, False):
                        if cmd := ctypes.windll.user32.TrackPopupMenuEx(
                            menu,
                            win32con.TPM_LEFTALIGN
                            | win32con.TPM_TOPALIGN
                            | win32con.TPM_NONOTIFY
                            | win32con.TPM_RETURNCMD,
                            pos.x(),
                            pos.y(),
                            hwnd,
                            None,
                        ):
                            ctypes.windll.user32.PostMessageW(
                                hwnd, win32con.WM_SYSCOMMAND, WPARAM(cmd), 0
                            )
            elif msg.message == win32con.WM_NCCALCSIZE:
                if msg.wParam:
                    rect = ctypes.cast(
                        msg.lParam, ctypes.POINTER(NCCalcSizeParams)
                    ).contents.rgrc[0]
                else:
                    rect = ctypes.cast(msg.lParam, LPRECT).contents
                if self.is_window_maximized(msg.hWnd):
                    ty = self.get_resize_border_thickness(msg.hWnd, False)
                    rect.top += ty
                    rect.bottom -= ty

                    tx = self.get_resize_border_thickness(msg.hWnd, True)
                    rect.left += tx
                    rect.right -= tx

                result = 0 if not msg.wParam else win32con.WVR_REDRAW
                return True, result
            elif msg.message == win32con.WM_ACTIVATE:
                if (hr := self.add_shadow_effect()) is not None:
                    return True, hr
        return super().nativeEvent(event_type, message)
