import dataclasses
import enum
import importlib.resources
import re
from typing import Optional

from libresvip.model.base import json_loads

from .msnrbf.xstudio_models import (
    XSNoteHeadTag,
    XSNoteHeadTagEnum,
    XSReverbPreset,
    XSReverbPresetEnum,
)


@dataclasses.dataclass
class OpenSvipSingers:
    singers: dict[str, str] = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        with importlib.resources.path(
            "libresvip.plugins.svip", "singers.json"
        ) as singers_data_path:
            self.singers = json_loads(singers_data_path.read_text(encoding="utf-8"))

    def get_name(self, id_: str) -> str:
        if id_ in self.singers:
            return self.singers[id_]
        return f"$({id_})" if re.match(r"[FM]\d+", id_) is not None else ""

    def get_id(self, name: str) -> str:
        for id_ in self.singers:
            if self.singers[id_] == name:
                return id_
        return name[2:-1] if re.match(r"\$\([FM]\d+\)", name) is not None else ""


opensvip_singers = OpenSvipSingers()


class OpenSvipReverbPresets(enum.Enum):
    干声 = XSReverbPresetEnum.NONE
    浮光 = XSReverbPresetEnum.DEFAULT
    午后 = XSReverbPresetEnum.SMALLHALL1
    月光 = XSReverbPresetEnum.MEDIUMHALL1
    水晶 = XSReverbPresetEnum.LARGEHALL1
    汽水 = XSReverbPresetEnum.SMALLROOM1
    夜莺 = XSReverbPresetEnum.MEDIUMROOM1
    大梦 = XSReverbPresetEnum.LONGREVERB2

    @classmethod
    def get_name(cls, index: int) -> Optional[str]:
        if isinstance(index, XSReverbPreset):
            index = index.value
        return next(
            (name for name in cls._member_names_ if cls[name].value == index),
            None,
        )

    @classmethod
    def get_index(cls, name: str) -> XSReverbPreset:
        if name in cls._member_names_:
            value = cls[name].value
        else:
            value = XSReverbPresetEnum.NONE
        return XSReverbPreset(value=value)


class OpenSvipNoteHeadTags:
    tags = [None, "0", "V"]

    @classmethod
    def get_name(cls, index: int) -> Optional[str]:
        return cls.tags[index] if index in cls.tags else None

    @classmethod
    def get_index(cls, name: str) -> XSNoteHeadTag:
        value = next(
            (XSNoteHeadTagEnum(i) for i, tag in enumerate(cls.tags) if tag == name),
            XSNoteHeadTagEnum.NoTag,
        )
        return XSNoteHeadTag(value)
