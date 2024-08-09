from config.remote import Cloud123Config
from config.siyuan import SiyuanConfig
from model.api_model import ConfigModel
from tools.base import SingletonMeta


class ConfigManager(metaclass=SingletonMeta):
    def __init__(self):
        self.siyuan = SiyuanConfig()
        self.cloud_123 = Cloud123Config()
        self.isConfigCompleted = False

    def load_config(self, config: ConfigModel):
        self.siyuan.load_config(config.siyuan)
        self.cloud_123.sync_config(config.cloud_123)
        self.isConfigCompleted = True
