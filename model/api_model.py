from collections import UserDict

from pydantic import BaseModel

from define.base import EndPoint


class NoteBookModel(BaseModel):
    method: str = ""
    notebook_id: str = ""


class Cloud123Model(BaseModel):
    method: str = ""


class Cloud123ConfigModel(BaseModel):
    AK: str
    SK: str
    dir_id: int
    history_dir_id: int = 0
    remote_path: str


class SiyuanConfigModel(BaseModel):
    token: str
    data_dir: str


class ConfigModel(BaseModel):
    cloud_123: Cloud123ConfigModel
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
