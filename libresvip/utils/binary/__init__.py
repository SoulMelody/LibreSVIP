from typing import BinaryIO

from construct import Construct, Container
from construct import Path as CSPath
from construct_typed import Context


def singleton(arg: type[Construct]) -> Construct:
    return arg()


@singleton
class Null(Construct):
    def _sizeof(self, context: Context, path: CSPath) -> int:
        return 0

    def _parse(self, stream: BinaryIO, context: Context, path: CSPath) -> None:
        return None

    def _build(self, obj: Container, stream: BinaryIO, context: Context, path: CSPath) -> None:
        pass
