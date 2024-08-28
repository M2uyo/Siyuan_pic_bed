import typing
from collections import UserDict
from typing import NamedTuple

from pydantic import BaseModel

from define.base import EndPoint


class SiyuanBaseModel(BaseModel):
    token: str
    toast: bool = True
    end_point: EndPoint = EndPoint.NONE


class NoteBookModel(SiyuanBaseModel):
    method: str = ""
    notebook_id: str = ""
    end_point: EndPoint = EndPoint.CLOUD_123


class SiyuanDatabaseModel(SiyuanBaseModel):
    method: str = ""
    database_id: str = ""
    end_point: EndPoint = EndPoint.CLOUD_123


class SiyuanIconModel(SiyuanBaseModel):
    old_icon: str = ""
    new_icon: str = ""


class Cloud123Model(BaseModel):
    method: str = ""


class Cloud123ConfigModel(BaseModel):
    AK: str
    SK: str
    dir_id: int
    history_dir_id: int = 0
    remote_path: str


class PicGoConfigModel(BaseModel):
    remote_path: str


class SiyuanConfigModel(BaseModel):
    token: str
    data_dir: str


class ConfigModel(BaseModel):
    cloud_123: Cloud123ConfigModel = None
    siyuan: SiyuanConfigModel


class EmptyModel(BaseModel):
    pass


class RemoteModel(BaseModel):
    remote: EndPoint
    renew_siyuan: bool = False
    renew_remote: bool = False
    show: bool = False
    delete: bool = False


class APIResponse(UserDict):
    def __init__(self, data: dict):
        super().__init__({
            "data": data
        })


class PicGoResponse(NamedTuple):
    success: bool
    result: typing.Any
