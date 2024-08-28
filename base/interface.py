import logging
import posixpath

from entity.siyuan import SiyuanBlockResource
from tools.base import SingletonMeta
from log import get_logger

cloud_log = get_logger("cloud_base")


class IBase(metaclass=SingletonMeta):
    @classmethod
    def is_same_as_record(cls, resource: SiyuanBlockResource, record_path):
        if posixpath.join(resource.file_pre_dir, resource.filename) == record_path:
            cloud_log.debug(f"IBase.is_same_as_record | filename:{resource.filename}")
            return True
        return False

    @classmethod
    async def receive(cls, resource: SiyuanBlockResource, log_level=logging.INFO):
        raise NotImplementedError()
