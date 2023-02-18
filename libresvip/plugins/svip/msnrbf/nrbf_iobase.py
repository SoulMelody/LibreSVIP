# Ported from QNrbf by SineStriker
import dataclasses
import threading
from collections import ChainMap
from functools import cached_property

from .binary_models import (
    classes_by_id,
    libraries_by_id,
    objects_by_id,
    references_by_id,
)


@dataclasses.dataclass
class NrbfIOBase:
    cur_thread_id: int = dataclasses.field(init=False)

    def __post_init__(self):
        self.cur_thread_id = threading.get_ident()

    @cached_property
    def ref_map(self):
        return ChainMap(
            classes_by_id[self.cur_thread_id],
            objects_by_id[self.cur_thread_id],
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        classes_by_id.pop(self.cur_thread_id, None)
        objects_by_id.pop(self.cur_thread_id, None)
        libraries_by_id.pop(self.cur_thread_id, None)
        references_by_id.pop(self.cur_thread_id, None)

