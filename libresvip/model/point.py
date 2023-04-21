from typing import Generic, List, NamedTuple, TypeVar

from pydantic import Field  # , root_validator, model_serializer
from pydantic.generics import GenericModel
from typing_extensions import Self

PointType = TypeVar("PointType")


class Point(NamedTuple):
    x: int
    y: int

    @classmethod
    def start_point(cls, value: int = -100) -> Self:
        return cls(-192000, value)

    @classmethod
    def end_point(cls, value: int = -100) -> Self:
        return cls(1073741823, value)


class PointList(GenericModel, Generic[PointType]):
    __root__: List[PointType] = Field(default_factory=list)
    # First attempt for pydantic v2
    """
    @root_validator(pre=True)
    @classmethod
    def populate_root(cls, values):
        return {'root': values}

    @model_serializer(mode='wrap')
    def _serialize(self, handler, info):
        data = handler(self)
        return data['root'] if info.mode == 'json' else data

    @classmethod
    def model_modify_json_schema(cls, json_schema):
        return json_schema['properties']['root']
    """

    def __iter__(self):
        return iter(self.root)

    def __len__(self):
        return len(self.root)

    def __getitem__(self, index):
        return self.root[index]

    def __setitem__(self, index, value):
        self.root[index] = value

    def __delitem__(self, index):
        del self.root[index]

    def __contains__(self, item):
        return item in self.root

    def append(self, item):
        self.root.append(item)

    def insert(self, i, item):
        self.root.insert(i, item)

    def pop(self, i=-1):
        return self.root.pop(i)

    def remove(self, item):
        self.root.remove(item)

    def clear(self):
        self.root.clear()

    def count(self, item):
        return self.root.count(item)

    def index(self, item, *args):
        return self.root.index(item, *args)

    def reverse(self):
        self.root.reverse()

    def sort(self, /, *args, **kwds):
        self.root.sort(*args, **kwds)

    def extend(self, other):
        if isinstance(other, PointList):
            self.root.extend(other.root)
        else:
            self.root.extend(other)
