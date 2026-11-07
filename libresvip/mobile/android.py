"""Thin bridge to Android platform APIs.

Every `jnius` import happens inside a function so that importing this module on
desktop and iOS cannot fail. No UI or notification logic belongs here.
"""

from __future__ import annotations

import platform
import time
from typing import TYPE_CHECKING, Any

from loguru import logger

if TYPE_CHECKING:
    from collections.abc import Callable

APK_MIME_TYPE = "application/vnd.android.package-archive"
POLL_INTERVAL = 0.5

DOWNLOAD_MANAGER_CLASS = "android.app.DownloadManager"
DOWNLOAD_REQUEST_CLASS = "android.app.DownloadManager$Request"
ACTIVITY_CLASS = "com.flet.serious_python_android.PythonActivity"


def _autoclass() -> Callable[[str], Any]:
    from jnius import autoclass

    return autoclass


def _activity() -> Any:
    return _autoclass()(ACTIVITY_CLASS).mActivity


def _download_manager() -> Any:
    manager_class = _autoclass()(DOWNLOAD_MANAGER_CLASS)
    return _activity().getSystemService(manager_class.DOWNLOAD_SERVICE)


def current_abi() -> str | None:
    """Return the primary ABI of the device, falling back to the machine name."""
    try:
        supported_abis = _autoclass()("android.os.Build").SUPPORTED_ABIS
        if supported_abis:
            return str(supported_abis[0])
    except Exception:
        logger.exception("Unable to read the supported Android ABIs")
    return platform.machine() or None


def enqueue_apk_download(url: str, filename: str) -> int:
    """Queue an APK download through the system DownloadManager and return its id."""
    autoclass = _autoclass()
    request_class = autoclass(DOWNLOAD_REQUEST_CLASS)
    uri_class = autoclass("android.net.Uri")
    environment_class = autoclass("android.os.Environment")
    request = request_class(uri_class.parse(url))
    request.setTitle(filename)
    request.setMimeType(APK_MIME_TYPE)
    request.setNotificationVisibility(request_class.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
    request.setDestinationInExternalPublicDir(environment_class.DIRECTORY_DOWNLOADS, filename)
    return int(_download_manager().enqueue(request))


def wait_for_downloaded_uri(download_id: int, timeout: float) -> str | None:
    """Poll the DownloadManager until the download finishes, or give up after `timeout`.

    Only `getUriForDownloadedFile(long)` is used: it is a single-argument call, unlike
    `Query.setFilterById(long...)`, so it does not depend on pyjnius vararg support.
    The system download notification reports failures to the user meanwhile.
    """
    manager = _download_manager()
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        uri = manager.getUriForDownloadedFile(download_id)
        if uri is not None:
            return uri.toString()
        time.sleep(POLL_INTERVAL)
    logger.warning("Timed out waiting for the APK download: {}", download_id)
    return None


def install_apk(uri: str) -> None:
    """Ask the system installer to install the APK behind `uri`."""
    autoclass = _autoclass()
    intent_class = autoclass("android.content.Intent")
    uri_class = autoclass("android.net.Uri")
    intent = intent_class(intent_class.ACTION_VIEW)
    intent.setDataAndType(uri_class.parse(uri), APK_MIME_TYPE)
    intent.addFlags(intent_class.FLAG_GRANT_READ_URI_PERMISSION)
    intent.addFlags(intent_class.FLAG_ACTIVITY_NEW_TASK)
    _activity().startActivity(intent)


def can_request_package_installs() -> bool:
    """Report whether this app may prompt the user to install packages."""
    try:
        return bool(_activity().getPackageManager().canRequestPackageInstalls())
    except Exception:
        logger.exception("Unable to query the unknown-sources install permission")
        return False


def open_install_permission_settings() -> None:
    """Open the system screen that grants the install-unknown-apps permission."""
    autoclass = _autoclass()
    intent_class = autoclass("android.content.Intent")
    settings_class = autoclass("android.provider.Settings")
    uri_class = autoclass("android.net.Uri")
    intent = intent_class(settings_class.ACTION_MANAGE_UNKNOWN_APP_SOURCES)
    intent.setData(uri_class.parse(f"package:{_activity().getPackageName()}"))
    intent.addFlags(intent_class.FLAG_ACTIVITY_NEW_TASK)
    _activity().startActivity(intent)
