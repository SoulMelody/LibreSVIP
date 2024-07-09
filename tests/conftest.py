import pytest


@pytest.fixture()
def pinyin_example() -> list[str]:
    return ["山东菏泽", "曹县，", "牛pi", "666我滴", "宝贝儿！", "行-走-", "行-业-", "-"]


@pytest.fixture()
def _pretty_construct() -> None:
    from enum import IntEnum

    from construct import Container, EnumIntegerString, ListContainer

    def int_enum_repr(self: object) -> str:
        return repr(self.value)

    setattr(IntEnum, "__repr__", int_enum_repr)

    def contruct_enum_repr(self: EnumIntegerString) -> str:
        return str.__repr__(self)

    EnumIntegerString.__repr__ = contruct_enum_repr

    def container_repr(self: Container) -> str:
        parts = [
            f"{k!r}: {v!r}"
            for k, v in self.items()
            if not (isinstance(k, str) and k.startswith("_"))
        ]
        return "{" + ", ".join(parts) + "}"

    Container.__repr__ = container_repr

    _list_container_repr = ListContainer.__repr__

    def list_container_repr(self: ListContainer) -> str:
        return _list_container_repr(self)[14:-1]

    ListContainer.__repr__ = list_container_repr

    return
