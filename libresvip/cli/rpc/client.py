import asyncio

import rich
from grpclib.client import Channel

from .conversion_grpc import ConversionStub
from .messages import PluginCategory, PluginInfosRequest


async def main() -> None:
    async with Channel("127.0.0.1", 50051) as channel:
        client = ConversionStub(channel)

        reply = await client.plugin_infos(
            PluginInfosRequest(
                category=PluginCategory.OUTPUT,
                language="zh-CN",
            )
        )
        for value in reply.values:
            rich.print(value)


if __name__ == "__main__":
    asyncio.run(main())
