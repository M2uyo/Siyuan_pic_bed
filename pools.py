import aiohttp

from tools.base import SingletonMeta

session = None


class AioSession(metaclass=SingletonMeta):
    def __init__(self):
        self.session = aiohttp.ClientSession(
            read_bufsize=2 ** 24,
            max_line_size=81960,
            max_field_size=81960
        )

    async def close(self):
        await self.session.close()


def GetAioSession():
    return AioSession().session
