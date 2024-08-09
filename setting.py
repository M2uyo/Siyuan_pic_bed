# ---------- 项目设置 ----------
# 启动设置
import os
import posixpath


def exist_or_create(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path


PORT = 38546
HOST = "127.0.0.1"
# 全局参数
num_tag = "-"
UTF8 = "utf-8"

special_replace_pattern = r'[、，()<>:"/\\|\-?*\'\s]|&quot;'

# ---------- picgo配置 ----------
picgo_url = "http://127.0.0.1:36677/upload"
test_pic_url = "https://pics3.sucaisucai.com/jingxuanbizhi/heiseshawenjianyuexpbizhi/jingxuan_jingxuanyitu_257126_18.jpg"

home_directory = posixpath.expanduser("~")
log_path = exist_or_create(posixpath.join(home_directory, ".config", "siyuan", "log"))
