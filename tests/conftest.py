import os
import sys

import pytest

sys.path.append(os.path.dirname(os.path.curdir))


@pytest.fixture()
def pinyin_example():
    return ["山东菏泽", "曹县，", "牛pi", "666我滴", "宝贝儿！", "行-走-", "行-业-", "-"]


@pytest.fixture()
def pretty_construct():
    from enum import IntEnum

    from construct import Container, EnumIntegerString, ListContainer

    def int_enum_repr(self: IntEnum) -> str:
        return repr(self.value)

    IntEnum.__repr__ = int_enum_repr

    def contruct_enum_repr(self: EnumIntegerString) -> str:
        return str.__repr__(self)

    EnumIntegerString.__repr__ = contruct_enum_repr

    _container_repr = Container.__repr__
    def container_repr(self: Container) -> str:
        return _container_repr(self)[10:-1]

    Container.__repr__ = container_repr

    _list_container_repr = ListContainer.__repr__
    def list_container_repr(self: ListContainer) -> str:
        return _list_container_repr(self)[14:-1]

    ListContainer.__repr__ = list_container_repr
