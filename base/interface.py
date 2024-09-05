import logging
import posixpath

from entity.siyuan import SiyuanBlockResource, SiyuanDataBaseResource
from model.siyuan import DataBaseResourceInfo
from tools.base import SingletonMeta
from log import get_logger

cloud_log = get_logger("cloud_base")


class IBase(metaclass=SingletonMeta):
    config = None

    @classmethod
    def is_same_as_record(cls, resource: SiyuanBlockResource, pre_dir, record_path):
        if posixpath.join(pre_dir, resource.filename) == record_path:
            cloud_log.debug(f"IBase.is_same_as_record | filename:{resource.filename}")
            return True
        return False

    @classmethod
    def is_same_as_record_database(cls, resource: SiyuanDataBaseResource, remote_path, record_path: list):
        exist, not_exist = [], {}
        filePath = set()
        for index, url in resource.urls.items():
            if url["path"] in record_path:
                if url["path"].startswith(remote_path):
                    exist.append(url)
                else:
                    not_exist[index] = url
            else:
                not_exist[index] = url
            filePath.add(url["path"])
        return exist, not_exist, set(record_path) - filePath

    @classmethod
    async def receive(cls, resource: SiyuanBlockResource, log_level=logging.INFO):
        """块资源"""
        raise NotImplementedError()

    @classmethod
    async def receive_database(cls, urls_info: dict[int, DataBaseResourceInfo], log_level=logging.DEBUG):
        """数据库资源"""
        raise NotImplementedError()

    @classmethod
    def get_all_file(cls):
        raise NotImplementedError()
