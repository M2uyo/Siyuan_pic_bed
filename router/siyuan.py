from fastapi import APIRouter

import define
from action.siyuan import SiyuanAction
from entity.siyuan import Record
from interface import ISiyuan
from model.api_model import APIResponse, NoteBookModel, SiyuanIconModel

router = APIRouter()


@router.post("/notebooks")
async def siyuan_notebooks(request: NoteBookModel):
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
        await ISiyuan.get_resource_record(keep_ori=True)
        return APIResponse(data={"result": True, "message": define.IMsg.OK})


@router.post("/icon")
async def siyuan_icon(request: SiyuanIconModel):
    await SiyuanAction.MultiReplaceDocIcon(request.old_icon, request.new_icon, toast=request.toast)
    return APIResponse(data={"result": True, "message": define.IMsg.OK})
