import json
import os
import posixpath
import re
import typing
from collections import defaultdict
from typing import Optional

import setting
from define.base import ResourceType
from model.siyuan import ResourceCache
from tools import string, file
from log import get_logger
from tools.base import SingletonMeta
from tools.file import get_file_name_and_extension, async_get_file_data

entity_log = get_logger("entity")


class SiyuanBlockResource:
    # 匹配整个资源文本 ![](http://xxx.xxx.com/siyuan/Nginx_image_20220512101137719.png)
    resource_pattern = r'!\[.*?\]\(.*?\)\s?'
    # 匹配markdown资源文本中的链接 http://xxx.xxx.com/siyuan/Nginx_image_20220512101137719.png
    resource_link_pattern = r'!\[.*?\]\((.*?)(?=\)| )\s?'

    def __init__(self, block):
        self.id = block["id"]
        self.markdown = block["markdown"]
        self.prefix = block["title"]
        self.typ: Optional[ResourceType] = None
        # ---------- 资源解析 ----------
        self.resource = ""  # 资源的原始文本  ![](http://xxx.xxx.com/siyuan/Nginx%20image_20220512101137719.png)
        self.url = ""  # 资源链接的原始文本   http://xxx.xxx.com/siyuan/Nginx%20image_20220512101137719.png
        self.image_path = ""  # 资源空格转义后路径 http://xxx.xxx.com/siyuan/Nginx_image_20220512101137719.png
        self.filename = ""  # 资源的文件名    Nginx_image_20220512101137719.png

        self.file: bytes = b""
        self.file_md5: str = ""
        self.file_size: int = 0

    def resource_path(self, remote):
        if remote == ResourceType.SIYUAN:
            return posixpath.join(setting.ASSETS_SUB_DIR, self.filename)

    async def parse(self, keep_ori):
        if not await self._GetResource():
            return False
        if keep_ori:
            self._GetOriginFilename()
        else:
            await self._GenFileName()
        return True

    async def _GetResource(self):
        if not (resource := re.search(self.resource_pattern, self.markdown)):
            return False
        self.resource = resource.group()
        self.url = re.search(self.resource_link_pattern, self.resource).group(1)  # 资源链接
        self.image_path = self.url.replace("%20", "_")  # 将空格的转义还原
        self.typ = file.get_file_typ(self.image_path, self.markdown)  # 获取文件类型
        if not self.typ:
            return False
        file_info = await file.get_file_info_by_type(self.url, self.typ)
        if not file_info:
            return False
        self.file, self.file_md5, self.file_size = file_info
        return True

    def _GetOriginFilename(self):
        _, file_name, extension = file.get_file_name_and_extension(self.url)
        self.filename = f"{file_name}{extension}"

    async def _GenFileName(self):
        _, ori_file_name, extension = file.get_file_name_and_extension(self.image_path)
        filename, ori_num = string.get_true_file_name(ori_file_name)
        if custom_name := _GetSourceName(self.resource.replace(self.url, "")):
            # 如果标题或者提示文本匹配成功，使用其替换filename
            filename = custom_name
        # 替换文本中的特殊字符
        filename = string.replace_special_characters(filename)
        # 加标题为前缀
        filename = string.add_prefix(filename, self.prefix)
        self.filename = self._GetRecordFileName(filename, ori_num, extension)

    def _GetRecordFileName(self, filename, ori_num, extension, suffix=""):
        """
        如果文件名已存在, 对比两个文件的md5
            如果md5相同则认为是相同文件 直接复用原始名称
            如果md5不同则 在原始后缀名后 + 1
        """
        base_filename = f"{filename}{extension}"  # 无后缀的文件名
        origin_filename = f"{filename}{string.get_suffix_by_num(ori_num)}{extension}"  # 可能带后缀的原始路径

        if number := Record().check_name_exist(base_filename):
            if Record().check_exist_ori_file(self.file_md5, origin_filename):
                return origin_filename  # 文件名-文件 对应
            suffix = f"{setting.num_tag}{number}"  # 当前已使用的最大number 是 number - 1 故这里直接使用number
        Record().incr_name_count(base_filename)  # 增加文件名记录
        entity_log.info(f"SiyuanBlockResource._GetRecordFileName | filename:{filename}{suffix}{extension}")
        new_filename = f"{filename}{suffix}{extension}"
        Record().update_one_new_file(new_filename, self.file_md5)  # 记录文件名md5
        return new_filename

    def dump(self) -> ResourceCache:
        return {
            "ori_image_path": self.url,
            "image_path": self.image_path,
            "filename": self.filename,
            "type": self.typ
        }

    async def get_file_data(self):
        return await async_get_file_data(self.image_path, self.typ)


class Record(metaclass=SingletonMeta):
    def __init__(self):
        self.name = {}
        self.name_md5_map = {}
        self.md5_name_map = {}

    def load_data(self):
        entity_log.info("load_record | start")
        if os.path.exists(path := posixpath.join(setting.RECORD_PATH, "siyuan_name.json")):
            with open(path, "r", encoding="utf8") as f:
                self.name = json.load(f)
        if os.path.join(posixpath.join(setting.RECORD_PATH, "name_md5_map.json")):
            with open(path, "r", encoding="utf8") as f:
                self.name_md5_map = json.load(f)
        self.build_image()
        entity_log.info("load_record | finished")

    def build_image(self):
        for name, md5 in self.name_md5_map.items():
            self.md5_name_map.setdefault(md5, set()).add(name)

    def save(self):
        entity_log.info("save_record | ")
        with open(posixpath.join(setting.RECORD_PATH, "siyuan_name.json"), "w", encoding="utf8") as f:
            json.dump(self.name, f, ensure_ascii=False, indent=4)
        with open(posixpath.join(setting.RECORD_PATH, "name_md5_map.json"), "w", encoding="utf8") as f:
            json.dump(self.name_md5_map, f, ensure_ascii=False, indent=4)

    @staticmethod
    def auto_record(func):
        def wrapper(*args, **kwargs):
            ret = func(*args, **kwargs)
            Record().save()
            return ret

        return wrapper

    def update_one_new_file(self, filename, md5):
        self.md5_name_map.setdefault(md5, set()).add(filename)
        self.name_md5_map[filename] = md5

    def check_name_exist(self, name):
        return self.name.get(name)

    def incr_name_count(self, name):
        self.name[name] = self.name.get(name, 0) + 1

    def check_exist_ori_file(self, md5, filename):
        if exist_file_names := self.md5_name_map.get(md5):
            if filename in exist_file_names:
                entity_log.debug(f"use old name | filename:{filename}")
                return True
            entity_log.warning(f"文件已存在 但 md5不匹配 | exist:{exist_file_names} filename:{filename}")
        return False

    def reset_name(self, resources: typing.Iterable[SiyuanBlockResource]):
        self.name = defaultdict(int)
        for resource in resources:
            file_dir, file_name, ext = get_file_name_and_extension(resource.image_path)
            suffix = file_name.split(setting.num_tag)[-1]
            if suffix.isdigit() and int(suffix) < 100:
                file_name = file_name[:-len(suffix) - 1]
            # 只保留不包含 num_tag 的原始文件名
            self.name[file_name.replace(setting.num_tag, "_") + ext] += 1
        with open(posixpath.join(setting.RECORD_PATH, "siyuan_name.json"), "w", encoding="utf8") as f:
            json.dump(self.name, f, ensure_ascii=False, indent=4)


def _GetSourceName(text):
    """
    Returns:
        标题 或 提示文本 | 无后缀
    """
    name_pattern = r'\s"(.*?)"\)'  # 匹配标题
    alt_pattern = r"!\[(.*?)\]"  # 匹配提示文本
    # 正则表达式匹配图片名称
    if name_match := re.search(alt_pattern, text):
        # 提示文本存在且非默认文本时 使用提示文本
        name_temp = name_match.group(1).strip()
        if name_temp and name_temp != "image":
            return name_match.group(1).strip()
    if name_match := re.search(name_pattern, text):
        # 当标题存在时 使用标题
        return name_match.group(1).strip()
