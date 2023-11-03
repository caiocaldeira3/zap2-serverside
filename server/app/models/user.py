import dataclasses as dc
from typing import Any

from bson import ObjectId


@dc.dataclass()
class OPKey ():
    key_idx: int
    opkey: str

    def to_insert (self) -> dict[str, Any]:
        return {
            field.name: self.__getattribute__(field.name)
            for field in dc.fields(OPKey)
        }
@dc.dataclass()
class User:
    name:str
    telephone: str
    id_key: str
    sgn_key: str
    ed_key: str
    socket_id: str | None
    opkeys: list[OPKey]
    desc: str = dc.field(default="default description")
    _id: ObjectId = dc.field(default_factory=ObjectId)

    def __post_init__ (self) -> None:
        self.opkeys = [
            OPKey(**key) if not isinstance(key, OPKey) else key
            for key in self.opkeys
        ]

    def to_insert (self) -> dict[str, Any]:
        return {
            field.name: (
                self.__getattribute__(field.name)
                if field.name != "opkeys" else
                [ key.to_insert() for key in self.opkeys ]
            ) for field in dc.fields(User)
        }
