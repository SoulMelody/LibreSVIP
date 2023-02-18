import os
import sys

import pytest

sys.path.append(os.path.dirname(os.path.curdir))


@pytest.fixture()
def pinyin_example():
    return ["山东菏泽", "曹县，", "牛pi", "666我滴", "宝贝儿！", "行-走-", "行-业-", "-"]
