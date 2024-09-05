import asyncio
import logging
import posixpath
import time
from operator import itemgetter

from api.base import CommonRequest
from api.remote import APICloud123, APIPicGo
from api.siyuan import APISiyuan
from base.interface import IBase
from config import Cloud123Config
from define import SiyuanMessage
from entity.siyuan import SiyuanBlockResource
from log import get_logger
from model.response import Cloud123Response, Cloud123FileInfo
from tools import string
from tools.file import split_file_context, get_file_info

remote_log = get_logger("interface_remote")


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
        return await cls._receive(resource.file, resource.filename, log_level)

    @classmethod
    async def receive_database(cls, urls_info, log_level=logging.DEBUG, toast=True):
        new_urls = {}
        for index, url in urls_info.items():
            if url["path"].startswith(Cloud123Config().save_pre_path):
                new_url = url["path"]
            else:
                new_url = await cls._receive(url["file"], url["filename"], log_level=log_level, toast=toast)
            if new_url:
                new_urls[index] = new_url
            else:
                APISiyuan.push_err_msg(f"上传失败: {url['filename']}")
        return new_urls

    @classmethod
    async def _receive(cls, file, filename, log_level, toast=True):
        if not file:
            return
        response: Cloud123Response = APICloud123.upload_file(file, filename)
        if not response:
            return
        new_path = string.unification_file_path(posixpath.join(Cloud123Config().save_pre_path, filename))
        if response.is_reuse():
            remote_log.log(log_level, f"ICloud123.upload | 上传成功 | filename:{filename} data:{response.data}")
            toast and await APISiyuan.async_push_msg(SiyuanMessage.上传成功_单文件.format(filename=filename))
            return new_path
        file_split_list, chunk_num = split_file_context(file, response.data["sliceSize"])
        is_async, completed = await cls._MultiUploadFilePart(response.data["preuploadID"], file_split_list, chunk_num)
        if not is_async:
            return new_path
        await cls._CheckReplace(response.data["preuploadID"], filename, completed)
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

    # region Check
    @classmethod
    def check_repeat_file(cls, ori_info: list[Cloud123FileInfo]) -> dict[str, dict[str, list[int]]]:
        """
        Returns:
            {filename: {etag: [file_ids]}}
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
            remote_log.info(f"ICloud123.check_no_reference | filename:{filename} info:{info}")
        remote_log.info(f"ICloud123.check_no_reference | amount:{amount}")
        return miss

    @classmethod
    def delete_files(cls, del_ids):
        if Cloud123Config().history_dir_id:
            cls.move_file_to_custom_history_dir(del_ids, Cloud123Config().history_dir_id)
        else:
            cls.move_file_to_trash(del_ids)
        remote_log.info(f"ICloud123.delete_files | quantity_deleted:{len(del_ids)}")

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
                remote_log.error(f"ICloud123._MultiUploadFilePart | 校验失败 | md5:{md5} file_size:{file_size} etag:{part['etag']} size:{part['size']} part:{part['partNumber']}")
                raise Exception()
            remote_log.info(f"ICloud123._MultiUploadFilePart | 校验成功 | md5:{md5} file_size:{file_size} etag:{part['etag']} size:{part['size']} part:{part['partNumber']}")
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
                    remote_log.info(f"ICloud123._CheckReplace | 异步校验上传成功 | filename:{filename} times:{i + 1}")
                    break
                await asyncio.sleep(1)
            else:
                remote_log.error(f"ICloud123._CheckReplace | 异步校验上传失败 | filename:{filename} times:{check_times}")

    # endregion private


class ICloudPicGo(IBase):
    @classmethod
    async def receive(cls, resource: SiyuanBlockResource, log_level=logging.INFO):
        return await cls._receive(resource.true_file_path, log_level)

    @classmethod
    async def receive_database(cls, urls_info, log_level=logging.INFO, toast=True):
        new_urls = {}
        for index, url in urls_info.items():
            new_url = await cls._receive(url["path"], log_level, toast=toast)
            if new_url:
                new_urls[index] = new_url
        return new_urls

    @classmethod
    async def _receive(cls, url: str, log_level, toast=True):
        response = APIPicGo.upload_file(url)
        if not response.success:
            return
        remote_log.log(log_level, f"ICloudPicGo.receive | 上传成功 | new_path:{response.result}")
        toast and await APISiyuan.async_push_msg(SiyuanMessage.上传成功_单列文件.format(filenames=response.result))
        return response.result
