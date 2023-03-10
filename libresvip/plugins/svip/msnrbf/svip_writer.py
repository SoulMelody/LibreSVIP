# Ported from QNrbf by SineStriker
import dataclasses
import enum
import math
import pathlib
from collections import defaultdict
from queue import Queue
from typing import Set, get_args

from .binary_models import (
    BinaryArrayTypeEnum,
    BinaryTypeEnum,
    PrimitiveTypeEnum,
    RecordTypeEnum,
    SVIPFile,
    classes_by_id,
    libraries_by_id,
    references_by_id,
)
from .constants import (
    LIBRARY_NAME_SINGING_TOOL_LIBRARY,
    LIBRARY_NAME_SINGING_TOOL_MODEL,
)
from .nrbf_iobase import NrbfIOBase
from .xstudio_models import (
    XSAppModel,
    XSITrack,
    XSNote,
    XSSongBeat,
    XSSongTempo,
)


def class_def_factory():
    return defaultdict(lambda: 0)


@dataclasses.dataclass
class SvipWriter(NrbfIOBase):
    ids: Queue = dataclasses.field(default_factory=Queue)
    id_max: int = dataclasses.field(default=0)
    model_library_id: int = dataclasses.field(default=0)
    lib_library_id: int = dataclasses.field(default=0)
    written_ids: Set[int] = dataclasses.field(default_factory=set)
    class_defs: dict = dataclasses.field(default_factory=class_def_factory)
    svip_file: dict = dataclasses.field(init=False)

    def enq(self) -> int:
        self.id_max += 1
        self.ids.put(self.id_max)
        return self.id_max

    def deq(self) -> int:
        return self.ids.get()

    def write(self, path: pathlib.Path, version: str, model: XSAppModel) -> None:
        self.svip_file = {
            "magic": version[:4],
            "version": version[4:],
            "record_stream": [],
        }
        self.id_max += 1
        app_model_id = self.id_max
        self.header = {
            "root_id": app_model_id,
            "header_id": -1,
            "major_version": 1,
            "minor_version": 0,
        }
        self.svip_file["record_stream"].append(
            {
                "record_type_enum": RecordTypeEnum.SerializedStreamHeader,
                "obj": self.header,
            }
        )
        self.id_max += 1
        self.model_library_id = self.id_max
        model_library = {
            "library_id": self.model_library_id,
            "library_name": LIBRARY_NAME_SINGING_TOOL_MODEL,
        }
        libraries_by_id[self.cur_thread_id][
            model_library["library_id"]
        ] = model_library["library_name"]
        self.svip_file["record_stream"].append(
            {"record_type_enum": RecordTypeEnum.BinaryLibrary, "obj": model_library}
        )
        self.id_max += 1
        self.lib_library_id = self.id_max
        lib_library = {
            "library_id": self.lib_library_id,
            "library_name": LIBRARY_NAME_SINGING_TOOL_LIBRARY,
        }
        libraries_by_id[self.cur_thread_id][lib_library["library_id"]] = lib_library[
            "library_name"
        ]
        self.svip_file["record_stream"].append(
            {"record_type_enum": RecordTypeEnum.BinaryLibrary, "obj": lib_library}
        )

        self.svip_file["record_stream"].append(
            self.write_dataclass(model, app_model_id)
        )
        while not self.ids.empty():
            not_written = self.deq()
            ref = references_by_id[self.cur_thread_id][not_written]
            if dataclasses.is_dataclass(ref["real_obj"]):
                self.svip_file["record_stream"].append(
                    self.write_dataclass(
                        ref["real_obj"], not_written, ref["subcon_class_name"]
                    )
                )
            else:
                self.svip_file["record_stream"].append(ref["real_obj"])

        self.svip_file["record_stream"].append(
            {
                "record_type_enum": RecordTypeEnum.MessageEnd,
                "obj": {},
            }
        )
        SVIPFile.build_file(self.svip_file, path)

    def create_string(self, value: str):
        self.id_max += 1
        result = {
            "record_type_enum": RecordTypeEnum.BinaryObjectString,
            "obj": {
                "object_id": self.id_max,
                "value": value,
            },
        }
        return result

    def create_reference(self, value, object_id: int, subcon_class_name: str):
        result = {
            "record_type_enum": RecordTypeEnum.MemberReference,
            "obj": {
                "id_ref": object_id,
            },
        }
        if subcon_class_name is not None and "`1" in subcon_class_name:
            subcon_class_name = subcon_class_name.split("[[", 1)[-1].split(", ", 1)[0]
        if object_id not in references_by_id[self.cur_thread_id]:
            references_by_id[self.cur_thread_id][object_id] = {
                "id_ref": object_id,
                "subcon_class_name": subcon_class_name,
                "real_obj": value,
            }
        return result

    def write_null_array(self, value: int):
        if value == 1:
            return {
                "record_type_enum": RecordTypeEnum.ObjectNull,
                "obj": {},
            }
        elif value <= 256:
            return {
                "record_type_enum": RecordTypeEnum.ObjectNullMultiple256,
                "obj": {
                    "null_count": value,
                },
            }
        else:
            return {
                "record_type_enum": RecordTypeEnum.ObjectNullMultiple,
                "obj": {
                    "null_count": value,
                },
            }

    def write_binary_array(self, values: list, type_name: str, library_id: int):
        object_id = self.enq()
        padded_length = max(
            4,
            2 ** math.ceil(math.log2(len(values))) if len(values) > 0 else 0,
        )
        result = {
            "record_type_enum": RecordTypeEnum.BinaryArray,
            "obj": {
                "object_id": object_id,
                "binary_array_type_enum": BinaryArrayTypeEnum.Single,
                "rank": 1,
                "lengths": [padded_length],
                "lower_bounds": None,
                "binary_type_enum": BinaryTypeEnum.Class,
                "info": {
                    "type_name": type_name.replace("InstrumentTrack", "ITrack").replace(
                        "SingingTrack", "ITrack"
                    ),
                    "library_id": library_id,
                },
                "member_values": [
                    {
                        "total": padded_length,
                        "real_obj": self.create_reference(value, self.enq(), type_name),
                    }
                    for value in values
                ],
            },
        }
        if len(values) < padded_length:
            result["obj"]["member_values"].append(
                {
                    "total": padded_length,
                    "real_obj": self.write_null_array(padded_length - len(values)),
                }
            )
        references_by_id[self.cur_thread_id][object_id] = {
            "id_ref": object_id,
            "real_obj": result,
        }
        ref = self.create_reference(result, object_id, None)
        return ref

    def create_primitive_array(self, values):
        object_id = self.enq()
        result = {
            "record_type_enum": RecordTypeEnum.ArraySinglePrimitive,
            "obj": {
                "array_info": {
                    "object_id": object_id,
                    "length": len(values),
                },
                "primitive_type_enum": PrimitiveTypeEnum.Byte,
                "member_values": values,
            },
        }
        references_by_id[self.cur_thread_id][object_id] = {
            "id_ref": object_id,
            "real_obj": result,
        }
        ref = self.create_reference(result, object_id, None)
        return ref

    def write_dataclass(self, obj, object_id, subcon_class_name=None):
        fields = sorted(
            dataclasses.fields(obj), key=lambda field: field.metadata.get("order", 0)
        )
        class_name = obj.__class__.__doc__

        if (
            subcon_class_name is not None
            and class_name.endswith("List")
            and subcon_class_name != class_name
        ):
            class_name = f"{class_name}`1[[{subcon_class_name}, {LIBRARY_NAME_SINGING_TOOL_MODEL}]]"

        if class_name not in self.class_defs:
            result = {
                "obj": {
                    "class_info": {
                        "object_id": object_id,
                        "name": class_name,
                        "member_count": 0,
                        "member_names": [],
                    },
                    "member_type_info": {
                        "binary_type_enums": [],
                        "additional_infos": [],
                    },
                    "member_values": [],
                },
            }
            if class_name.startswith("System."):
                result[
                    "record_type_enum"
                ] = RecordTypeEnum.SystemClassWithMembersAndTypes
            else:
                if class_name.startswith("SingingTool.Model."):
                    result["obj"]["library_id"] = self.model_library_id
                elif class_name.startswith("SingingTool.Library."):
                    result["obj"]["library_id"] = self.lib_library_id
                result["record_type_enum"] = RecordTypeEnum.ClassWithMembersAndTypes
            for field in fields:
                if field.metadata.get("alias"):
                    field_args = get_args(field.type)
                    if len(field_args) == 2 and issubclass(field_args[-1], type(None)):
                        field_type = field_args[0]
                    else:
                        field_type = field.type
                    if (
                        field.name == "edited_power_line"
                        and self.svip_file["version"] != "7.0.0"
                    ):
                        continue
                    if issubclass(field_type, str):
                        result["obj"]["member_type_info"]["binary_type_enums"].append(
                            BinaryTypeEnum.String
                        )
                        result["obj"]["member_type_info"]["additional_infos"].append(
                            {"info": None}
                        )
                    elif issubclass(field_type, (int, float, bool, enum.IntEnum)):
                        result["obj"]["member_type_info"]["binary_type_enums"].append(
                            BinaryTypeEnum.Primitive
                        )
                        if issubclass(field_type, bool):
                            primitive_type_enum = PrimitiveTypeEnum.Boolean
                        elif issubclass(field_type, float):
                            if field.name in ("pan", "sample_rate", "volume"):
                                primitive_type_enum = PrimitiveTypeEnum.Double
                            else:
                                primitive_type_enum = PrimitiveTypeEnum.Single
                        else:
                            primitive_type_enum = PrimitiveTypeEnum.Int32
                        result["obj"]["member_type_info"]["additional_infos"].append(
                            {"info": primitive_type_enum}
                        )
                    elif issubclass(field_type, list):
                        values = getattr(obj, field.name)
                        if len(values) > 0:
                            subcon_class_name = values[0].__class__.__doc__

                        result["obj"]["member_type_info"]["binary_type_enums"].append(
                            BinaryTypeEnum.Class
                        )
                        result["obj"]["member_type_info"]["additional_infos"].append(
                            {
                                "info": {
                                    "type_name": subcon_class_name.replace(
                                        "InstrumentTrack", "ITrack"
                                    ).replace("SingingTrack", "ITrack")
                                    + "[]",
                                    "library_id": self.model_library_id,
                                }
                            }
                        )
                    elif issubclass(field_type, bytes):
                        result["obj"]["member_type_info"]["binary_type_enums"].append(
                            BinaryTypeEnum.PrimitiveArray
                        )
                        result["obj"]["member_type_info"]["additional_infos"].append(
                            {"info": PrimitiveTypeEnum.Byte}
                        )
                    elif dataclasses.is_dataclass(field_type):
                        sub_class_name = field_type.__doc__
                        if field.name == "tempo_list":
                            subcon_class_name = XSSongTempo.__doc__
                        elif field.name == "beat_list":
                            subcon_class_name = XSSongBeat.__doc__
                        elif field.name == "note_list":
                            subcon_class_name = XSNote.__doc__
                        elif field.name == "track_list":
                            subcon_class_name = XSITrack.__doc__

                        if sub_class_name.endswith("List"):
                            sub_class_name = f"{sub_class_name}`1[[{subcon_class_name}, {LIBRARY_NAME_SINGING_TOOL_MODEL}]]"

                        if sub_class_name.startswith("System."):
                            result["obj"]["member_type_info"][
                                "binary_type_enums"
                            ].append(BinaryTypeEnum.SystemClass)
                            result["obj"]["member_type_info"][
                                "additional_infos"
                            ].append(
                                {
                                    "info": sub_class_name,
                                }
                            )
                        else:
                            result["obj"]["member_type_info"][
                                "binary_type_enums"
                            ].append(BinaryTypeEnum.Class)
                            result["obj"]["member_type_info"][
                                "additional_infos"
                            ].append(
                                {
                                    "info": {
                                        "type_name": sub_class_name,
                                        "library_id": self.model_library_id
                                        if sub_class_name.startswith(
                                            "SingingTool.Model."
                                        )
                                        else self.lib_library_id,
                                    },
                                }
                            )
                    else:
                        raise Exception(f"Unknown type {field_type}")
                    value = getattr(obj, field.name)
                    if value is None:
                        result["obj"]["member_values"].append(
                            {
                                "value": {
                                    "record_type_enum": RecordTypeEnum.ObjectNull,
                                    "obj": {},
                                }
                            }
                        )
                    else:
                        if issubclass(field_type, str):
                            result["obj"]["member_values"].append(
                                {"value": self.create_string(value or "")}
                            )
                        elif issubclass(field_type, (int, float, bool, enum.IntEnum)):
                            result["obj"]["member_values"].append({"value": value})
                        elif issubclass(field_type, list):
                            if len(value) > 0:
                                subcon_class_name = value[0].__class__.__doc__
                            result["obj"]["member_values"].append(
                                {
                                    "value": self.write_binary_array(
                                        value, subcon_class_name, self.model_library_id
                                    )
                                }
                            )
                        elif issubclass(field_type, bytes):
                            result["obj"]["member_values"].append(
                                {
                                    "value": self.create_primitive_array(
                                        getattr(obj, field.name)
                                    )
                                }
                            )
                        elif dataclasses.is_dataclass(field_type):
                            sub_class_name = field_type.__doc__
                            if field.name == "tempo_list":
                                subcon_class_name = XSSongTempo.__doc__
                            elif field.name == "beat_list":
                                subcon_class_name = XSSongBeat.__doc__
                            elif field.name == "note_list":
                                subcon_class_name = XSNote.__doc__
                            elif field.name == "track_list":
                                subcon_class_name = XSITrack.__doc__

                            if sub_class_name.endswith("List"):
                                sub_class_name = f"{sub_class_name}`1[[{subcon_class_name}, {LIBRARY_NAME_SINGING_TOOL_MODEL}]]"
                            if field.name == "buf_1":
                                obj_id = self.id_max
                            elif hasattr(field_type, "value"):
                                self.id_max += 1
                                obj_id = self.id_max
                            else:
                                obj_id = self.enq()
                            if hasattr(field_type, "value"):
                                result["obj"]["member_values"].append(
                                    {
                                        "value": self.write_dataclass(
                                            value, -obj_id, sub_class_name
                                        )
                                    }
                                )
                            elif field.name.endswith("_line") and not len(
                                value.line_param
                            ):
                                result["obj"]["member_values"].append(
                                    {
                                        "value": {
                                            "record_type_enum": RecordTypeEnum.ObjectNull,
                                            "obj": {},
                                        }
                                    }
                                )
                            else:
                                result["obj"]["member_values"].append(
                                    {
                                        "value": self.create_reference(
                                            value, obj_id, sub_class_name
                                        )
                                    }
                                )
                        else:
                            raise Exception(f"Unknown type {field_type}")
                    result["obj"]["class_info"]["member_names"].append(
                        field.metadata["alias"]
                    )
                    result["obj"]["class_info"]["member_count"] += 1
            self.class_defs[class_name] = result
            classes_by_id[self.cur_thread_id][object_id] = result["obj"]
        else:
            result = {
                "record_type_enum": RecordTypeEnum.ClassWithId,
                "obj": {
                    "object_id": object_id,
                    "metadata_id": self.class_defs[class_name]["obj"]["class_info"][
                        "object_id"
                    ],
                    "member_values": [],
                },
            }
            for field in fields:
                if field.metadata.get("alias"):
                    field_args = get_args(field.type)
                    if len(field_args) == 2 and issubclass(field_args[-1], type(None)):
                        field_type = field_args[0]
                    else:
                        field_type = field.type

                    if (
                        field.name == "edited_power_line"
                        and self.svip_file["version"] != "7.0.0"
                    ):
                        continue
                    value = getattr(obj, field.name)
                    if value is None:
                        result["obj"]["member_values"].append(
                            {
                                "value": {
                                    "record_type_enum": RecordTypeEnum.ObjectNull,
                                    "obj": {},
                                }
                            }
                        )
                    else:
                        if issubclass(field_type, str):
                            result["obj"]["member_values"].append(
                                {"value": self.create_string(value or "")}
                            )
                        elif issubclass(field_type, (int, float, bool, enum.IntEnum)):
                            result["obj"]["member_values"].append({"value": value})
                        elif issubclass(field_type, list):
                            if len(value) > 0:
                                subcon_class_name = value[0].__class__.__doc__
                            result["obj"]["member_values"].append(
                                {
                                    "value": self.write_binary_array(
                                        value, subcon_class_name, self.model_library_id
                                    )
                                }
                            )
                        elif issubclass(field_type, bytes):
                            result["obj"]["member_values"].append(
                                {
                                    "value": self.create_primitive_array(
                                        getattr(obj, field.name)
                                    )
                                }
                            )
                        elif dataclasses.is_dataclass(field_type):
                            sub_class_name = field_type.__doc__
                            if field.name == "tempo_list":
                                subcon_class_name = XSSongTempo.__doc__
                            elif field.name == "beat_list":
                                subcon_class_name = XSSongBeat.__doc__
                            elif field.name == "note_list":
                                subcon_class_name = XSNote.__doc__
                            elif field.name == "track_list":
                                subcon_class_name = XSITrack.__doc__

                            if sub_class_name.endswith("List"):
                                sub_class_name = f"{sub_class_name}`1[[{subcon_class_name}, {LIBRARY_NAME_SINGING_TOOL_MODEL}]]"
                            if field.name == "buf_1":
                                obj_id = self.id_max
                            elif hasattr(field_type, "value"):
                                self.id_max += 1
                                obj_id = self.id_max
                            else:
                                obj_id = self.enq()
                            if hasattr(field_type, "value"):
                                result["obj"]["member_values"].append(
                                    {
                                        "value": self.write_dataclass(
                                            value, -obj_id, sub_class_name
                                        )
                                    }
                                )
                            elif field.name.endswith("_line") and not len(
                                value.line_param
                            ):
                                result["obj"]["member_values"].append(
                                    {
                                        "value": {
                                            "record_type_enum": RecordTypeEnum.ObjectNull,
                                            "obj": {},
                                        }
                                    }
                                )
                            else:
                                result["obj"]["member_values"].append(
                                    {
                                        "value": self.create_reference(
                                            value, obj_id, sub_class_name
                                        )
                                    }
                                )
                        else:
                            raise Exception(f"Unknown type {field_type}")
        return result
