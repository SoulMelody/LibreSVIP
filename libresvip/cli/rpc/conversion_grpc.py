import aristaproto
import grpclib.server
from aristaproto.grpc.grpclib_client import MetadataLike
from aristaproto.grpc.grpclib_server import ServiceBase
from grpclib.metadata import Deadline

from .messages import ConversionRequest, ConversionResponse, PluginInfosRequest, PluginInfosResponse


class ConversionStub(aristaproto.ServiceStub):
    async def plugin_infos(
        self,
        plugin_infos_request: PluginInfosRequest,
        *,
        timeout: float | None = None,
        deadline: Deadline | None = None,
        metadata: MetadataLike | None = None,
    ) -> PluginInfosResponse:
        return await self._unary_unary(
            "/LibreSVIP.Conversion/PluginInfos",
            plugin_infos_request,
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
        metadata: MetadataLike | None = None,
    ) -> ConversionResponse:
        return await self._unary_unary(
            "/LibreSVIP.Conversion/Convert",
            conversion_request,
            ConversionResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )


class ConversionBase(ServiceBase):
    async def plugin_infos(self, plugin_infos_request: PluginInfosRequest) -> PluginInfosResponse:
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def convert(self, conversion_request: ConversionRequest) -> ConversionResponse:
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def __rpc_plugin_infos(
        self, stream: "grpclib.server.Stream[PluginInfosRequest, PluginInfosResponse]"
    ) -> None:
        request = await stream.recv_message()
        response = await self.plugin_infos(request)
        await stream.send_message(response)

    async def __rpc_convert(
        self, stream: "grpclib.server.Stream[ConversionRequest, ConversionResponse]"
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
