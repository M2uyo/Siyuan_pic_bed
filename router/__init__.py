from fastapi import APIRouter, HTTPException, Depends

import define
from config import ConfigManager
from define.base import EndPoint
from model.api_model import SiyuanBaseModel
from router import config, siyuan, base, remote, local


# 校验siyuan项目token
async def validate_siyuan_init(request: SiyuanBaseModel):
    if not (cfg := ConfigManager().get_config(request.token)):
        raise HTTPException(status_code=400, detail=define.ConfigMsg.TOKEN_NOT_EXIST)
    if not cfg.init:
        raise HTTPException(status_code=400, detail=define.ConfigMsg.NOT_INIT.format(name="思源"))
    if request.endpoint == EndPoint.CLOUD_123:
        if not ConfigManager().cloud_123.init:
            raise HTTPException(status_code=400, detail=define.ConfigMsg.NOT_INIT.format(name="123云盘"))
    elif request.endpoint == EndPoint.PICGO:
        if not ConfigManager().picgo.init:
            raise HTTPException(status_code=400, detail=define.ConfigMsg.NOT_INIT.format(name="PicGo"))
    elif request.endpoint == EndPoint.SIYUAN:
        pass
    elif request.endpoint == EndPoint.NONE:
        raise HTTPException(status_code=400, detail=define.ConfigMsg.ILLEGAL_SOURCE)
    ConfigManager().cur_token = request.token


config_depend = [Depends(validate_siyuan_init)]

root_router = APIRouter()
root_router.include_router(base.router)
root_router.include_router(config.router)
root_router.include_router(siyuan.router, prefix="/siyuan", dependencies=config_depend)
root_router.include_router(remote.router, prefix="/remote", dependencies=config_depend)
root_router.include_router(local.router, prefix="/local", dependencies=config_depend)
