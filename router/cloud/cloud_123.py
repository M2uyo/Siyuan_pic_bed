from fastapi import APIRouter

import define
from action.remote import ActionRemote
from model.api_model import Cloud123Model, APIResponse

router = APIRouter()


@router.post("/123")
async def cloud_123(request: Cloud123Model):
    if request.method == "reloadInfo":
        ActionRemote.renew_cache()
        return APIResponse(data={"result": True, "message": define.IMsg.OK})
