import asyncio
import logging
import posixpath
import time
from operator import itemgetter

from api.base import CommonRequest
from api.remote import APICloud123
from base.interface import IBase
from config import Cloud123Config
from entity.siyuan import SiyuanBlockResource
from log import get_logger
from model.response import Cloud123Response, Cloud123FileInfo
from tools import string
from tools.file import split_file_context, get_file_info

cloud_123_log = get_logger("interface_remote")


class ICloud123(IBase):

    @classmethod
    def get_all_file(cls):
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
        new_path = string.unification_file_path(posixpath.join(Cloud123Config().remote_path, resource.filename))
        if response.is_reuse():
            cloud_123_log.log(log_level, f"ICloud123.upload | 上传成功 | filename:{resource.filename} data:{response.data}")
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
        if posixpath.join(Cloud123Config().remote_path, filename) == record_path:
            cloud_123_log.debug(f"ICloud123.is_same_as_record | filename:{filename}")
            return True
        return False

    # region Check
    @classmethod
    def check_repeat_file(cls, ori_info: list[Cloud123FileInfo]) -> dict[str, dict[str, list]]:
        """
        Returns:
            {filename: {etag: file_ids}}
        """
        files = {}
        for file in sorted(ori_info, key=itemgetter("fileId"), reverse=True):
            _file = files.setdefault(file["filename"], {})
            _file.setdefault(file["etag"], []).append(file["fileId"])
            _file["amount"] = 1 + _file.get("amount", 0)
        repeats = {}
        for filename, file_info in files.items():
            if file_info["amount"] > 1:
                repeats[filename] = file_info
            file_info.pop("amount")
        return repeats

    @classmethod
    def check_no_reference(cls, siyuan, cache, ):
        miss = {}
        amount = 0
        for file in cache:
            if file["filename"] not in siyuan:
                _file = miss.setdefault(file["filename"], {})
                _file.setdefault(file["etag"], []).append(file["fileId"])
                amount += 1
        for filename, info in miss.items():
            cloud_123_log.info(f"ICloud123.check_no_reference | filename:{filename} info:{info}")
        cloud_123_log.info(f"ICloud123.check_no_reference | amount:{amount}")
        return miss

    @classmethod
    def delete_files(cls, del_ids):
        if Cloud123Config().history_dir_id:
            cls.move_file_to_custom_history_dir(del_ids, Cloud123Config().history_dir_id)
        else:
            cls.move_file_to_trash(del_ids)
        cloud_123_log.info(f"ICloud123.delete_files | quantity_deleted:{len(del_ids)}")

    # endregion Check

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
                cloud_123_log.error(f"ICloud123._MultiUploadFilePart | 校验失败 | md5:{md5} file_size:{file_size} etag:{part['etag']} size:{part['size']} part:{part['partNumber']}")
                raise Exception()
            cloud_123_log.info(f"ICloud123._MultiUploadFilePart | 校验成功 | md5:{md5} file_size:{file_size} etag:{part['etag']} size:{part['size']} part:{part['partNumber']}")
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
                    cloud_123_log.info(f"ICloud123._CheckReplace | 异步校验上传成功 | filename:{filename} times:{i + 1}")
                    break
                await asyncio.sleep(1)
            else:
                cloud_123_log.error(f"ICloud123._CheckReplace | 异步校验上传失败 | filename:{filename} times:{check_times}")

    # endregion private
