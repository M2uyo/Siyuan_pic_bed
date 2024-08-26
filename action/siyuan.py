import asyncio

from api.siyuan import APISiyuan
from control.siyuan import SiyuanControl
from define.base import SQLWhere
from define.siyuan import SiyuanMessage
from interface import ISiyuan
from log import get_logger
from model.base_model import CustomRecordT
from tools.base import SingletonMeta

action_log = get_logger("action_siyuan")


class SiyuanAction(metaclass=SingletonMeta):
    @classmethod
    async def download_single_notebook_resource(cls, notebook_id, toast=True):
        sql_where = SQLWhere.sep_and.join([SQLWhere.root_id.format(root_id=notebook_id), SQLWhere.type_in])
        resource_dict = await ISiyuan.async_quick_get_resource(where=sql_where)
        custom_record: CustomRecordT = await SiyuanControl.GetCustomRecord(notebook_id)
        success_amount = sum(await asyncio.gather(*(
            SiyuanControl.download_file(resource, custom_record)
            for resource in resource_dict.values()
        )))
        if success_amount:
            toast and await APISiyuan.async_push_msg(SiyuanMessage.下载成功_汇总.format(amount=success_amount))
        else:
            toast and await APISiyuan.async_push_msg(SiyuanMessage.下载成功_无更改)
        await SiyuanControl.SetCustomRecord(notebook_id, custom_record)
        return resource_dict

    @classmethod
    async def upload_single_notebook_resource(cls, notebook_id, toast=True):
        sql_where = SQLWhere.sep_and.join([SQLWhere.root_id.format(root_id=notebook_id), SQLWhere.type_in])
        resource_dict = await ISiyuan.async_quick_get_resource(where=sql_where)
        custom_record: CustomRecordT = await SiyuanControl.GetCustomRecord(notebook_id)
        success_amount = sum(await asyncio.gather(*(
            SiyuanControl.upload_file(resource, custom_record)
            for resource in resource_dict.values()
        )))
        if success_amount:
            toast and await APISiyuan.async_push_msg(SiyuanMessage.上传成功_汇总.format(amount=success_amount))
        else:
            toast and await APISiyuan.async_push_msg(SiyuanMessage.上传成功_无更改)
        await SiyuanControl.SetCustomRecord(notebook_id, custom_record)
        return resource_dict
