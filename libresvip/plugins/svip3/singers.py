import dataclasses
import pathlib

try:
    import ujson as json
except ImportError:
    import json


@dataclasses.dataclass
class XStudio3Singers:
    singers: dict = dataclasses.field(init=False)

    def __post_init__(self):
        plugin_path = pathlib.Path(__file__).parent
        self.singers = json.loads(
            (plugin_path / "singers.json").read_text(encoding="utf-8")
        )

    def get_name(self, uuid: str) -> str:
        return self.singers[uuid] if uuid in self.singers else ""

    def get_uuid(self, name: str) -> str:
        try:
            return next(uuid for uuid, singer in self.singers.items() if singer == name)
        except StopIteration:
            return next(iter(self.singers.keys()), "")


xstudio3_singers = XStudio3Singers()
