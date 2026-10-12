import traceback
from pathlib import Path
from typing import Annotated, Any

from pydantic import BaseModel, ValidationError
from zeromcp import McpServer, McpToolError

from libresvip.core.warning_types import CatchWarnings
from libresvip.extension.base import Middleware, ReadOnlyConverterMixin, WriteOnlyConverterMixin
from libresvip.extension.manager import (
    get_svs_plugin_by_suffix,
    middleware_manager,
    plugin_manager,
)
from libresvip.model.base import Project

from .session import ProjectSession, ProjectSummary, summarize

INSTRUCTIONS = (
    "Load a singing-synthesis project into a session handle, inspect a short summary, "
    "run one middleware at a time on that handle, then save it to another format. "
    "Never paste project contents into the conversation: pass local file paths and handles."
)

session = ProjectSession()
mcp = McpServer("libresvip", instructions=INSTRUCTIONS)


def _warnings(caught: CatchWarnings) -> list[str]:
    return [line for line in caught.output.splitlines() if line]


def _fail(message: str) -> None:
    raise McpToolError(message)


def _require(handle: str) -> Project:
    project = session.get(handle)
    if project is None:
        message = f"Unknown project handle: {handle}"
        _fail(message)
    return project


def _plugin(suffix: str, *, writing: bool) -> Any:
    plugin = get_svs_plugin_by_suffix(suffix.lstrip(".").lower())
    if plugin is None:
        message = f"Unsupported format: {suffix}"
        _fail(message)
    if writing and issubclass(plugin, ReadOnlyConverterMixin):
        message = f"{suffix} cannot be written"
        _fail(message)
    if not writing and issubclass(plugin, WriteOnlyConverterMixin):
        message = f"{suffix} cannot be read"
        _fail(message)
    return plugin


def _options(option_cls: type[BaseModel], raw: str | None) -> dict[str, Any]:
    if not raw:
        return {}
    try:
        return option_cls.model_validate_json(raw).model_dump()
    except ValidationError as exc:
        raise McpToolError(exc.json()) from exc


@mcp.tool(read_only=True, destructive=False, idempotent=True, open_world=False)
def list_formats() -> dict[str, list[dict[str, str | list[str]]]]:
    """List readable and writable singing-synthesis formats."""
    readable = []
    writable = []
    for identifier, plugin in plugin_manager.plugins.get("svs", {}).items():
        if plugin.info is None:
            continue
        entry = {
            "id": identifier,
            "name": plugin.info.name,
            "suffixes": list(plugin.info.suffixes),
        }
        if not issubclass(plugin, WriteOnlyConverterMixin):
            readable.append(entry)
        if not issubclass(plugin, ReadOnlyConverterMixin):
            writable.append(entry)
    return {"readable": readable, "writable": writable}


@mcp.tool(destructive=False, idempotent=False, open_world=False)
def load_project(
    path: Annotated[str, "Local path of the project file to load"],
    options: Annotated[str | None, "JSON object of the format plugin's input options"] = None,
) -> ProjectSummary:
    """Load a project file and return a session handle plus a short summary."""
    file_path = Path(path)
    if not file_path.is_file():
        message = f"File not found: {path}"
        _fail(message)
    plugin = _plugin(file_path.suffix, writing=False)
    try:
        with CatchWarnings() as caught:
            project = plugin.load(file_path, _options(plugin.input_option_cls, options))
    except McpToolError:
        raise
    except Exception as exc:
        raise McpToolError(traceback.format_exc()) from exc
    return summarize(session.put(project), project, _warnings(caught))


@mcp.tool(read_only=True, destructive=False, idempotent=True, open_world=False)
def project_summary(
    handle: Annotated[str, "Session handle returned by load_project"],
) -> ProjectSummary:
    """Return the current summary of a loaded project."""
    return summarize(handle, _require(handle))


@mcp.tool(destructive=True, idempotent=False, open_world=False)
def save_project(
    handle: Annotated[str, "Session handle returned by load_project"],
    path: Annotated[str, "Local path to write. Its suffix selects the output format"],
    options: Annotated[str | None, "JSON object of the format plugin's output options"] = None,
) -> str:
    """Write a loaded project to a local file. Returns the written path."""
    file_path = Path(path)
    plugin = _plugin(file_path.suffix, writing=True)
    try:
        with CatchWarnings():
            plugin.dump(file_path, _require(handle), _options(plugin.output_option_cls, options))
    except McpToolError:
        raise
    except Exception as exc:
        raise McpToolError(traceback.format_exc()) from exc
    return str(file_path)


@mcp.tool(destructive=False, idempotent=True, open_world=False)
def close_project(handle: Annotated[str, "Session handle to drop"]) -> bool:
    """Drop a loaded project from the session."""
    if not session.drop(handle):
        message = f"Unknown project handle: {handle}"
        _fail(message)
    return True


def _register_middlewares() -> None:
    for identifier, middleware in middleware_manager.plugins.get("middleware", {}).items():
        info = middleware.info
        description = (
            f"{info.name}. {info.description}".strip()
            if info is not None
            else f"Apply the {identifier} middleware."
        )

        def apply(
            handle: Annotated[str, "Session handle returned by load_project"],
            options: Annotated[
                str | None, "JSON object of this middleware's process options"
            ] = None,
            *,
            middleware: Middleware = middleware,
        ) -> ProjectSummary:
            project = _require(handle)
            try:
                with CatchWarnings() as caught:
                    project = middleware.process(
                        project, _options(middleware.process_option_cls, options)
                    )
            except McpToolError:
                raise
            except Exception as exc:
                raise McpToolError(traceback.format_exc()) from exc
            session.replace(handle, project)
            return summarize(handle, project, _warnings(caught))

        apply.__name__ = f"apply_{identifier}"
        apply.__doc__ = description
        mcp.tool(destructive=True, idempotent=False, open_world=False)(apply)


_register_middlewares()
