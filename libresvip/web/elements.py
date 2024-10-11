import asyncio
from collections.abc import Callable
from typing import Any, Optional

from nicegui.elements.mixins.color_elements import BackgroundColorElement
from nicegui.elements.mixins.disableable_element import DisableableElement
from nicegui.elements.mixins.text_element import TextElement
from nicegui.events import ClickEventArguments, handle_event


class QFab(TextElement, DisableableElement, BackgroundColorElement):
    def __init__(
        self,
        text: str = "",
        *,
        on_click: Optional[Callable[..., Any]] = None,
        color: Optional[str] = "primary",
        icon: Optional[str] = None,
    ) -> None:
        super().__init__(tag="q-fab", text=text, background_color=color)

        if icon:
            self._props["icon"] = icon

        if on_click:
            self.on(
                "click",
                lambda _: handle_event(
                    on_click,
                    ClickEventArguments(sender=self, client=self.client),
                ),
            )

    def _text_to_model_text(self, text: str) -> None:
        self._props["label"] = text

    async def clicked(self) -> None:
        """Wait until the button is clicked."""
        event = asyncio.Event()
        self.on("click", event.set)
        await self.client.connected()
        await event.wait()


class QFabAction(TextElement, DisableableElement, BackgroundColorElement):
    def __init__(
        self,
        text: str = "",
        *,
        on_click: Optional[Callable[..., Any]] = None,
        color: Optional[str] = "primary",
        icon: Optional[str] = None,
    ) -> None:
        super().__init__(tag="q-fab-action", text=text, background_color=color)

        if icon:
            self._props["icon"] = icon

        if on_click:
            self.on(
                "click",
                lambda _: handle_event(
                    on_click,
                    ClickEventArguments(sender=self, client=self.client),
                ),
            )

    def _text_to_model_text(self, text: str) -> None:
        self._props["label"] = text

    async def clicked(self) -> None:
        """Wait until the button is clicked."""
        event = asyncio.Event()
        self.on("click", event.set)
        await self.client.connected()
        await event.wait()
