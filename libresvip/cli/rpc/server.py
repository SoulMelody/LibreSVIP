import asyncio
import sys
from concurrent.futures import ThreadPoolExecutor
from typing import override

from grpclib.server import Server
from grpclib.utils import graceful_exit
from loguru import logger
from pydantic import BaseModel
from pydantic._internal._core_utils import CoreSchemaOrField
from pydantic.json_schema import GenerateJsonSchema, JsonSchemaValue

from libresvip.core.compat import json
from libresvip.extension.base import ReadOnlyConverterMixin, WriteOnlyConverterMixin
from libresvip.extension.manager import get_translation, middleware_manager, plugin_manager
from libresvip.utils.translation import gettext_lazy as _
from libresvip.utils.translation import lazy_translation

from .conversion_grpc import ConversionBase
from .messages import PluginCategory, PluginInfo, PluginInfosRequest, PluginInfosResponse


class GettextGenerateJsonSchema(GenerateJsonSchema):
    @override
    def generate_inner(self, schema: CoreSchemaOrField) -> JsonSchemaValue:
        json_schema = super().generate_inner(schema)
        if "title" in json_schema:
            json_schema["title"] = _(json_schema["title"])
        if "description" in json_schema:
            json_schema["description"] = _(json_schema["description"])
        return json_schema


def model_json_schema(option_cls: BaseModel) -> JsonSchemaValue:
    json_schema = option_cls.model_json_schema(schema_generator=GettextGenerateJsonSchema)
    json_schema.pop("title", None)
    return json_schema


class Conversion(ConversionBase):
    def __init__(self, executor: ThreadPoolExecutor) -> None:
        self._executor = executor
        self._loop = asyncio.get_event_loop()

    async def plugin_infos(self, plugin_infos_request: PluginInfosRequest) -> PluginInfosResponse:
        lazy_translation.set(get_translation(plugin_infos_request.language))
        plugin_infos: list[PluginInfo] = []
        match plugin_infos_request.category:
            case PluginCategory.MIDDLEWARE:
                plugins = middleware_manager.plugins.get("middleware", {})
                plugin_infos.extend(
                    PluginInfo(
                        identifier=identifier,
                        name=plugin.info.name,
                        author=_(plugin.info.author),
                        description=_(plugin.info.description),
                        website=plugin.info.website,
                        version=plugin.version,
                        json_schema=json.dumps(model_json_schema(plugin.process_option_cls)),
                    )
                    for identifier, plugin in plugins.items()
                )
            case PluginCategory.OUTPUT:
                plugins = {
                    identifier: plugin
                    for identifier, plugin in plugin_manager.plugins.get("svs", {}).items()
                    if not issubclass(plugin, ReadOnlyConverterMixin)
                }
                plugin_infos.extend(
                    PluginInfo(
                        identifier=identifier,
                        name=plugin.info.name,
                        author=_(plugin.info.author),
                        description=_(plugin.info.description),
                        website=_(plugin.info.website),
                        version=plugin.version,
                        file_format=_(plugin.info.file_format),
                        suffixes=[plugin.info.suffix],
                        icon_base64=plugin.info.icon_base64 or "",
                        json_schema=json.dumps(model_json_schema(plugin.output_option_cls)),
                    )
                    for identifier, plugin in plugins.items()
                )
            case _:
                plugins = {
                    identifier: plugin
                    for identifier, plugin in plugin_manager.plugins.get("svs", {}).items()
                    if not issubclass(plugin, WriteOnlyConverterMixin)
                }
                plugin_infos.extend(
                    PluginInfo(
                        identifier=identifier,
                        name=plugin.info.name,
                        author=_(plugin.info.author),
                        description=_(plugin.info.description),
                        website=plugin.info.website,
                        version=plugin.version,
                        file_format=_(plugin.info.file_format),
                        suffixes=[plugin.info.suffix],
                        icon_base64=plugin.info.icon_base64 or "",
                        json_schema=json.dumps(model_json_schema(plugin.input_option_cls)),
                    )
                    for identifier, plugin in plugins.items()
                )
        return PluginInfosResponse(plugin_infos)


async def main(*, host: str = "127.0.0.1", port: int = 50051) -> None:
    with ThreadPoolExecutor(max_workers=4) as executor:
        server = Server([Conversion(executor)])
        with graceful_exit([server]):
            await server.start(host, port)
            logger.info(f"Serving on {host}:{port}")
            await server.wait_closed()


if __name__ == "__main__":
    run_kwargs = {}
    if sys.platform == "win32":
        import winloop

        run_kwargs["loop_factory"] = winloop.new_event_loop
    asyncio.run(main(), **run_kwargs)
