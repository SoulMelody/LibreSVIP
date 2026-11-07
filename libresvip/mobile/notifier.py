"""Flet local-notification wrapper for the mobile frontend.

Keeps three concerns in one small class: register the Flet service, ask for the
permission at most once, and never let a failed notification break a conversion.
"""

from __future__ import annotations

import itertools
from typing import TYPE_CHECKING

import flet_notifications as ftn
from loguru import logger

from libresvip.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    import flet as ft


class MobileNotifier:
    def __init__(self, page: ft.Page) -> None:
        self.page = page
        # Handlers are bound before registration so the client never needs a patch
        # for a service field set after `page.services.append(...)`.
        self.action_handler: Callable[[ftn.NotificationActionEvent], None] | None = None
        self.tap_handler: Callable[[ftn.NotificationEvent], None] | None = None
        self.service = ftn.Notifications(
            on_action=self._dispatch_action,
            on_tap=self._dispatch_tap,
        )
        # `Notifications` registers itself with the page; adding it to
        # `page.services` as well would register it twice.
        self._ids = itertools.count(1)
        self._permission_requested = False

    def _dispatch_action(self, event: ftn.NotificationActionEvent) -> None:
        if self.action_handler is not None:
            self.action_handler(event)

    def _dispatch_tap(self, event: ftn.NotificationEvent) -> None:
        if self.tap_handler is not None:
            self.tap_handler(event)

    async def _ensure_permission(self) -> bool:
        if self._permission_requested:
            return True
        self._permission_requested = True
        try:
            if await self.service.are_notifications_enabled():
                return True
            return bool(await self.service.request_permissions())
        except Exception:
            logger.exception("Unable to obtain the notification permission")
            return False

    async def notify(
        self,
        title: str,
        body: str,
        *,
        actions: Sequence[ftn.NotificationAction] = (),
        payload: str | None = None,
    ) -> None:
        if not await self._ensure_permission():
            return
        try:
            await self.service.show(
                id=next(self._ids),
                title=title,
                body=body,
                payload=payload,
                actions=list(actions) or None,
            )
        except Exception:
            logger.exception("Unable to show the notification: {}", title)

    def post(
        self,
        title: str,
        body: str,
        *,
        actions: Sequence[ftn.NotificationAction] = (),
        payload: str | None = None,
    ) -> None:
        """Thread-safe entry point for code running outside the event loop."""
        self.page.run_task(self.notify, title, body, actions=actions, payload=payload)

    def notify_conversion_finished(
        self,
        name: str,
        *,
        warnings: bool = False,
        failed: bool = False,
    ) -> None:
        if failed:
            title = _("Conversion failed")
        elif warnings:
            title = _("Conversion completed with warnings")
        else:
            title = _("Conversion completed")
        self.post(title, name)
