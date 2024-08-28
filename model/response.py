import time
import typing

from log import get_logger

response_log = get_logger("response_cloud_123")


class Cloud123FileInfo(typing.TypedDict):
    fileId: int  # 文件 ID
    filename: str  # 文件名
    type: int  # 0 文件 1 文件夹
    size: int  # 文件大小
    etag: str  # 文件 md5
    status: int  # 文件审核状态。 大于 100 为审核驳回文件
    parentFileId: int  # 目录ID
    category: int  # 文件分类：0-未知 1-音频 2-视频 3-图片


class APIErrorMessage:
    文件重复 = "该目录下文件名重复无法创建"
    文件移动_已在当前文件夹 = "文件已在当前文件夹中，请选择其他文件夹"


class Cloud123Response:
    reuse = False

    def __init__(self, response_json):
        self.code = response_json['code']
        self.message = response_json['message']
        self.data = response_json['data']

    @property
    def file_list(self) -> list[Cloud123FileInfo]:
        return self.data["fileList"]

    @property
    def last_file_id(self):
        return self.data["lastFileId"]

    @property
    def info(self):
        return f"code:{self.code} message:{self.message}"

    def Check(self, _from="Cloud123Response.Check"):
        if self.code != 0:
            response_log.error(f"{_from} | {self.info}")
            return False
        return True

    def IsLimit(self, sleep=None):
        if self.code == 429:
            sleep and time.sleep(sleep)
            return True
        return False

    def is_reuse(self):
        return self.reuse or self.data["reuse"]
