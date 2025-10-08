# Ported from QNrbf by SineStriker
import dataclasses
import pathlib
from typing import Annotated, Any

from construct import Container
from loguru import logger

from libresvip.utils.translation import gettext_lazy as _

from .binary_models import (
    PrimitiveTypeEnum,
    RecordTypeEnum,
    SerializedStreamHeader,
    SVIPFile,
    local_store,
)
from .nrbf_iobase import NrbfIOBase
from .xstudio_models import XSAppModel, fullname2classes


@dataclasses.dataclass
class SvipReader(NrbfIOBase):
    svip_file: Annotated[Container, SVIPFile] = dataclasses.field(init=False)
    xstudio_model: XSAppModel = dataclasses.field(init=False)
    header: Annotated[Container, SerializedStreamHeader] = dataclasses.field(init=False)

    def build_binary_array(self, obj: Container) -> list[Any | None]:
        results: list[Any | None] = []
        if "Class" in str(obj.binary_type_enum):
            if obj.member_values is not None:
                for member in obj.member_values:
                    if member is None or member.real_obj is None or member.real_obj.obj is None:
                        results.append(None)
                    else:
                        obj = member.real_obj.obj
                        if "real_obj" in obj:
                            results.append(self.build_object(obj["real_obj"]))
                        else:
                            results.append(self.build_object(obj))
            else:
                results = [None] * obj.lengths[0]
        else:
            logger.warning(obj.binary_type_enum)
        return results

    def build_class(self, obj: Container) -> Any:
        full_name = obj.class_info.name
        class_name = full_name.split("`1", 1)[0]
        model_class = fullname2classes[class_name]
        alias2key = {
            f.metadata["alias"]: f.name
            for f in dataclasses.fields(model_class)
            if "alias" in f.metadata
        }
        class_kwargs = {}
        for name, value in zip(obj.class_info.member_names, obj.member_values):
            key = alias2key.get(name, name)
            if isinstance(value.value, dict):
                if "real_obj" in value.value:
                    class_kwargs[key] = self.build_object(value.value["real_obj"])
                else:
                    class_kwargs[key] = self.build_object(value.value)
            else:
                class_kwargs[key] = value.value
        if class_name == "System.Collections.Generic.List":
            assert isinstance(class_kwargs["items"], list)
            class_kwargs["items"] = class_kwargs["items"][: class_kwargs["size"]]
        return model_class(**class_kwargs)  # type: ignore[arg-type]

    def build_object(self, obj: Container) -> Any | None:
        if "obj" in obj:
            obj = obj.obj
        if "real_obj" in obj:
            return self.build_object(obj["real_obj"])
        if "Class" in str(obj.record_type_enum):
            return self.build_class(obj)
        elif obj.record_type_enum == RecordTypeEnum.BinaryArray:
            return self.build_binary_array(obj)
        elif obj.record_type_enum == RecordTypeEnum.ArraySinglePrimitive:
            if obj.primitive_type_enum == PrimitiveTypeEnum.Byte:
                return list(obj.member_values)
        elif obj.record_type_enum == RecordTypeEnum.BinaryObjectString:
            return obj.value
        elif "ObjectNullMultiple" in str(obj.record_type_enum):
            return [None] * obj.null_count
        elif obj.record_type_enum not in [
            RecordTypeEnum.ObjectNull,
            RecordTypeEnum.MessageEnd,
        ]:
            logger.warning(obj.record_type_enum)

    def read_record(self, record: Container) -> bool:
        if record.record_type_enum == RecordTypeEnum.SerializedStreamHeader:
            self.header = record.obj
        elif (
            ("Class" in str(record.record_type_enum))
            and (record.obj.class_info.object_id == self.header.root_id)
            and (xstudio_model := self.build_object(record.obj)) is not None
            and isinstance(xstudio_model, XSAppModel)
        ):
            self.xstudio_model = xstudio_model
            return True
        return False

    def resolve_references(self) -> None:
        for ref_id in local_store.references:
            ref = local_store.references[ref_id]
            ref["real_obj"] = self.ref_map[ref["id_ref"]]

    def read(self, path: pathlib.Path) -> tuple[str, XSAppModel]:
        self.svip_file = SVIPFile.parse(path.read_bytes())
        self.resolve_references()

        for record in self.svip_file.record_stream:
            root_found = self.read_record(record)
            if root_found:
                break
        else:
            raise ValueError(_("Root not found"))

        return (
            f"{self.svip_file.magic}{self.svip_file.version}",
            self.xstudio_model,
        )
