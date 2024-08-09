from fastapi import HTTPException

import define
<< << << < HEAD
import setting
== == == =
from config import ConfigManager
from router import config, siyuan, base, remote, local
>> >> >> > dev


# 校验配置是否已经初始化
def validate_config():

    << << << < HEAD
    if not setting.self_config:
== == == =
if not ConfigManager().isConfigCompleted:
>> >> >> > dev
        raise HTTPException(status_code=400, detail=define.ConfigMsg.NOT_INIT)


config_depend = [Depends(validate_config)]

root_router = APIRouter()
root_router.include_router(base.router)
root_router.include_router(config.router)
root_router.include_router(siyuan.router, prefix="/siyuan", dependencies=config_depend)
<< << << < HEAD
root_router.include_router(cloud.router, prefix="/cloud", dependencies=config_depend)

root_router.include_router(check.router, prefix="/check", dependencies=config_depend)
== == == =
root_router.include_router(remote.router, prefix="/remote", dependencies=config_depend)
root_router.include_router(local.router, prefix="/local", dependencies=config_depend)
>> >> >> > dev
