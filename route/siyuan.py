import define
import setting
from action.local import CheckAction
from action.siyuan import SiyuanAction
from model.api_model import APIResponse, NoteBookModel, CheckModel
from entity.siyuan import Record
from fastapi import APIRouter

router = APIRouter()


@router.post("/notebooks")
async def siyuan_notebooks(request: NoteBookModel):
    if not setting.self_config:
        return APIResponse(data={"result": False, "message": define.ConfigMsg.NOT_INIT})
    if request.method == define.NotebookMethod.上传所有文档图片:
        # 同步所有笔记本的图像文件到123云盘
        # do_upload_all_notebook_pic(False)  # 暂时屏蔽
        return APIResponse(data={"result": False, "message": define.IMsg.BAN})
    elif request.method == define.NotebookMethod.下载指定文档图片:
        await SiyuanAction.download_single_notebook_resource(request.notebook_id)
        Record().save()
        return APIResponse({"result": True, "message": define.IMsg.OK})
    elif request.method == define.NotebookMethod.下载所有文档图片:
        return APIResponse(data={"result": False, "message": define.IMsg.BAN})
    elif request.method == define.NotebookMethod.上传指定文档图片:
        # try:
        await SiyuanAction.upload_single_notebook_resource(request.notebook_id)
        # except Exception as e:
        #     await APISiyuan.push_err_msg(f"上传失败: {str(e)}")
        #     return APIResponse({"result": False, "message": str(e)})
        Record().save()
        return APIResponse(data={"result": True, "message": define.IMsg.OK})
    elif request.method == define.NotebookMethod.加载文件信息:
        await SiyuanAction.get_siyuan_resource_record(keep_ori=True)
        return APIResponse(data={"result": True, "message": define.IMsg.OK})


@router.post("/check")
async def check(request: CheckModel):
    if not setting.self_config:
        return APIResponse(data={"result": False, "message": define.ConfigMsg.NOT_INIT})
    if request.method == define.CheckMethod.远程重复文件:
        await CheckAction.check_repeat_cloud_123(**request.kwargs)
    elif request.method == define.CheckMethod.远程冗余文件:
        await CheckAction.check_no_ref_resource_in_cloud_123(**request.kwargs)
    elif request.method == define.CheckMethod.本地缺失文件:
        CheckAction.check_miss_in_remote(**request.kwargs)
    return APIResponse(data={"result": True, "message": define.IMsg.OK})
