#!/usr/bin/env python3

import io
import json
import os
import shutil
import tempfile

from babel.messages.frontend import extract_messages
from translate.convert.json2po import convertjson
from translate.storage import factory
from translate.tools.pomerge import mergestore

from libresvip.extension.messages import messages_iterator

if __name__ == "__main__":
    locale_name = os.environ.get("LIBRESVIP_LOCALE", "zh_CN")

    for plugin_suffix, plugin_metadata, info_path in messages_iterator():
        with tempfile.NamedTemporaryFile(suffix=".po") as tmp_po:
            with tempfile.TemporaryDirectory() as tmp_dir:
                tmp_pot_name = tempfile.mktemp(suffix=".pot", dir=tmp_dir)
                cmdinst = extract_messages()
                cmdinst.initialize_options()
                cmdinst.input_paths = [str(info_path)]
                cmdinst.output_file = tmp_pot_name
                cmdinst.finalize_options()
                cmdinst.run()
                python_store = factory.getobject(tmp_pot_name)
                plugin_metadata["messages"] = list(python_store.getids())
            convertjson(
                json.dumps(
                    {plugin_suffix: plugin_metadata},
                ),
                tmp_po,
                None,
                duplicatestyle="merge",
            )

            tmp_po.seek(0)

            plugin_info_path = next(info_path.glob("*.yapsy-plugin"))
            i18n_file = info_path / f"{plugin_info_path.stem}-{locale_name}.po"
            if i18n_file.exists():
                if ori_content := i18n_file.read_bytes():
                    orig_po = io.BytesIO(ori_content)
                    mergestore(
                        orig_po,
                        i18n_file.open("wb"),
                        tmp_po,
                    )
                    continue
            shutil.copyfileobj(tmp_po, i18n_file.open("wb"))
