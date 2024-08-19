from fastapi import APIRouter, HTTPException, Depends

import define
from config import ConfigManager
from model.api_model import SiyuanBaseModel
from router import config, siyuan, base, remote, local


# 校验配置是否已经初始化
async def validate_config():
    if not ConfigManager().isConfigCompleted:
        raise HTTPException(status_code=400, detail=define.ConfigMsg.NOT_INIT)


# 校验siyuan项目token
async def validate_siyuan_token(request: SiyuanBaseModel):
    if not ConfigManager().check_token_is_exist(request.token):
        raise HTTPException(status_code=400, detail=define.ConfigMsg.TOKEN_NOT_EXIST)
    ConfigManager().cur_token = request.token


config_depend = [Depends(validate_config)]

root_router = APIRouter()
root_router.include_router(base.router)
root_router.include_router(config.router)
root_router.include_router(siyuan.router, prefix="/siyuan", dependencies=config_depend + [Depends(validate_siyuan_token)])
root_router.include_router(remote.router, prefix="/remote", dependencies=config_depend)
root_router.include_router(local.router, prefix="/local", dependencies=config_depend)
