from __future__ import annotations

import xml.etree.ElementTree as ET

# Elements where MusicXML 4.0 allows empty content (the corresponding enum has
# an empty-string member) but the xsdata-generated `value` field is marked
# `required=True`. Inject the spec's default text so the strict pydantic models
# can parse real-world v4 files (notably MuseScore 4 output).
EMPTY_DEFAULTS: dict[str, str] = {
    "fermata": "normal",
    "caesura": "normal",
    "breath-mark": "comma",
    "note-size": "100",
}


def preprocess_for_v4(xml_bytes: bytes) -> bytes:
    root = ET.fromstring(xml_bytes)
    for elem in root.iter():
        tag = elem.tag.rsplit("}", 1)[-1]
        if tag in EMPTY_DEFAULTS and (elem.text is None or not elem.text.strip()):
            elem.text = EMPTY_DEFAULTS[tag]
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)
