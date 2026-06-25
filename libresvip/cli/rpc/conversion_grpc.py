from __future__ import annotations

from typing import TYPE_CHECKING, Any

import grpclib.client
import grpclib.const
import grpclib.server

if TYPE_CHECKING:
    from grpclib.metadata import Deadline

from .libresvip_pb import (
    ConversionRequest,
    ConversionResponse,
    PluginInfosRequest,
    PluginInfosResponse,
)


class ConversionStub:
    def __init__(self, channel: grpclib.client.Channel) -> None:
        self._channel = channel

    async def _unary_unary(
        self,
        method_name: str,
        request_message: Any,
        request_type: type[Any],
        reply_type: type[Any],
        *,
        timeout: float | None = None,
        deadline: Deadline | None = None,
        metadata: Any | None = None,
    ) -> Any:
        request_factory = getattr(self._channel, "request", None)
        if request_factory is None:
            request_factory = getattr(self._channel, "unary_unary")
            async with request_factory(
                method_name,
                request_type,
                reply_type,
                timeout=timeout,
                deadline=deadline,
                metadata=metadata,
            ) as stream:
                await stream.send_message(request_message, end=True)
                return await stream.recv_message()
        async with request_factory(
            method_name,
            grpclib.const.Cardinality.UNARY_UNARY,
            request_type,
            reply_type,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        ) as stream:
            await stream.send_message(request_message, end=True)
            return await stream.recv_message()

    async def plugin_infos(
        self,
        plugin_infos_request: PluginInfosRequest,
        *,
        timeout: float | None = None,
        deadline: Deadline | None = None,
        metadata: Any | None = None,
    ) -> PluginInfosResponse:
        return await self._unary_unary(
            "/LibreSVIP.Conversion/PluginInfos",
            plugin_infos_request,
            PluginInfosRequest,
            PluginInfosResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def convert(
        self,
        conversion_request: ConversionRequest,
        *,
        timeout: float | None = None,
        deadline: Deadline | None = None,
        metadata: Any | None = None,
    ) -> ConversionResponse:
        return await self._unary_unary(
            "/LibreSVIP.Conversion/Convert",
            conversion_request,
            ConversionRequest,
            ConversionResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )


class ConversionBase:
    async def plugin_infos(self, plugin_infos_request: PluginInfosRequest) -> PluginInfosResponse:
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def convert(self, conversion_request: ConversionRequest) -> ConversionResponse:
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def __rpc_plugin_infos(
        self, stream: grpclib.server.Stream[PluginInfosRequest, PluginInfosResponse]
    ) -> None:
        request = await stream.recv_message()
        response = await self.plugin_infos(request)
        await stream.send_message(response)

    async def __rpc_convert(
        self, stream: grpclib.server.Stream[ConversionRequest, ConversionResponse]
    ) -> None:
        request = await stream.recv_message()
        response = await self.convert(request)
        await stream.send_message(response)

    def __mapping__(self) -> dict[str, grpclib.const.Handler]:
        return {
            "/LibreSVIP.Conversion/PluginInfos": grpclib.const.Handler(
                self.__rpc_plugin_infos,
                grpclib.const.Cardinality.UNARY_UNARY,
                PluginInfosRequest,
                PluginInfosResponse,
            ),
            "/LibreSVIP.Conversion/Convert": grpclib.const.Handler(
                self.__rpc_convert,
                grpclib.const.Cardinality.UNARY_UNARY,
                ConversionRequest,
                ConversionResponse,
            ),
        }
