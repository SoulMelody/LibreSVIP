#!/usr/bin/env python3

import io
import json
import shutil
import tempfile

from babel.messages.frontend import extract_messages
from translate.convert.json2po import convertjson
from translate.storage import factory
from translate.tools.pomerge import mergestore

from libresvip.extension.messages import messages_iterator

if __name__ == "__main__":
    for plugin_suffix, plugin_metadata, info_path in messages_iterator():
        with tempfile.NamedTemporaryFile(suffix=".po") as tmp_po:
            with tempfile.TemporaryDirectory() as tmp_dir:
                tmp_pot_name = tempfile.mktemp(suffix=".pot", dir=tmp_dir)
                cmdinst = extract_messages()
                cmdinst.initialize_options()
                cmdinst.input_paths = [str(info_path.parent)]
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

            i18n_file = info_path.parent / (info_path.stem + "-zh_CN.po")
            if i18n_file.exists():
                ori_content = i18n_file.read_bytes()
                if ori_content:
                    orig_po = io.BytesIO(ori_content)
                    mergestore(
                        orig_po,
                        i18n_file.open("wb"),
                        tmp_po,
                    )
                    continue
            shutil.copyfileobj(tmp_po, i18n_file.open("wb"))
