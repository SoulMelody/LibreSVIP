import ctypes
from ctypes.wintypes import MSG, WPARAM
from typing import Optional

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
        self.prev_visibility = None

    @property
    def hwnd(self) -> int:
        return self.winId()

    @property
    def is_composition_enabled(self) -> bool:
        b_result = ctypes.c_int(0)
        ctypes.windll.dwmapi.DwmIsCompositionEnabled(ctypes.byref(b_result))
        return bool(b_result.value)

    def set_borderless(self) -> None:
        hwnd = self.hwnd
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

        margins = MARGINS(-1, -1, -1, -1)
        return dwmapi.DwmExtendFrameIntoClientArea(self.hwnd, ctypes.byref(margins))

    def nativeEvent(self, event_type: bytes, message: int) -> tuple[bool, int]:
        if self.caption_label is None:
            self.caption_label = self.findChild(QQuickItem, "captionLabel")
        if self.maximize_btn is None:
            self.maximize_btn = self.findChild(QQuickItem, "maximizeButton")
        if event_type == b"windows_generic_MSG":
            msg = MSG.from_address(message.__int__())

            if msg.message == win32con.WM_NCHITTEST and self.border_width is not None:
                if msg.hWnd == self.hwnd:
                    pos = QCursor.pos()
                    x_pos = pos.x() - self.x()
                    y_pos = pos.y() - self.y()
                    w, h = self.width(), self.height()
                    bw = (
                        0
                        if self.visibility() == QQuickWindow.Visibility.Maximized
                        else self.border_width
                    )
                    lx = x_pos < bw
                    rx = x_pos > w - bw
                    ty = y_pos < bw
                    by = y_pos > h - bw
                    if not self.visibility() == QQuickWindow.Visibility.Maximized:
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
                    hwnd = self.hwnd
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
                return True, win32con.WVR_REDRAW if msg.wParam else 0
            elif msg.message == win32con.WM_ACTIVATE:
                if (hr := self.add_shadow_effect()) is not None:
                    return True, hr
            elif msg.message == win32con.WM_SYSCOMMAND:
                if msg.wParam == win32con.SC_RESTORE:
                    if self.visibility() == QQuickWindow.Visibility.Minimized:
                        if self.prev_visibility == QQuickWindow.Visibility.Maximized:
                            self.showMaximized()
                        else:
                            self.showNormal()
                        return True, 0
            elif msg.message == win32con.WM_SIZE:
                if msg.wParam == win32con.SIZE_MINIMIZED:
                    self.prev_visibility = self.visibility()
        return super().nativeEvent(event_type, message)
