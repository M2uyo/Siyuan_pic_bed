from config.remote import Cloud123Config
from config.siyuan import SiyuanConfig
from model.api_model import ConfigModel
from tools.base import SingletonMeta
from log import get_logger

router_log = get_logger('router')


class ConfigManager(metaclass=SingletonMeta):
    def __init__(self):
        self._siyuan: dict[str, SiyuanConfig] = {}
        self.cloud_123 = Cloud123Config()
        self.isConfigCompleted = False

        self.cur_token = None

    @property
    def siyuan(self):
        return self._siyuan[self.cur_token]

    def check_token_is_exist(self, token):
        return token in self._siyuan

    def load_config(self, config: ConfigModel):
        _siyuan = self._siyuan.setdefault(config.siyuan.token, SiyuanConfig())
        if _siyuan.init:
            if not _siyuan.check_repeat_token(config.siyuan):
                from api.siyuan import APISiyuan
                APISiyuan.push_err_msg(f"重复的token | token:{config.siyuan.token} path1:{config.siyuan.data_dir} path2:{_siyuan.data_dir}")
                router_log.error(f"ConfigManager.load_config | 重复的token | token:{config.siyuan.token} path1:{config.siyuan.data_dir} path2:{_siyuan.data_dir}")
                assert False
        else:
            router_log.info(f"ConfigManager.load_config | new config | token:{config.siyuan.token} path:{config.siyuan.data_dir}")
        _siyuan.load_config(config.siyuan)
        self.cloud_123.sync_config(config.cloud_123)
        self.cur_token = config.siyuan.token
        self.isConfigCompleted = True
        return True
