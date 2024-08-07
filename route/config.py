import os

from fastapi import APIRouter

import define
import setting
from model.api_model import APIResponse, ConfigModel

router = APIRouter()

@router.post("/config")
async def set_config(request: ConfigModel):
    _ = {
        "SK": str(setting.cloud_123_SK),
        "dir": str(setting.cloud_123_dir_id),
        "plugin_path": str(setting.SIYUAN_PLUGINS_PATH),
        "data_path": str(setting.SIYUAN_DATA_PATH)
    }
    try:
        setting.reload_config(request)
    except Exception:
        return APIResponse(data={"result": False, "message": define.ConfigMsg.ILLEGAL_SOURCE})
    return APIResponse(data={"result": True, "message": define.IMsg.OK})


@router.post("/tmp")
async def tmp_control(request):
    if not setting.self_config:
        return APIResponse(data={"result": False, "message": define.ConfigMsg.NOT_INIT})
    if request.method == "clearAllTmp":
        os.rmdir(setting.TEMP_PATH)
        os.mkdir(setting.TEMP_PATH)
        os.mkdir(setting.PART_PATH)
    elif request.method == "clearPart":
        os.rmdir(setting.PART_PATH)
        os.mkdir(setting.PART_PATH)
    return APIResponse(data={"result": True, "message": define.IMsg.OK})


@router.get("/config")
async def get_config():
    if not setting.self_config:
        return APIResponse(data={"result": False, "message": define.ConfigMsg.NOT_INIT})
    import os
    return APIResponse(data={
        "SK": setting.cloud_123_SK,
        "dir": setting.cloud_123_dir_id,
        "history_dir": setting.cloud_123_history_dir_id,
        "plugin_path": setting.SIYUAN_PLUGINS_PATH,
        "data_path": setting.SIYUAN_DATA_PATH,
        "log_path": setting.LOG_PATH,
        "token": setting.siyuan_headers["Authorization"],
        "config_right": setting.self_config,
        "result": True, "message": define.IMsg.OK,
        "cur_location": os.path.abspath(__file__),
        "cwd": os.getcwd(),
    })
