import json

import requests

from api.base import BaseAPI
from config import SiyuanConfig
from log import get_logger
from pools import GetAioSession

api_log = get_logger("api_siyuan")


class APISiyuan(BaseAPI):
    @classmethod
    async def async_sql_query(cls, stmt):
        """执行sql语句"""
        api_log.debug(f"APISiyuan.async_sql_query | stmt:{stmt}")
        session = GetAioSession()
        async with session.post(
                SiyuanConfig.server_point + "query/sql",
                data=f'{{"stmt": "{stmt}"}}', headers=SiyuanConfig().header
        ) as response:
            return await response.json()

    @classmethod
    async def get_kramdown(cls, _id):
        session = GetAioSession()
        async with session.post(
                SiyuanConfig.server_point + "block/getBlockKramdown",
                data=json.dumps({
                    "id": _id
                }), headers=SiyuanConfig().header
        ) as response:
            return await response.json()

    @classmethod
    async def get_sub_block(cls, _id):
        session = GetAioSession()
        async with session.post(
                SiyuanConfig.server_point + "block/getChildBlocks",
                data=json.dumps({
                    "id": _id
                }), headers=SiyuanConfig().header
        ) as response:
            return await response.json()

    @classmethod
    async def get_block_attr(cls, _id):
        session = GetAioSession()
        async with session.post(
                SiyuanConfig.server_point + "attr/getBlockAttrs",
                data=json.dumps({
                    "id": _id
                }), headers=SiyuanConfig().header
        ) as response:
            return await response.json()

    @classmethod
    async def set_block_attr(cls, _id, _attrs):
        session = GetAioSession()
        async with session.post(
                SiyuanConfig.server_point + "attr/setBlockAttrs",
                data=json.dumps({
                    "id": _id,
                    "attrs": _attrs
                }), headers=SiyuanConfig().header
        ) as response:
            return await response.json()

    @classmethod
    async def update_block(cls, _id, _data, data_type="markdown"):
        session = GetAioSession()
        async with session.post(
                SiyuanConfig.server_point + "block/updateBlock",
                data=json.dumps({
                    "dataType": data_type,
                    "id": _id,
                    "data": _data
                }), headers=SiyuanConfig().header
        ) as response:
            return await response.json()

    # ---------- Message ----------
    @classmethod
    async def async_push_msg(cls, msg, timeout=7000):
        session = GetAioSession()
        async with session.post(
                SiyuanConfig.server_point + "notification/pushMsg",
                data=json.dumps({
                    "msg": msg,
                    "timeout": timeout
                }), headers=SiyuanConfig().header
        ) as response:
            return await response.json()

    @classmethod
    async def async_push_err_msg(cls, msg, timeout=7000):
        session = GetAioSession()
        async with session.post(
                SiyuanConfig.server_point + "notification/pushErrMsg",
                data=json.dumps({
                    "msg": msg,
                    "timeout": timeout
                }), headers=SiyuanConfig().header
        ) as response:
            return await response.json()

    @classmethod
    def push_msg(cls, msg, timeout=7000):
        return requests.post(
            SiyuanConfig.server_point + "notification/pushMsg",
            data=json.dumps({
                "msg": msg,
                "timeout": timeout
            }), headers=SiyuanConfig().header
        ).json()

    @classmethod
    def push_err_msg(cls, msg, timeout=7000):
        return requests.post(
            SiyuanConfig.server_point + "notification/pushErrMsg",
            data=json.dumps({
                "msg": msg,
                "timeout": timeout
            }), headers=SiyuanConfig().header
        ).json()
