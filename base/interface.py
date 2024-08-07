import logging

from entity.siyuan import SiyuanBlockResource
from tools.base import SingletonMeta


class IBase(metaclass=SingletonMeta):
    @classmethod
    def is_same_as_record(cls, filename, record_path):
        raise NotImplementedError()

    @classmethod
    async def receive(cls, resource: SiyuanBlockResource, log_level=logging.INFO):
        raise NotImplementedError()
