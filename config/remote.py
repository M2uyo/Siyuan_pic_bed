import json

from model.api_model import Cloud123ConfigModel, PicGoConfigModel
from tools.base import SingletonMeta


class Cloud123Config(metaclass=SingletonMeta):
    api_url = "https://open-api.123pan.com"
    default_header = {"Platform": "open_platform"}

    def __init__(self):
        self.key: dict = {}
        self.dir_id: int = 0  # 资源存储目录
        self.history_dir_id: int = 0  # 删除后的目录 0 回收站
        self.save_pre_path: str = ""
        self.init = False

    def sync_config(self, config: Cloud123ConfigModel):
        if not config:
            return
        self.key = {
            "clientID": config.AK,
            "clientSecret": config.SK
        }
        self.dir_id = int(config.dir_id)
        self.history_dir_id = int(config.history_dir_id)
        self.save_pre_path = config.remote_path
        self.init = True

    def dump(self):
        if not self.init:
            return "Not init"
        return {
            "key": self.key,
            "dir_id": self.dir_id,
            "history_dir_id": self.history_dir_id,
            "remote_path": self.save_pre_path
        }

    def key_dump(self):
        return json.dumps(self.key)


class PicGoConfig(metaclass=SingletonMeta):
    picgo_url = "http://127.0.0.1:36677/upload"

    def __init__(self):
        self.save_pre_path: str = ""
        self.init = False

    def sync_config(self, config: PicGoConfigModel):
        if not config:
            return
        self.save_pre_path = config.remote_path
        self.init = True

    def dump(self):
        if not self.init:
            return "Not init"
        return {
            "remote_path": self.save_pre_path,
        }
