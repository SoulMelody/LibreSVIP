import dataclasses
import importlib.resources

from libresvip.model.base import json_loads


@dataclasses.dataclass
class XStudio3Singers:
    singers: dict[str, str] = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        with importlib.resources.path(__package__, "singers.json") as singer_data_path:
            self.singers = json_loads(singer_data_path.read_text(encoding="utf-8"))

    def get_name(self, uuid: str) -> str:
        return self.singers[uuid] if uuid in self.singers else ""

    def get_uuid(self, name: str) -> str:
        try:
            return next(uuid for uuid, singer in self.singers.items() if singer == name)
        except StopIteration:
            return next(iter(self.singers.keys()), "")


xstudio3_singers = XStudio3Singers()
