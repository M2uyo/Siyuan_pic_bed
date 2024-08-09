import posixpath

from model.api_model import SiyuanConfigModel
from tools.base import SingletonMeta, exist_or_create


class SiyuanConfig(metaclass=SingletonMeta):
    plugin_name = "plugin-upload-to-cloud"
    server_point = r"http://127.0.0.1:6806/api/"
    default_image_alt = "image"

    # ---------- Sub Dir ----------
    assets_sub_dir = "assets"
    plugin_sub_dir = "plugins"

    config_sub_dir = "config"
    record_sub_dir = "record"

    def __init__(self):
        # ---------- Wait Sync Attribute ----------
        self.header: dict = {}
        self.data_dir: str = ""
        # ---------- Parse ----------
        self.assets_path: str = ""
        self.plugins_path: str = ""
        self.this_plugin_path: str = ""
        # ---------- local storage data path ----------
        self.config_path: str = ""
        self.record_path: str = ""

    def load_config(self, config: SiyuanConfigModel):
        self.header["Authorization"] = config.token
        self.data_dir = posixpath.join(config.data_dir)
        self._Parse()

    def _Parse(self):
        self.assets_path = posixpath.join(self.data_dir, self.assets_sub_dir)
        self.plugins_path = posixpath.join(self.data_dir, self.plugin_sub_dir)
        self.this_plugin_path = posixpath.join(self.plugins_path, self.plugin_name)
        self.config_path = exist_or_create(posixpath.join(self.this_plugin_path, self.config_sub_dir))
        self.record_path = exist_or_create(posixpath.join(self.config_path, self.record_sub_dir))

    def dump(self) -> dict:
        return {
            "header": self.header,
            "data_dir": self.data_dir,
            "assets_path": self.assets_path,
            "plugins_path": self.plugins_path,
            "this_plugin_path": self.this_plugin_path,
            "config_path": self.config_path,
            "record_path": self.record_path,
        }
