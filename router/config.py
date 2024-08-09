import os

from fastapi import APIRouter

import define
import setting
from config import ConfigManager, SiyuanConfig, Cloud123Config
from model.api_model import APIResponse, ConfigModel

router = APIRouter()


@router.post("/config")
async def set_config(request: ConfigModel):
    try:
        ConfigManager().load_config(request)
    except Exception as e:
        return APIResponse(data={"result": False, "message": define.ConfigMsg.ILLEGAL_SOURCE, "error": str(e)})
    return APIResponse(data={"result": True, "message": define.IMsg.OK})


@router.get("/config")
async def get_config():
    if not ConfigManager().isConfigCompleted:
        return APIResponse(data={"result": False, "message": define.ConfigMsg.NOT_INIT})
    return APIResponse(data={
        "config_right": True,
        "result": True,
        "message": define.IMsg.OK,
        "cur_location": os.path.abspath(__file__),
        "log_path": setting.log_path,
        "cwd": os.getcwd(),
        "siyuan": SiyuanConfig().dump(),
        "cloud_123": Cloud123Config().dump()
    })
