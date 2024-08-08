from action.remote import ActionRemote
from define.base import EndPoint
from interface import ISiyuan, EndPointMap


async def load_cache(_remote, renew_siyuan=False, renew_remote=False):
    siyuan: ISiyuan = EndPointMap[EndPoint.SIYUAN]
    return await siyuan.load_cache(renew_siyuan), await ActionRemote.load_cache(_remote, renew_remote)
