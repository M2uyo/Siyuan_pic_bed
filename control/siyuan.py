import json
import logging

from api.siyuan import APISiyuan
from define.base import ResourceType, EndPoint
from define.siyuan import SiyuanMessage
from entity.siyuan import SiyuanBlockResource, Record, SiyuanDataBaseResource
from interface import EndPointMap, ISiyuan, ICloud123, EndPointConfigMap
from log import get_logger
from tools.base import SingletonMeta

control_log = get_logger("control")


# noinspection SqlNoDataSourceInspection
class SiyuanControl(metaclass=SingletonMeta):

    @classmethod
    async def download_file(cls, resource: SiyuanBlockResource, custom_record, log_level=logging.INFO, endpoint_enum=EndPoint.SIYUAN, toast=True):
        if resource.typ != ResourceType.WEB:
            return  # 本地资源  跳过
        endpoint: ISiyuan = EndPointMap[endpoint_enum]
        if not (new_url := await endpoint.receive(resource, log_level)):
            return False
        toast and await APISiyuan.async_push_msg(SiyuanMessage.下载成功_单文件.format(filename=resource.filename))
        await cls._UpdateInfo(resource, new_url, custom_record)
        return True

    @classmethod
    async def upload_file(cls, resource: SiyuanBlockResource, custom_record, log_level=logging.INFO, endpoint_enum=EndPoint.CLOUD_123, toast=True):
        endpoint: ICloud123 = EndPointMap[endpoint_enum]
        endPointConfig = EndPointConfigMap[endpoint_enum]
        if endpoint.is_same_as_record(resource, endPointConfig.save_pre_path, custom_record.get(resource.id)):
            return False
        if not (new_url := await endpoint.receive(resource, log_level)):
            return False
        toast and await APISiyuan.async_push_msg(SiyuanMessage.上传成功_单文件.format(filename=resource.filename))
        await cls._UpdateInfo(resource, new_url, custom_record)
        return True

    @classmethod
    async def upload_database_resource(cls, resource: SiyuanDataBaseResource, custom_record: list, log_level=logging.INFO, endpoint_enum=EndPoint.CLOUD_123, toast=True):
        endpoint = EndPointMap[endpoint_enum]
        config = EndPointConfigMap[endpoint_enum]
        exist, not_exist, redundant = endpoint.is_same_as_record_database(resource, config.save_pre_path, custom_record)
        if not not_exist:
            if redundant:
                for url in redundant:
                    custom_record.remove(url)
            return 0
        if not (new_urls := await endpoint.receive_database(not_exist, log_level, toast)):
            return 0
        await cls._UploadDatabaseInfo(resource, new_urls, custom_record)
        return len(new_urls)

    @classmethod
    async def _UpdateInfo(cls, resource: SiyuanBlockResource, new_url, record):
        new_data = resource.markdown.replace(resource.url, new_url)
        await APISiyuan.update_block(resource.id, new_data)
        record[resource.id] = new_url

    @classmethod
    async def _UploadDatabaseInfo(cls, resource: SiyuanDataBaseResource, new_urls, record):
        for index, url in new_urls.items():
            resource.ref[index]["content"] = url
        record.extend(new_urls.values())

    # region Record
    """
    自定义文档属性 custom-record
    快速检查 block_id - 资源 是否对应
    如果对应则返回
    不对应  则更新
    """

    @classmethod
    async def GetCustomRecord(cls, notebook_id, default=None):
        if default is None:
            default = {}
        record = (await APISiyuan.get_block_attr(notebook_id))["data"].get("custom-record", default)
        return record and json.loads(record)

    @classmethod
    async def SetCustomRecord(cls, block_id, record):
        await APISiyuan.set_block_attr(block_id, {
            "custom-record": json.dumps(record, ensure_ascii=False),
        })

    @classmethod
    async def clear_deleted_resource_record(cls, resource, record):
        for deleted in record.keys() - resource.keys():
            Record().clear_name(record.pop(deleted))
    # endregion
