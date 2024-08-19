from fastapi import APIRouter

import define
from action import load_cache
from log import get_logger
from model.api_model import RemoteModel, APIResponse

router = APIRouter()

router_log = get_logger("router_local")


@router.post("/lack")
async def lack(request: RemoteModel):
    siyuan, remote = await load_cache(request.remote, request.renew_siyuan, request.renew_remote)
    siyuan_names = [s["filename"] for s in siyuan.values()]
    remote_names = {s["filename"] for s in remote}  # 集合查找快一点
    miss = [name for name in siyuan_names if name in remote_names]
    for filename in miss:
        router_log.info(f"CheckAction.check_miss_in_remote | filename:{filename}")
    router_log.info(f"CheckAction.check_miss_in_remote | amount:{len(miss)}")
    return APIResponse(data={"result": True, "message": define.IMsg.OK})
