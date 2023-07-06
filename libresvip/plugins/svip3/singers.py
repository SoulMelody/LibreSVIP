import dataclasses
import pkgutil

from libresvip.model.base import json_loads


@dataclasses.dataclass
class XStudio3Singers:
    singers: dict = dataclasses.field(init=False)

    def __post_init__(self):
        self.singers = json_loads(
            pkgutil.get_data(__package__, "singers.json")
        )

    def get_name(self, uuid: str) -> str:
        return self.singers[uuid] if uuid in self.singers else ""

    def get_uuid(self, name: str) -> str:
        try:
            return next(uuid for uuid, singer in self.singers.items() if singer == name)
        except StopIteration:
            return next(iter(self.singers.keys()), "")


xstudio3_singers = XStudio3Singers()
