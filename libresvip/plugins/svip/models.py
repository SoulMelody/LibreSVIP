import dataclasses
import re

from bidict import bidict

from libresvip.core.compat import json, package_path

from .msnrbf.xstudio_models import (
    XSNoteHeadTagEnum,
    XSReverbPresetEnum,
)


@dataclasses.dataclass
class OpenSvipSingers:
    singers: bidict[str, str] = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        singers_data_path = package_path("libresvip.plugins.svip") / "singers.json"
        self.singers = bidict(json.loads(singers_data_path.read_text(encoding="utf-8")))

    def get_name(self, id_: str) -> str:
        if id_ in self.singers:
            return self.singers[id_]
        return f"$({id_})" if re.match(r"[FM]\d+", id_) is not None else ""

    def get_id(self, name: str) -> str:
        if name in self.singers.inverse:
            return self.singers.inverse[name]
        return name[2:-1] if re.match(r"\$\([FM]\d+\)", name) is not None else ""


opensvip_singers = OpenSvipSingers()

svip_reverb_presets = bidict(
    {
        "干声": XSReverbPresetEnum.NONE,
        "浮光": XSReverbPresetEnum.DEFAULT,
        "午后": XSReverbPresetEnum.SMALLHALL1,
        "月光": XSReverbPresetEnum.MEDIUMHALL1,
        "水晶": XSReverbPresetEnum.LARGEHALL1,
        "汽水": XSReverbPresetEnum.SMALLROOM1,
        "夜莺": XSReverbPresetEnum.MEDIUMROOM1,
        "大梦": XSReverbPresetEnum.LONGREVERB2,
    }
)


svip_note_head_tags = bidict(
    {
        None: XSNoteHeadTagEnum.NoTag,
        "0": XSNoteHeadTagEnum.SilTag,
        "V": XSNoteHeadTagEnum.SpTag,
    }
)
