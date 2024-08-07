import asyncio
import json
import posixpath

import setting
from action.remote import ActionCloud123
from api.siyuan import APISiyuan
from control.siyuan import SiyuanControl
from define.base import SQLWhere
from define.siyuan import SiyuanMessage
from entity.siyuan import Record
from model.base_model import CustomRecordT
from tools.base import SingletonMeta
from log import get_logger

action_log = get_logger("action_siyuan")


class SiyuanAction(metaclass=SingletonMeta):
    @classmethod
    async def download_single_notebook_resource(cls, notebook_id, toast=True):
        sql_where = SQLWhere.sep.join([SQLWhere.root_id.format(root_id=notebook_id), SQLWhere.type_in])
        resource_dict = await SiyuanControl.async_quick_get_resource(where=sql_where)
        custom_record: CustomRecordT = await SiyuanControl.GetCustomRecord(notebook_id)
        success_amount = sum(await asyncio.gather(*(
            SiyuanControl.download_file(resource, custom_record)
            for resource in resource_dict.values()
        )))
        if success_amount:
            toast and APISiyuan.push_msg(SiyuanMessage.下载成功_汇总.format(amount=success_amount))
        else:
            toast and APISiyuan.push_msg(SiyuanMessage.下载成功_无更改)
        await SiyuanControl.SetCustomRecord(notebook_id, custom_record)
        return resource_dict

    @classmethod
    async def upload_single_notebook_resource(cls, notebook_id, toast=True):
        sql_where = SQLWhere.sep.join([SQLWhere.root_id.format(root_id=notebook_id), SQLWhere.type_in])
        resource_dict = await SiyuanControl.async_quick_get_resource(where=sql_where)
        custom_record: CustomRecordT = await SiyuanControl.GetCustomRecord(notebook_id)
        success_amount = sum(await asyncio.gather(*(
            SiyuanControl.upload_file(resource, custom_record)
            for resource in resource_dict.values()
        )))
        if success_amount:
            toast and APISiyuan.push_msg(SiyuanMessage.上传成功_汇总.format(amount=success_amount))
        else:
            toast and APISiyuan.push_msg(SiyuanMessage.上传成功_无更改)
        await SiyuanControl.SetCustomRecord(notebook_id, custom_record)
        return resource_dict

    @classmethod
    async def get_siyuan_resource_record(cls, keep_ori=False):
        sql_where = SQLWhere.sep.join([SQLWhere.type_in])
        resource_dict = await SiyuanControl.async_quick_get_resource(keep_ori=keep_ori, where=sql_where)
        action_log.info(f"SiyuanAction.do_get_all_siyuan_image | path:{posixpath.join(setting.RECORD_PATH, 'siyuan.json')}")
        with open(posixpath.join(setting.RECORD_PATH, "siyuan.json"), "w", encoding="utf8") as f:
            json.dump({_id: resource.dump() for _id, resource in resource_dict.items()}, f, ensure_ascii=False, indent=4)
        Record().reset_name(resource_dict.values())
        return resource_dict


async def renew_cache(siyuan=False, cloud_123=False, keep_ori=True):
    cache = {}
    if siyuan:
        siyuan_info = await SiyuanAction.get_siyuan_resource_record(keep_ori=keep_ori)
        cache["siyuan"] = [s.filename for s in siyuan_info.values()]
    if cloud_123:
        cache["cloud_123"] = ActionCloud123.get_file_list_info()  # NOTICE @Muu 同步方法
    return cache
