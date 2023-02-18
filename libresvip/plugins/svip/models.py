import dataclasses
import enum
import pathlib
import re

try:
    import ujson as json
except ImportError:
    import json

from .msnrbf.xstudio_models import (
    XSNoteHeadTag,
    XSNoteHeadTagEnum,
    XSReverbPreset,
    XSReverbPresetEnum,
)


@dataclasses.dataclass
class OpenSvipSingers:
    singers: dict = dataclasses.field(init=False)

    def __post_init__(self):
        plugin_path = pathlib.Path(__file__).parent
        self.singers = json.loads((plugin_path / 'singers.json').read_text(encoding='utf-8'))

    def get_name(self, id_: str) -> str:
        if id_ in self.singers:
            return self.singers[id_]
        if re.match(r'[FM]\d+', id_) is not None:
            return f'$({id_})'
        return ''

    def get_id(self, name: str) -> str:
        for id_ in self.singers:
            if self.singers[id_] == name:
                return id_
        if re.match(r'\$\([FM]\d+\)', name) is not None:
            return name[2:-1]
        return ''


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
    def get_name(cls, index) -> str:
        if isinstance(index, XSReverbPreset):
            index = index.value
        try:
            return next(
                name for name, member in cls.__members__.items()
                if member.value == index
            )
        except StopIteration:
            return None

    @classmethod
    def get_index(cls, name) -> XSReverbPreset:
        if name in cls.__members__:
            value = cls.__members__[name].value
        else:
            value = XSReverbPresetEnum.NONE
        return XSReverbPreset(value=value)


class OpenSvipNoteHeadTags:
    tags = [None, '0', 'V']

    @classmethod
    def get_name(cls, index) -> str:
        if index in cls.tags:
            return cls.tags[index]
        return None

    @classmethod
    def get_index(cls, name) -> XSNoteHeadTag:
        for i, tag in enumerate(cls.tags):
            if tag == name:
                value = XSNoteHeadTagEnum(i)
                break
        else:
            value = XSNoteHeadTagEnum.NoTag
        return XSNoteHeadTag(value)
