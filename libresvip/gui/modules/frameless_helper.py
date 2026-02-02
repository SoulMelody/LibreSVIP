# mypy: disable-error-code="arg-type"
import sys
from typing import SupportsInt

from PySide6.QtCore import (
    Property,
    QAbstractNativeEventFilter,
    QEvent,
    QObject,
    QPoint,
    QPointF,
    QRectF,
    Qt,
    Signal,
    Slot,
)
from PySide6.QtGui import QCursor, QMouseEvent
from PySide6.QtQml import QmlElement
from PySide6.QtQuick import QQuickItem, QQuickWindow

from __feature__ import snake_case, true_property  # isort:skip # noqa: F401

from .application import app

QML_IMPORT_NAME = "FramelessWindow"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0

if sys.platform == "win32":
    from ctypes import (
        POINTER,
        Structure,
        WinDLL,
        byref,
        c_int,
        cast,
        memset,
        sizeof,
    )
    from ctypes.wintypes import HWND, LPARAM, MSG, POINT, RECT, UINT, WPARAM

    GWL_STYLE = -16
    CS_DBLCLKS = 8
    WS_CAPTION = 0x00C00000
    WS_THICKFRAME = 0x00040000
    WS_MAXIMIZEBOX = 0x00010000

    SWP_FRAMECHANGED = 0x0020
    SWP_NOMOVE = 0x0002
    SWP_NOSIZE = 0x0001
    SWP_NOZORDER = 0x0004
    SWP_NOACTIVATE = 0x0100

    WM_GETMINMAXINFO = 0x0024
    WM_WINDOWPOSCHANGING = 0x0046
    WM_NCCALCSIZE = 0x0083
    WM_NCHITTEST = 0x0084
    WM_NCLBUTTONDOWN = 0x00A1
    WM_NCLBUTTONUP = 0x00A2
    WM_NCLBUTTONDBLCLK = 0x00A3
    WM_NCRBUTTONDOWN = 0x00A4
    WM_NCRBUTTONUP = 0x00A5
    WM_SYSCOMMAND = 0x0112
    WM_NCMOUSELEAVE = 0x02A2
    WM_MOUSELEAVE = 0x02A3

    WVR_REDRAW = 0x0001

    HTCLIENT = 1
    HTCAPTION = 2
    HTMAXBUTTON = 9
    HTLEFT = 10
    HTRIGHT = 11
    HTTOP = 12
    HTTOPLEFT = 13
    HTTOPRIGHT = 14
    HTBOTTOM = 15
    HTBOTTOMLEFT = 16
    HTBOTTOMRIGHT = 17

    SPI_GETWORKAREA = 0x0030

    SM_CXSIZEFRAME = 32
    SM_CYSIZEFRAME = 33
    SM_CXPADDEDBORDER = 92

    SW_SHOWMAXIMIZED = 3
    SW_SHOWMINIMIZED = 2
    SW_SHOWNORMAL = 1

    SC_MOVE = 0xF010
    SC_SIZE = 0xF020
    SC_MAXIMIZE = 0xF030
    SC_RESTORE = 0xF120

    MF_ENABLED = 0x00000000
    MF_DISABLED = 0x00000001
    MF_GRAYED = 0x00000002

    TPM_RETURNCMD = 0x0100
    TPM_LEFTALIGN = 0x0000
    TPM_RIGHTALIGN = 0x0008

    ABM_GETSTATE = 4
    ABM_GETTASKBARPOS = 5
    ABS_AUTOHIDE = 1

    MONITOR_DEFAULTTONEAREST = 2
    MONITOR_DEFAULTTOPRIMARY = 1

    class MARGINS(Structure):
        _fields_ = [
            ("cxLeftWidth", c_int),
            ("cxRightWidth", c_int),
            ("cyTopHeight", c_int),
            ("cyBottomHeight", c_int),
        ]

    class PWINDOWPOS(Structure):
        _fields_ = [
            ("hWnd", HWND),
            ("hwndInsertAfter", HWND),
            ("x", c_int),
            ("y", c_int),
            ("cx", c_int),
            ("cy", c_int),
            ("flags", UINT),
        ]

    class NcCalcsizeParams(Structure):
        _fields_ = [("rgrc", RECT * 3), ("lppos", POINTER(PWINDOWPOS))]

    class MINMAXINFO(Structure):
        _fields_ = [
            ("ptReserved", POINT),
            ("ptMaxSize", POINT),
            ("ptMaxPosition", POINT),
            ("ptMinTrackSize", POINT),
            ("ptMaxTrackSize", POINT),
        ]

    class WINDOWPLACEMENT(Structure):
        _fields_ = (
            ("length", UINT),
            ("flags", UINT),
            ("showCmd", UINT),
            ("ptMinPosition", POINT),
            ("ptMaxPosition", POINT),
            ("rcNormalPosition", RECT),
        )

    class APPBARDATA(Structure):
        _fields_ = (
            ("cbSize", UINT),
            ("hWnd", HWND),
            ("uCallbackMessage", UINT),
            ("uEdge", UINT),
            ("rc", RECT),
            ("lParam", LPARAM),
        )

    LPNCCALCSIZE_PARAMS = POINTER(NcCalcsizeParams)
    qt_native_event_type = b"windows_generic_MSG"

    user32 = WinDLL("user32")
    dwmapi = WinDLL("dwmapi")
    shell32 = WinDLL("shell32")

    GetWindowLongPtrW = user32.GetWindowLongPtrW
    SetWindowLongPtrW = user32.SetWindowLongPtrW
    SetWindowPos = user32.SetWindowPos
    IsZoomed = user32.IsZoomed
    ScreenToClient = user32.ScreenToClient
    GetClientRect = user32.GetClientRect
    SystemParametersInfoW = user32.SystemParametersInfoW
    GetSystemMetrics = user32.GetSystemMetrics
    DwmExtendFrameIntoClientArea = dwmapi.DwmExtendFrameIntoClientArea
    PostMessageW = user32.PostMessageW
    TrackPopupMenu = user32.TrackPopupMenu
    EnableMenuItem = user32.EnableMenuItem
    GetSystemMenu = user32.GetSystemMenu

    def is_composition_enabled() -> bool:
        b_result = c_int(0)
        dwmapi.DwmIsCompositionEnabled(byref(b_result))
        return bool(b_result.value)

    def set_shadow(hwnd: HWND) -> None:
        margins = MARGINS(-1, -1, -1, -1)
        DwmExtendFrameIntoClientArea(hwnd, byref(margins))

    def apply_frameless_style(hwnd: HWND) -> None:
        style = GetWindowLongPtrW(hwnd, GWL_STYLE)
        SetWindowLongPtrW(
            hwnd, GWL_STYLE, style | WS_CAPTION | WS_THICKFRAME | WS_MAXIMIZEBOX | CS_DBLCLKS
        )
        SetWindowPos(
            hwnd,
            None,
            0,
            0,
            0,
            0,
            SWP_FRAMECHANGED | SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_NOACTIVATE,
        )
        if is_composition_enabled():
            set_shadow(hwnd)


@QmlElement
class FramelessHelper(QQuickItem, QAbstractNativeEventFilter):
    titlebar_item_changed = Signal()
    maximize_button_changed = Signal()

    def __init__(self) -> None:
        QQuickItem.__init__(self)
        QAbstractNativeEventFilter.__init__(self)
        self._current = HWND(0)
        self._edges = 0
        self._margins = 5
        self._titlebar_item = None
        self._maximize_button = None

    @property
    def is_windows_11_or_newer(self) -> bool:
        if sys.platform != "win32":
            return False
        windows_version = sys.getwindowsversion()
        return windows_version.major >= 10 and windows_version.build >= 22000

    def get_maximize_button(self) -> QQuickItem | None:
        return self._maximize_button

    def set_maximize_button(self, value: QQuickItem | None) -> None:
        self._maximize_button = value
        self.maximize_button_changed.emit()

    maximize_button = Property(
        QQuickItem,
        fget=get_maximize_button,
        fset=set_maximize_button,
        notify=maximize_button_changed,
    )

    def get_titlebar_item(self) -> QQuickItem | None:
        return self._titlebar_item

    def set_titlebar_item(self, value: QQuickItem | None) -> None:
        self._titlebar_item = value
        self.titlebar_item_changed.emit()

    titlebar_item = Property(
        QQuickItem, fget=get_titlebar_item, fset=set_titlebar_item, notify=titlebar_item_changed
    )

    @Slot()
    def on_destruction(self) -> None:
        if sys.platform == "win32":
            app.remove_native_event_filter(self)

    @Slot()
    def refresh_shadow(self) -> None:
        if sys.platform == "win32" and self.window():
            hwnd = self.window().win_id()
            if hwnd:
                apply_frameless_style(hwnd)
                self._current = hwnd

    def component_complete(self) -> None:
        window = self.window()
        self._current = window.win_id()
        window.flags |= (
            Qt.WindowType.Window
            | Qt.WindowType.CustomizeWindowHint
            | Qt.WindowType.WindowMaximizeButtonHint
            | Qt.WindowType.FramelessWindowHint
        )
        window.install_event_filter(self)

        if sys.platform == "win32":
            app.install_native_event_filter(self)
            apply_frameless_style(self._current)

    def native_event_filter(self, event_type: bytes, message: SupportsInt) -> tuple[bool, int]:
        if sys.platform == "win32":
            if event_type != qt_native_event_type or message is None:
                return False, 0

            msg = MSG.from_address(message.__int__())
            hwnd = msg.hWnd

            if hwnd is None or hwnd != self._current:
                return False, 0

            u_msg = msg.message
            if u_msg == WM_WINDOWPOSCHANGING:
                return self._handle_window_pos_changing(msg.lParam)
            elif u_msg == WM_NCCALCSIZE:
                return self._handle_nc_calc_size(hwnd, msg.wParam, msg.lParam)
            elif u_msg == WM_NCHITTEST:
                return self._handle_nc_hit_test(hwnd, msg.lParam)
            elif u_msg == WM_GETMINMAXINFO:
                return self._handle_get_min_max_info(msg.lParam)
            elif u_msg == WM_NCRBUTTONDOWN and msg.wParam == HTCAPTION:
                return self._handle_nc_rbutton_down(hwnd)
            elif self.is_windows_11_or_newer and self.maximize_button is not None:
                if u_msg == WM_NCLBUTTONDOWN and msg.wParam == HTMAXBUTTON:
                    self._set_maximize_pressed(True)
                    return True, 1
                elif u_msg == WM_NCLBUTTONUP and msg.wParam == HTMAXBUTTON:
                    self._set_maximize_pressed(False)
                    return True, 1
                elif u_msg in (WM_NCMOUSELEAVE, WM_MOUSELEAVE):
                    self._set_maximize_hovered(False)
        return False, 0

    def _handle_nc_rbutton_down(self, hwnd: HWND) -> tuple[bool, int]:
        window = self.window()
        pos = window.position()
        offset = window.map_from_global(QCursor.pos())
        self._show_system_menu(QPoint(pos.x() + offset.x(), pos.y() + offset.y()))
        return True, 1

    def _show_system_menu(self, point: QPoint) -> None:
        if sys.platform == "win32":
            screen = self.window().screen()
            origin = screen.geometry.top_left()
            native_pos = (
                QPointF(QPointF(point - origin) * self.window().device_pixel_ratio()).to_point()
                + origin
            )
            hwnd = self.window().win_id()
            h_menu = GetSystemMenu(hwnd, False)
            if self._is_maximized():
                EnableMenuItem(h_menu, SC_MOVE, MF_DISABLED | MF_GRAYED)
                EnableMenuItem(h_menu, SC_SIZE, MF_DISABLED | MF_GRAYED)
                EnableMenuItem(h_menu, SC_MAXIMIZE, MF_DISABLED | MF_GRAYED)
                EnableMenuItem(h_menu, SC_RESTORE, MF_ENABLED)
            else:
                EnableMenuItem(h_menu, SC_MOVE, MF_ENABLED)
                EnableMenuItem(h_menu, SC_SIZE, MF_ENABLED)
                EnableMenuItem(h_menu, SC_MAXIMIZE, MF_ENABLED)
                EnableMenuItem(h_menu, SC_RESTORE, MF_DISABLED | MF_GRAYED)

            result = TrackPopupMenu(
                h_menu,
                (TPM_RETURNCMD | (TPM_RIGHTALIGN if app.is_right_to_left else TPM_LEFTALIGN)),
                native_pos.x(),
                native_pos.y(),
                0,
                hwnd,
                0,
            )
            if result:
                PostMessageW(hwnd, WM_SYSCOMMAND, result, 0)

    def _handle_window_pos_changing(self, l_param: LPARAM) -> tuple[bool, int]:
        wp = cast(l_param, POINTER(PWINDOWPOS)).contents
        if wp is not None and ((wp.flags & SWP_NOZORDER) == 0):
            wp.flags |= SWP_NOACTIVATE
        return False, 0

    def _handle_nc_calc_size(
        self, hwnd: HWND, w_param: WPARAM, l_param: LPARAM
    ) -> tuple[bool, int]:
        client_rect = cast(l_param, POINTER(NcCalcsizeParams)).contents.rgrc[0]
        is_maximum = bool(IsZoomed(hwnd))
        if is_maximum and w_param:
            frame_y = GetSystemMetrics(SM_CYSIZEFRAME) + GetSystemMetrics(SM_CXPADDEDBORDER)
            client_rect.top += frame_y
            client_rect.bottom -= frame_y

            frame_x = GetSystemMetrics(SM_CXSIZEFRAME) + GetSystemMetrics(SM_CXPADDEDBORDER)
            client_rect.left += frame_x
            client_rect.right -= frame_x
            abd = APPBARDATA()
            memset(byref(abd), 0, sizeof(abd))
            abd.cbSize = sizeof(APPBARDATA)
            taskbar_state = shell32.SHAppBarMessage(ABM_GETSTATE, byref(abd))
            if taskbar_state & ABS_AUTOHIDE:
                edge = -1
                abd2 = APPBARDATA()
                memset(byref(abd2), 0, sizeof(abd2))
                abd2.cbSize = sizeof(APPBARDATA)
                abd2.hWnd = user32.FindWindowW("Shell_TrayWnd", None)
                if abd2.hWnd:
                    window_monitor = user32.MonitorFromWindow(hwnd, MONITOR_DEFAULTTONEAREST)
                    if window_monitor:
                        taskbar_monitor = user32.MonitorFromWindow(
                            abd2.hWnd, MONITOR_DEFAULTTONEAREST
                        )
                        if taskbar_monitor and taskbar_monitor == window_monitor:
                            shell32.SHAppBarMessage(ABM_GETTASKBARPOS, byref(abd2))
                            edge = int(abd2.uEdge)
                top = edge == Qt.Edge.TopEdge.value
                bottom = edge == Qt.Edge.BottomEdge.value
                left = edge == Qt.Edge.LeftEdge.value
                right = edge == Qt.Edge.RightEdge.value
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
        return True, WVR_REDRAW if w_param else 0

    def _handle_nc_hit_test(self, hwnd: HWND, l_param: LPARAM) -> tuple[bool, int]:
        if self.is_windows_11_or_newer and self.maximize_button is not None:
            if self._hit_maximize_button():
                self._set_maximize_hovered(True)
                return True, HTMAXBUTTON
            self._set_maximize_hovered(False)
            self._set_maximize_pressed(False)
        cursor_pos = QCursor.pos()
        point = self.window().map_from_global(cursor_pos)
        logical_x = point.x()
        logical_y = point.y()

        client_width = self.window().width
        client_height = self.window().height
        margins = self._margins

        left = logical_x < margins
        right = logical_x > client_width - margins
        top = logical_y < margins
        bottom = logical_y > client_height - margins

        if not self._is_maximized():
            result = self._get_hit_test_result(left, right, top, bottom)
            if result != 0:
                return True, result

        if self._hit_title_bar():
            return True, HTCAPTION
        return True, HTCLIENT

    def _get_hit_test_result(self, left: bool, right: bool, top: bool, bottom: bool) -> int:
        if left and top:
            return HTTOPLEFT
        if left and bottom:
            return HTBOTTOMLEFT
        if right and top:
            return HTTOPRIGHT
        if right and bottom:
            return HTBOTTOMRIGHT
        if left:
            return HTLEFT
        if right:
            return HTRIGHT
        if top:
            return HTTOP
        if bottom:
            return HTBOTTOM
        return 0

    def _handle_get_min_max_info(self, l_param: LPARAM) -> tuple[bool, int]:
        minmax_info = cast(l_param, POINTER(MINMAXINFO)).contents
        pixel_ratio = self.window().device_pixel_ratio()
        geometry = self.window().screen().available_geometry
        rect = RECT()
        SystemParametersInfoW(SPI_GETWORKAREA, 0, byref(rect), 0)
        minmax_info.ptMaxPosition.x = rect.left
        minmax_info.ptMaxPosition.y = rect.top
        minmax_info.ptMaxSize.x = int(geometry.width() * pixel_ratio)
        minmax_info.ptMaxSize.y = int(geometry.height() * pixel_ratio)
        return False, 0

    def event_filter(self, watched: QObject, event: QEvent) -> bool:
        if self.window() is None:
            return False

        event_type = event.type()

        if event_type == QEvent.Type.MouseButtonPress:
            return self._handle_mouse_button_press(event)
        elif event_type == QEvent.Type.MouseButtonRelease:
            self._edges = 0
            return False
        elif event_type == QEvent.Type.MouseMove:
            return self._handle_mouse_move(event)

        return super().event_filter(watched, event)

    @Slot()
    def show_maximized(self) -> None:
        if sys.platform == "win32":
            hwnd = self.window().win_id()
            user32.ShowWindow(hwnd, SW_SHOWMAXIMIZED)
        else:
            self.window().show_maximized()

    @Slot()
    def show_minimized(self) -> None:
        if sys.platform == "win32":
            hwnd = self.window().win_id()
            user32.ShowWindow(hwnd, SW_SHOWMINIMIZED)
        else:
            self.window().show_minimized()

    @Slot()
    def show_normal(self) -> None:
        if sys.platform == "win32":
            hwnd = self.window().win_id()
            user32.ShowWindow(hwnd, SW_SHOWNORMAL)
        else:
            self.window().show_normal()

    @Slot()
    def start_system_move(self) -> None:
        if sys.platform == "win32":
            hwnd = self.window().win_id()
            user32.ReleaseCapture()
            user32.SendMessageW(hwnd, WM_SYSCOMMAND, SC_MOVE + HTCAPTION, 0)
        else:
            self.window().start_system_move()

    def _handle_mouse_button_press(self, mouse_event: QMouseEvent) -> bool:
        if mouse_event.button() != Qt.MouseButton.LeftButton:
            return False

        if self._edges != 0:
            self._update_cursor(self._edges)
            self.window().start_system_resize(Qt.Edge(self._edges))
            return False
        return False

    def _handle_mouse_move(self, event: QMouseEvent) -> bool:
        if self._is_maximized():
            return False

        win = self.window()
        p = event.position()
        margins = self._margins

        in_interior = (
            margins <= p.x() <= win.width - margins and margins <= p.y() <= win.height - margins
        )
        if in_interior:
            if self._edges != 0:
                self._edges = 0
                self._update_cursor(self._edges)
            return False

        self._edges = self._calc_resize_edges(p, win.width, win.height)
        self._update_cursor(self._edges)
        return False

    def _calc_resize_edges(self, pos: QPointF, width: float, height: float) -> int:
        edges = 0
        if pos.x() < self._margins:
            edges |= Qt.Edge.LeftEdge.value
        elif pos.x() > width - self._margins:
            edges |= Qt.Edge.RightEdge.value
        if pos.y() < self._margins:
            edges |= Qt.Edge.TopEdge.value
        elif pos.y() > height - self._margins:
            edges |= Qt.Edge.BottomEdge.value
        return edges

    def _contains_cursor_to_item(self, item: QQuickItem) -> bool:
        try:
            if not item or not item.visible:
                return False
            point = item.window().map_from_global(QCursor.pos())
            rect = QRectF(item.map_to_item(item.window().content_item, QPointF(0, 0)), item.size())
            return rect.contains(point)
        except RuntimeError:
            pass
        return False

    def _is_maximized(self) -> bool:
        return self.window().visibility == QQuickWindow.Visibility.Maximized

    def _update_cursor(self, edges: int) -> None:
        cursor_map = {
            0: Qt.CursorShape.ArrowCursor,
            Qt.Edge.LeftEdge.value: Qt.CursorShape.SizeHorCursor,
            Qt.Edge.RightEdge.value: Qt.CursorShape.SizeHorCursor,
            Qt.Edge.TopEdge.value: Qt.CursorShape.SizeVerCursor,
            Qt.Edge.BottomEdge.value: Qt.CursorShape.SizeVerCursor,
            Qt.Edge.LeftEdge.value | Qt.Edge.TopEdge.value: Qt.CursorShape.SizeFDiagCursor,
            Qt.Edge.RightEdge.value | Qt.Edge.BottomEdge.value: Qt.CursorShape.SizeFDiagCursor,
            Qt.Edge.RightEdge.value | Qt.Edge.TopEdge.value: Qt.CursorShape.SizeBDiagCursor,
            Qt.Edge.LeftEdge.value | Qt.Edge.BottomEdge.value: Qt.CursorShape.SizeBDiagCursor,
        }
        self.window().set_cursor(cursor_map.get(edges, Qt.CursorShape.ArrowCursor))

    def _hit_title_bar(self) -> bool:
        if self._titlebar_item:
            return self._contains_cursor_to_item(self._titlebar_item)
        return False

    def _hit_maximize_button(self) -> bool:
        if self._maximize_button:
            return self._contains_cursor_to_item(self._maximize_button)
        return False

    def _set_maximize_pressed(self, val: bool) -> None:
        app.send_event(
            self.maximize_button,
            QMouseEvent(
                QEvent.Type.MouseButtonPress if val else QEvent.Type.MouseButtonRelease,
                QPoint(),
                Qt.MouseButton.LeftButton,
                Qt.MouseButton.LeftButton,
                Qt.KeyboardModifier.NoModifier,
            ),
        )

    def _set_maximize_hovered(self, val: bool) -> None:
        app.send_event(
            self.maximize_button,
            QMouseEvent(
                QEvent.Type.HoverEnter if val else QEvent.Type.HoverLeave,
                QPoint(),
                Qt.MouseButton.NoButton,
                Qt.MouseButton.NoButton,
                Qt.KeyboardModifier.NoModifier,
            ),
        )
