from fastapi import APIRouter

import define
from action import load_cache, ActionRemote
from interface import EndPointMap
from log import get_logger
from model.api_model import RemoteModel, APIResponse, RemoteBaseModel

router = APIRouter()

router_log = get_logger("router_check")


@router.post("/repeat")
async def repeat(request: RemoteModel):
    """检查云盘重复资源"""
    repeat_info = await ActionRemote.check_repeat(request.remote, request.renew_remote)
    data = {"result": True, "message": define.IMsg.OK}
    if request.delete:
        ActionRemote.del_repeat(repeat_info, save_amount=1)

    if request.show:
        data["data"] = repeat_info

    return APIResponse(data=data)


@router.post("/redundancy")
async def redundancy(request: RemoteModel):
    """检查本地未引用的云盘资源"""
    siyuan_cache, remote_cache = await load_cache(request.remote, request.renew_siyuan, request.renew_remote)
    endpoint = EndPointMap[request.remote]
    siyuan_names = {s["filename"] for s in siyuan_cache.values()}
    no_ref_ids = endpoint.check_no_reference(siyuan_names, remote_cache)
    if request.delete:
        ActionRemote.del_repeat(no_ref_ids, save_amount=0)
    data = {"result": True, "message": define.IMsg.OK}
    if request.show:
        data["data"] = no_ref_ids
    return APIResponse(data=data)


@router.post("/reload")
async def reload(request: RemoteBaseModel):
    ActionRemote.renew_cache(request.remote)
    return APIResponse(data={"result": True, "message": define.IMsg.OK})
