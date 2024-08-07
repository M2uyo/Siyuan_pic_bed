import define
import setting
from action.remote import ActionCloud123
from model.api_model import Cloud123Model, APIResponse

from fastapi import APIRouter

router = APIRouter()


@router.post("/123")
async def cloud_123(request: Cloud123Model):
    if not setting.self_config:
        return APIResponse(data={"result": False, "message": define.ConfigMsg.NOT_INIT})
    if request.method == "reloadInfo":
        ActionCloud123.get_file_list_info()
        return APIResponse(data={"result": True, "message": define.IMsg.OK})
