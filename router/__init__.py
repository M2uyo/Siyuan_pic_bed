from fastapi import APIRouter, HTTPException, Depends

import define
import setting
from router import config, siyuan, cloud, check, base


# 校验配置是否已经初始化
def validate_config():
    if not setting.self_config:
        raise HTTPException(status_code=400, detail=define.ConfigMsg.NOT_INIT)


config_depend = [Depends(validate_config)]

root_router = APIRouter()
root_router.include_router(base.router)
root_router.include_router(config.router)
root_router.include_router(siyuan.router, prefix="/siyuan", dependencies=config_depend)
root_router.include_router(cloud.router, prefix="/cloud", dependencies=config_depend)

root_router.include_router(check.router, prefix="/check", dependencies=config_depend)
