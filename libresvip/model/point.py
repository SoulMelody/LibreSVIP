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
        return iter(self.__root__)

    def __len__(self):
        return len(self.__root__)

    def __getitem__(self, index):
        return self.__root__[index]

    def __setitem__(self, index, value):
        self.__root__[index] = value

    def __delitem__(self, index):
        del self.__root__[index]

    def __contains__(self, item):
        return item in self.__root__

    def append(self, item):
        self.__root__.append(item)

    def insert(self, i, item):
        self.__root__.insert(i, item)

    def pop(self, i=-1):
        return self.__root__.pop(i)

    def remove(self, item):
        self.__root__.remove(item)

    def clear(self):
        self.__root__.clear()

    def count(self, item):
        return self.__root__.count(item)

    def index(self, item, *args):
        return self.__root__.index(item, *args)

    def reverse(self):
        self.__root__.reverse()

    def sort(self, /, *args, **kwds):
        self.__root__.sort(*args, **kwds)

    def extend(self, other):
        if isinstance(other, PointList):
            self.__root__.extend(other.__root__)
        else:
            self.__root__.extend(other)
