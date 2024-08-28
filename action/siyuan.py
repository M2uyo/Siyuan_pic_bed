import asyncio
import json

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
    async def upload_single_notebook_resource(cls, notebook_id, end_point, toast=True):
        sql_where = SQLWhere.sep_and.join([SQLWhere.root_id.format(root_id=notebook_id), SQLWhere.type_in])
        resource_dict = await ISiyuan.async_quick_get_resource(where=sql_where)
        custom_record: CustomRecordT = await SiyuanControl.GetCustomRecord(notebook_id)
        success_amount = sum(await asyncio.gather(*(
            SiyuanControl.upload_file(resource, custom_record, end_point_enum=end_point)
            for resource in resource_dict.values()
        )))
        if success_amount:
            toast and await APISiyuan.async_push_msg(SiyuanMessage.上传成功_汇总.format(amount=success_amount))
        else:
            toast and await APISiyuan.async_push_msg(SiyuanMessage.上传成功_无更改)
        await SiyuanControl.SetCustomRecord(notebook_id, custom_record)
        return resource_dict

    @classmethod
    async def upload_database_resource(cls, database_id, end_point, toast=True):
        sql_where = SQLWhere._id.format(id=database_id)
        resources, database_json_data, av_file_path = await ISiyuan.async_get_database_resource(where=sql_where)
        if not resources:
            return
        custom_record = await SiyuanControl.GetCustomRecord(database_id, [])
        success_amount = sum(await asyncio.gather(*(
            SiyuanControl.upload_database_resource(resource, custom_record, end_point_enum=end_point)
            for resource in resources
        )))
        if success_amount:
            toast and await APISiyuan.async_push_msg(SiyuanMessage.上传成功_汇总.format(amount=success_amount))
        else:
            toast and await APISiyuan.async_push_msg(SiyuanMessage.上传成功_无更改)
        with open(av_file_path, 'w', encoding='utf-8') as f:
            json.dump(database_json_data, f, ensure_ascii=False)
        await SiyuanControl.SetCustomRecord(database_id, custom_record)
        return resources

    @classmethod
    async def MultiReplaceDocIcon(cls, old_icon, new_icon, toast=True):
        resource_list = await ISiyuan.GetDocByIcon(old_icon)
        if not resource_list:
            toast and await APISiyuan.async_push_msg(SiyuanMessage.替换图标_无更改.format(icon=old_icon))
            return
        await asyncio.gather(*(
            APISiyuan.set_block_attr(_id, {"icon": new_icon})
            for _id in resource_list
        ))
        toast and await APISiyuan.async_push_msg(SiyuanMessage.替换图标_成功.format(amount=len(resource_list), old_icon=old_icon, new_icon=new_icon))
        return resource_list
