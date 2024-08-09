import asyncio
import json
import logging
import posixpath

import aiofiles

import setting
from api.siyuan import APISiyuan
from base.interface import IBase
from define.base import SQLWhere
from entity.siyuan import SiyuanBlockResource, Record
from log import get_logger
from model.siyuan import ResourceCache
from tools.file import get_file_info, get_file_info_by_type, async_save_data_to_local_file
from tools.string import unification_file_path

interface_log = get_logger("interface_local")


# noinspection SqlNoDataSourceInspection
class ISiyuan(IBase):
    cache_file_name = "siyuan.json"

    @classmethod
    async def async_quick_get_resource(cls, step=200, keep_ori=False, where=None) -> dict[int, SiyuanBlockResource]:
        """快速获取带有资源的块数据"""
        if not where:
            where = " and ".join([f"markdown like %{setting.cloud_123_remote_path}%", SQLWhere.type_in])
        total_amount = (await APISiyuan.async_sql_query(f"select count(*) as total from blocks b where {where}"))['data'][0]['total']
        resource_dict = {}

        async def parse_block_resource(block):
            block_resource = SiyuanBlockResource(block)
            if not await block_resource.parse(keep_ori=keep_ori):
                return
            resource_dict[block["id"]] = block_resource

        interface_log.info(f"ISiyuan.async_quick_get_resource | total_amount:{total_amount}")
        for begin in range(0, total_amount, step):
            sql = f"select id, markdown, (select content from blocks where id=b.root_id) as title from blocks b where {where} limit {step} offset {begin};"
            response = await APISiyuan.async_sql_query(sql)
            await asyncio.gather(*(parse_block_resource(block) for block in response['data']))
        interface_log.info(f"ISiyuan.async_quick_get_resource | len:{len(resource_dict)}")
        return resource_dict

    @classmethod
    def is_same_as_record(cls, filename, record_path):
        """校验是否已经是siyuan:assets"""
        if posixpath.join(setting.ASSETS_SUB_DIR, filename) == record_path:
            interface_log.debug(f"ICloud123.is_same_as_record | filename:{filename}")
            return True
        return False

    @classmethod
    async def receive(cls, resource: SiyuanBlockResource, log_level=logging.DEBUG):
        """保存资源到思源assets"""
        if not (web_file_data := resource.get_file_data()):
            return False  # 请求失败
        web_file_info = get_file_info(web_file_data)
        # 检查请求是否成功
        save_path, new_url = cls._GetSaveInfo(None, resource.filename)
        # 以二进制方式写入文件
        if posixpath.exists(save_path) and web_file_info == await get_file_info_by_type(save_path, resource.typ):
            interface_log.warning(f"ISiyuan.receive | 图片在本地已经存在 | img_url:{resource.url} save_path:{save_path}")
        else:
            await async_save_data_to_local_file(save_path, web_file_data)
        interface_log.log(log_level, f"ISiyuan.receive | 图片已成功保存 | img_url:{resource.url} save_path:{save_path}")
        return new_url

    @classmethod
    async def get_resource_record(cls, keep_ori=False) -> (dict[int, SiyuanBlockResource], dict[int, ResourceCache]):
        sql_where = SQLWhere.sep.join([SQLWhere.type_in])
        resource_dict = await cls.async_quick_get_resource(keep_ori=keep_ori, where=sql_where)
        cache_path = posixpath.join(setting.RECORD_PATH, cls.cache_file_name)
        interface_log.info(f"ISiyuan.get_resource_record | path:{cache_path}")
        json_info = {_id: resource.dump() for _id, resource in resource_dict.items()}
        with open(cache_path, "w", encoding=setting.UTF8) as f:
            json.dump(json_info, f, ensure_ascii=False, indent=4)
        Record().reset_name(resource_dict.values())
        return resource_dict, json_info

    # region Check Cache
    @classmethod
    async def renew_cache(cls, keep_ori) -> dict[int, ResourceCache]:
        _, cache = await cls.get_resource_record(keep_ori=keep_ori)
        return cache

    @classmethod
    async def load_cache(cls, renew) -> dict[int, ResourceCache]:
        if renew:
            return await cls.renew_cache(True)
        async with aiofiles.open(posixpath.join(setting.RECORD_PATH, cls.cache_file_name), "rb") as f:
            text = (await f.read()).decode(setting.UTF8)  # 假设文件是以utf-8编码
            return json.loads(text)

    # endregion Check Cache

    @classmethod
    def _GetSaveInfo(cls, save_dir, filename):
        """
        Args:
            save_dir: 默认存储到笔记的assets路径下
        Returns
            save_dir: 保存目录
            link_dir: 链接中的目录
        """
        if save_dir is None:
            # 默认为下载操作
            save_dir = setting.ASSETS_PATH
            link_dir = setting.ASSETS_SUB_DIR
        else:  # 默认为 先下载到临时文件夹 然后再上传到指定远程目录
            link_dir = save_dir
        save_path = posixpath.join(save_dir, filename)
        link_path = posixpath.join(link_dir, filename)
        return unification_file_path(save_path), unification_file_path(link_path)
