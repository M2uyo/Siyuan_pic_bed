from pools import GetAioSession
from tools.base import SingletonMeta

from log import get_logger
import requests

api_log = get_logger("api_base")


class BaseAPI(metaclass=SingletonMeta):
    pass


class CommonAsyncRequest(metaclass=SingletonMeta):
    @classmethod
    async def Get(cls, url, _from="CommonAsyncRequest.Get"):
        session = GetAioSession()
        try:
            response = await session.get(url)
        except Exception as e:
            api_log.info(f"{_from} | url:{url} e:{e}")
            return
        if response.status != 200:
            api_log.info(f"{_from} | url:{url} code:{response.status} reason:{response.reason}")
            return
        return response

    @classmethod
    async def Put(cls, url, _from="CommonAsyncRequest.Put", **kwargs):
        session = GetAioSession()
        try:
            response = await session.put(url, **kwargs, timeout=10)
        except Exception as e:
            api_log.info(f"{_from} |  url:{url} e:{e}")
            return
        if response.status != 200:
            api_log.info(f"{_from} | url:{url} code:{response.status} reason:{response.reason}")
            return
        return response

    @classmethod
    async def Post(cls, url, _from="CommonAsyncRequest.Post", **kwargs):
        session = GetAioSession()
        try:
            response = await session.post(url, **kwargs)
        except Exception as e:
            api_log.info(f"{_from} |  url:{url} e:{e}")
            return
        if response.status != 200:
            api_log.info(f"{_from} | url:{url} code:{response.status} reason:{response.reason}")
            return
        return response


class CommonRequest(metaclass=SingletonMeta):
    @classmethod
    def Get(cls, url, _from="CommonRequest.Get", params=None, **kwargs):
        try:
            response = requests.get(url, params=params, **kwargs)
        except Exception as e:
            api_log.info(f"{_from} | url:{url} e:{e}")
            return
        if response.status_code != 200:
            api_log.info(f"{_from} | url:{url} code:{response.status_code} reason:{response.reason}")
            return
        return response

    @classmethod
    def Post(cls, url, _from="CommonRequest.Post", **kwargs):
        try:
            response = requests.post(url, **kwargs)
        except Exception as e:
            api_log.info(f"{_from} | url:{url} e:{e}")
            return
        if response.status_code != 200:
            api_log.info(f"{_from} | url:{url} code:{response.status_code} reason:{response.reason}")
            return
        return response

    @classmethod
    def Put(cls, url, _from="CommonRequest.put", **kwargs):
        try:
            response = requests.put(url, **kwargs)
        except Exception as e:
            api_log.info(f"{_from} | url:{url} e:{e}")
            return
        if response.status_code != 200:
            api_log.info(f"{_from} | url:{url} code:{response.status_code} reason:{response.reason}")
            return
        return response
