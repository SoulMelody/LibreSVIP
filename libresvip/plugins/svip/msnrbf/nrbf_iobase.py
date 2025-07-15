# Ported from QNrbf by SineStriker
from collections import ChainMap
from collections.abc import MutableMapping
from functools import cached_property
from types import TracebackType

from construct import Container
from typing_extensions import Self

from .binary_models import local_store


class NrbfIOBase:
    @cached_property
    def ref_map(self) -> MutableMapping[int, MutableMapping[int, Container]]:
        return ChainMap(
            local_store.classes,
            local_store.objects,
        )

    def __enter__(self) -> Self:
        local_store.classes = {}
        local_store.libraries = {}
        local_store.objects = {}
        local_store.references = {}
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        local_store.classes.clear()
        local_store.libraries.clear()
        local_store.objects.clear()
        local_store.references.clear()
