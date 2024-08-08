from fastapi import APIRouter

import define
from action import load_cache, ActionRemote
from define.base import EndPoint
from interface import EndPointMap
from log import get_logger
from model.api_model import CheckModel, APIResponse

router = APIRouter()

router_log = get_logger("router_check")


@router.post("/repeat")
async def repeat(request: CheckModel):
    """检查云盘重复资源"""
    remote = getattr(EndPoint, request.remote, None)
    if remote is None:
        return APIResponse(data={"result": True, "message": define.IMsg.ILLEGAL_PARAMETER.format(args=f"remote:{request.remote}")})
    await ActionRemote.check_repeat(remote, None, request.delete)
    return APIResponse(data={"result": True, "message": define.IMsg.OK})


@router.post("/redundancy")
async def redundancy(request: CheckModel):
    """检查本地未引用的云盘资源"""
    remote = getattr(EndPoint, request.remote, None)
    if remote is None:
        return APIResponse(data={"result": True, "message": define.IMsg.ILLEGAL_PARAMETER.format(args=f"remote:{request.remote}")})
    siyuan_cache, remote_cache = await load_cache(remote, request.renew_siyuan, request.renew_remote)
    end_point = EndPointMap[remote]
    siyuan_names = {s["filename"] for s in siyuan_cache.values()}
    no_ref_ids = end_point.check_no_reference(siyuan_names, remote_cache)
    if request.delete:
        ActionRemote.del_repeat(no_ref_ids, save_amount=0)
    data = {"result": True, "message": define.IMsg.OK}
    if request.show:
        data["data"] = no_ref_ids
    return APIResponse(data=data)
