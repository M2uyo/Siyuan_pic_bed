import os
import posixpath
from os.path import expanduser

from model.api_model import ConfigModel
from tools.base import exist_or_create

home_directory = expanduser("~")

# ---------- 项目设置 ----------
# 启动设置
PORT = 38546
HOST = "127.0.0.1"
# 全局参数
num_tag = "-"
UTF8 = "utf-8"
# ---------- 项目路径 ----------
# 插件配置路径
CONFIG_PATH = ""
RECORD_PATH = ""
# ---------- 思源API配置 ----------
ASSETS_SUB_DIR = "assets"
SIYUAN_MY_PLUGIN_PATH = ""
SIYUAN_PLUGINS_PATH = ""
SIYUAN_DATA_PATH = ""
ASSETS_PATH = ""

# 临时文件存储位置
PIC_BED_PATH = ""
TEMP_PATH = ""
LOG_PATH = exist_or_create(os.path.join(home_directory, ".config", "siyuan", "log"))
PART_PATH = ""

siyuan_server_point = r"http://127.0.0.1:6806/api/"
special_replace_pattern = r'[、，()<>:"/\\|\-?*\'\s]|&quot;'
siyuan_default_image_alt = "image"
# ---------- 123云盘配置 ----------

cloud_123_api_url = "https://open-api.123pan.com"
cloud_123_default_header = {"Platform": "open_platform"}
# ---------- picgo配置 ----------
picgo_url = "http://127.0.0.1:36677/upload"

test_pic_url = "https://pics3.sucaisucai.com/jingxuanbizhi/heiseshawenjianyuexpbizhi/jingxuan_jingxuanyitu_257126_18.jpg"

# 待同步配置
self_config = False
cloud_123_SK = {
    "clientID": "123456",
    "clientSecret": "123456"
}
cloud_123_dir_id = 123456
cloud_123_history_dir_id = 0
siyuan_headers = {
    "Authorization": ""
}
cloud_123_remote_path = ""


def reload_config(config: ConfigModel):
    global cloud_123_SK, cloud_123_dir_id, cloud_123_history_dir_id, cloud_123_remote_path
    cloud_123_SK["clientID"] = config.cloud_123.AK
    cloud_123_SK["clientSecret"] = config.cloud_123.SK
    cloud_123_dir_id = int(config.cloud_123.dir_id)
    cloud_123_history_dir_id = int(config.cloud_123.history_dir_id)
    cloud_123_remote_path = config.cloud_123.remote_path
    global siyuan_headers
    siyuan_headers["Authorization"] = config.token
    global SIYUAN_DATA_PATH
    SIYUAN_DATA_PATH = posixpath.join(config.siyuan_data_dir)
    global SIYUAN_PLUGINS_PATH, ASSETS_PATH, SIYUAN_MY_PLUGIN_PATH
    ASSETS_PATH = posixpath.join(SIYUAN_DATA_PATH, ASSETS_SUB_DIR)
    SIYUAN_PLUGINS_PATH = posixpath.join(SIYUAN_DATA_PATH, "plugins")
    SIYUAN_MY_PLUGIN_PATH = posixpath.join(SIYUAN_PLUGINS_PATH, "plugin-upload-to-cloud")
    global CONFIG_PATH, RECORD_PATH
    CONFIG_PATH = exist_or_create(posixpath.join(SIYUAN_MY_PLUGIN_PATH, "config"))
    RECORD_PATH = exist_or_create(posixpath.join(CONFIG_PATH, "record"))
    global PIC_BED_PATH, TEMP_PATH, LOG_PATH, PART_PATH
    PIC_BED_PATH = exist_or_create(posixpath.join(os.path.dirname(SIYUAN_DATA_PATH), "pic_bed"))
    # LOG_PATH = exist_or_create(posixpath.join(PIC_BED_PATH, "output", "log"))
    TEMP_PATH = exist_or_create(posixpath.join(PIC_BED_PATH, "tmp"))
    PART_PATH = exist_or_create(posixpath.join(TEMP_PATH, "part"))
    # 激活配置
    global self_config
    self_config = True
    from entity.siyuan import Record
    Record().load_data()
