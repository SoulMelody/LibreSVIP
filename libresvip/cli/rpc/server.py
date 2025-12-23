import asyncio
import traceback

import rich
from grpclib.server import Server
from grpclib.utils import graceful_exit
from pydantic import BaseModel, ValidationError
from pydantic._internal._core_utils import CoreSchemaOrField
from pydantic.json_schema import GenerateJsonSchema, JsonSchemaValue
from typing_extensions import override
from upath import UPath

from libresvip.core.compat import json
from libresvip.core.warning_types import CatchWarnings
from libresvip.extension.base import (
    OptionsDict,
    ReadOnlyConverterMixin,
    SVSConverter,
    WriteOnlyConverterMixin,
)
from libresvip.extension.manager import get_translation, middleware_manager, plugin_manager
from libresvip.model.base import Project
from libresvip.utils.translation import gettext_lazy as _
from libresvip.utils.translation import lazy_translation

from .conversion_grpc import ConversionBase
from .messages import (
    ConversionGroup,
    ConversionMode,
    ConversionRequest,
    ConversionResponse,
    PluginCategory,
    PluginInfo,
    PluginInfosRequest,
    PluginInfosResponse,
    SingleConversionResult,
)


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


def convert_one_group(
    fs: UPath,
    mode: ConversionMode,
    max_track_count: int,
    group: ConversionGroup,
    input_plugin: SVSConverter,
    output_plugin: SVSConverter,
    input_options: OptionsDict,
    output_options: OptionsDict,
    middleware_options: dict[str, str],
) -> tuple[str, SingleConversionResult]:
    result = SingleConversionResult()
    group_path = fs / group.group_id
    group_path.mkdir()
    project = None
    if mode == ConversionMode.MERGE:
        child_projects = []
        for i, content in enumerate(group.file_contents):
            child_path = group_path / str(i)
            child_path.write_bytes(content)
            try:
                with CatchWarnings() as w:
                    child_projects.append(input_plugin.load(child_path, input_options))
                if w.output:
                    result.warning_messages.append(w.output)
            except Exception:
                result.success = False
                result.error_message = traceback.format_exc()
                project = None
                break
        else:
            project = Project.merge_projects(child_projects)
    else:
        child_path = group_path / "0"
        child_path.write_bytes(group.file_contents[0])
        try:
            with CatchWarnings() as w:
                project = input_plugin.load(child_path, input_options)
            if w.output:
                result.warning_messages.append(w.output)
        except Exception:
            result.success = False
            result.error_message = traceback.format_exc()
    group_path.rmdir()
    if project is not None:
        middlewares = middleware_manager.plugins.get("middleware", {})
        for middleware_id, middleware_option_str in middleware_options.items():
            if middleware := middlewares.get(middleware_id):
                try:
                    process_options = middleware.process_option_cls.model_validate_json(
                        middleware_option_str
                    )
                except ValidationError:
                    process_options = middleware.process_option_cls()
                try:
                    with CatchWarnings() as w:
                        project = middleware.process(project, process_options.model_dump())
                    if w.output:
                        result.warning_messages.append(w.output)
                except Exception:
                    result.success = False
                    result.error_message = traceback.format_exc()
                    project = None
                    break
    if project is not None:
        group_path.mkdir()
        if mode == ConversionMode.SPLIT:
            for i, sub_proj in enumerate(project.split_tracks(max_track_count)):
                child_path = group_path / str(i)
                try:
                    with CatchWarnings() as w:
                        output_plugin.dump(child_path, sub_proj, output_options)
                    if w.output:
                        result.warning_messages.append(w.output)
                    result.file_contents.append(child_path.read_bytes())
                except Exception:
                    result.success = False
                    result.error_message = traceback.format_exc()
                    break
            else:
                result.success = True
        else:
            child_path = group_path / "0"
            try:
                output_plugin.dump(child_path, project, output_options)
                result.file_contents.append(child_path.read_bytes())
                result.success = True
            except Exception:
                result.success = False
                result.error_message = traceback.format_exc()
        group_path.rmdir()
    return group.group_id, result


class Conversion(ConversionBase):
    def __init__(self) -> None:
        self._fs = UPath("memory://")

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

    async def convert(self, conversion_request: ConversionRequest) -> ConversionResponse:
        group_id2results = {}
        futures = []
        input_plugin = plugin_manager.plugins.get("svs", {})[conversion_request.input_format]
        output_plugin = plugin_manager.plugins.get("svs", {})[conversion_request.output_format]
        try:
            input_options = input_plugin.input_option_cls.model_validate_json(
                conversion_request.input_options
            )
        except ValidationError:
            input_options = input_plugin.input_option_cls()
        try:
            output_options = output_plugin.output_option_cls.model_validate_json(
                conversion_request.output_options
            )
        except ValidationError:
            output_options = output_plugin.output_option_cls()
        for group in conversion_request.groups:
            coro = asyncio.to_thread(
                convert_one_group,
                self._fs,
                conversion_request.mode,
                conversion_request.max_track_count,
                group,
                input_plugin,
                output_plugin,
                input_options.model_dump(),
                output_options.model_dump(),
                conversion_request.middleware_options,
            )
            futures.append(asyncio.create_task(coro))
        for future in asyncio.as_completed(futures):
            group_id, result = await future
            group_id2results[group_id] = result
        return ConversionResponse(group_id2results)


async def run_grpc_server(*, host: str = "127.0.0.1", port: int = 15150) -> None:
    server = Server([Conversion()])
    with graceful_exit([server]):
        await server.start(host, port)
        rich.print(f"Serving on {host}:{port}")
        await server.wait_closed()
