import json

from model.api_model import Cloud123ConfigModel
from tools.base import SingletonMeta


class Cloud123Config(metaclass=SingletonMeta):
    api_url = "https://open-api.123pan.com"
    default_header = {"Platform": "open_platform"}

    def __init__(self):
        self.key: dict = {}
        self.dir_id: int = 0  # 资源存储目录
        self.history_dir_id: int = 0  # 删除后的目录 0 回收站
        self.remote_path: str = ""

    def sync_config(self, config: Cloud123ConfigModel):
        self.key = {
            "clientID": config.AK,
            "clientSecret": config.SK
        }
        self.dir_id = int(config.dir_id)
        self.history_dir_id = int(config.history_dir_id)
        self.remote_path = config.remote_path

    def dump(self):
        return {
            "key": self.key,
            "dir_id": self.dir_id,
            "history_dir_id": self.history_dir_id,
            "remote_path": self.remote_path
        }

    def key_dump(self):
        return json.dumps(self.key)