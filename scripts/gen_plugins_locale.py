import json

from translate.convert.json2po import convertjson

from libresvip.core.constants import res_dir
from libresvip.extension.manager import plugin_registry

if __name__ == "__main__":
    plugin_metadatas = {}

    for plugin_info in plugin_registry.values():
        plugin_metadata = {"file_format": plugin_info.file_format}
        if plugin_info.description:
            plugin_metadata["description"] = plugin_info.description
        plugin_metadatas[plugin_info.name] = plugin_metadata

    convertjson(
        json.dumps(
            plugin_metadatas,
        ),
        (res_dir / "i18n" / "libresvip_plugins-zh_CN.po").open("wb"),
        None,
    )
