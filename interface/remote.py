import asyncio
import logging
import posixpath
import time

import setting
from api.base import CommonRequest
from api.remote import APICloud123
from base.interface import IBase
from entity.siyuan import SiyuanBlockResource
from log import get_logger
from model.response import Cloud123Response
from tools import string
from tools.file import split_file_context, get_file_info

cloud_123_log = get_logger("interface_remote")


class ICloud123(IBase):

    @classmethod
    def cloud_123_get_all_file(cls):
        last_file_id = None
        files = []
        while True:
            response = APICloud123.get_file_list(last_file_id=last_file_id)
            if not response:
                break
            files.extend(response.file_list)
            if -1 == (last_file_id := response.last_file_id):
                break  # -1 代表最后一页（无需再翻页查询）其他代表下一页开始的文件id，携带到请求参数中
            time.sleep(0.5)  # 官方限制 QPS 4
        return files

    @classmethod
    async def receive(cls, resource: SiyuanBlockResource, log_level=logging.DEBUG):
        if not (file_data := await resource.get_file_data()):
            return
        response: Cloud123Response = APICloud123.upload_file(file_data, resource.filename)
        if not response:
            return
        new_path = string.unification_file_path(posixpath.join(setting.cloud_123_remote_path, resource.filename))
        if response.is_reuse():
            cloud_123_log.log(log_level, f"ICloud123.upload | 上传成功 filename:{resource.filename} data:{response.data}")
            return new_path
        file_split_list, chunk_num = split_file_context(file_data, response.data["sliceSize"])
        is_async, completed = await cls._MultiUploadFilePart(response.data["preuploadID"], file_split_list, chunk_num)
        if not is_async:
            return new_path
        await cls._CheckReplace(response.data["preuploadID"], resource.filename, completed)
        return new_path

    # 文件移动
    @classmethod
    def move_file_to_trash(cls, del_ids, step=50):
        for begin in range(0, len(del_ids), step):
            APICloud123.move_file_to_trash(del_ids[begin: begin + step])

    @classmethod
    def move_file_to_custom_history_dir(cls, del_ids, toParentFileId, step=50):
        for begin in range(0, len(del_ids), step):
            APICloud123.move_file_to_dest_dir(del_ids[begin: begin + step], toParentFileId)

    @classmethod
    def is_same_as_record(cls, filename, record_path):
        if posixpath.join(setting.cloud_123_remote_path, filename) == record_path:
            cloud_123_log.debug("ICloud123.already_in | filename")
            return True
        return False

    # region private
    @classmethod
    async def _MultiUploadFilePart(cls, preuploadID, file_split_list, chunk_num):
        for slice_no in range(1, chunk_num + 1):
            response_data = APICloud123.get_slice_upload_url(preuploadID, slice_no).data
            presignedURL = response_data["presignedURL"]
            CommonRequest.Put(presignedURL, data=file_split_list[slice_no - 1])  # TODO @Muu 测试下 123云盘的qps 支不支持异步上传

        response_data = APICloud123.check_upload_integrity(preuploadID).data
        assert response_data is not None
        for index, part in enumerate(response_data["parts"]):
            file_part = file_split_list[index]
            md5, file_size = get_file_info(file_part)
            if md5 != part["etag"] or file_size != part["size"]:
                cloud_123_log.error(f"校验失败 | md5:{md5} file_size:{file_size} etag:{part['etag']} size:{part['size']} part:{part['partNumber']}")
                raise Exception()
            cloud_123_log.info(f"校验成功 | md5:{md5} file_size:{file_size} etag:{part['etag']} size:{part['size']} part:{part['partNumber']}")
        response_data = APICloud123.upload_complete(preuploadID)
        assert response_data is not None
        return response_data.data['async'], response_data.data['completed']

    @classmethod
    async def _CheckReplace(cls, preuploadID, filename, completed, check_times=3):
        """异步校验上传结果"""
        if not completed:
            for i in range(check_times):
                response = APICloud123.upload_async_result(preuploadID).data
                if response and response["completed"]:
                    cloud_123_log.info(f"异步校验上传成功 | filename:{filename} times:{i + 1}")
                    break
                await asyncio.sleep(1)
            else:
                cloud_123_log.error("异步校验上传失败 | filename:{change['res']['filename']} times:{times}")

    # endregion private
