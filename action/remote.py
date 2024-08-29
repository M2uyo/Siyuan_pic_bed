import json
import posixpath

import aiofiles

import setting
from config import SiyuanConfig
from define.base import EndPoint
from interface import EndPointMap
from log import get_logger
from model.response import Cloud123FileInfo
from tools.base import SingletonMeta

action_log = get_logger("action_remote")


class ActionRemote(metaclass=SingletonMeta):

    @classmethod
    def renew_cache(cls, remote=EndPoint.CLOUD_123) -> list[Cloud123FileInfo]:
        endpoint = EndPointMap[remote]
        files = endpoint.get_all_file()
        with open(posixpath.join(SiyuanConfig().record_path, f"{remote.name.lower()}.json"), "w", encoding=setting.UTF8) as f:
            json.dump(files, f, ensure_ascii=False, indent=4)

        name_md5_map = {
            file["filename"]: file["etag"]
            for file in files
        }

        with open(posixpath.join(SiyuanConfig().record_path, "name_md5_map.json"), "w", encoding=setting.UTF8) as f:
            json.dump(name_md5_map, f, ensure_ascii=False, indent=4)
        action_log.info(f"ActionRemote.renew_cache | finished | remote:{remote} file_amount:{len(files)} map_amount:{len(name_md5_map)}")
        return files

    @classmethod
    async def load_cache(cls, remote=EndPoint.CLOUD_123, renew=False) -> list[Cloud123FileInfo]:
        if renew:
            return cls.renew_cache(remote)
        async with aiofiles.open(posixpath.join(SiyuanConfig().record_path, f"{remote.name.lower()}.json"), "rb") as f:
            return json.loads((await f.read()).decode(setting.UTF8))  # 假设文件是以utf-8编码

    @classmethod
    async def check_repeat(cls, remote=EndPoint.CLOUD_123, renew_remote=False) -> dict[str, dict[str, list[int]]]:
        """
        Returns:
             {filename: {etag: [file_ids]}}
        """
        remote_data = await cls.load_cache(remote=remote, renew=renew_remote)
        return EndPointMap[remote].check_repeat_file(remote_data)

    @classmethod
    def del_repeat(cls, del_info, remote=EndPoint.CLOUD_123, save_amount=1):
        """
        Args:
            save_amount (int): 保存重复的副本数量
            del_info (dict): {filename: {etag: [file_ids]} }
        """
        action_log.info(f"ActionRemote.del_repeat | remote:{remote} save_amount:{save_amount}")
        true_del_ids = []
        for filename, info in del_info.items():
            for etag, repeat_ids in info.items():
                if etag == "amount":  # 跳过计数key 待删除
                    continue
                if save_amount:
                    wait_del_ids = repeat_ids[:-save_amount]
                else:
                    wait_del_ids = repeat_ids
                if not wait_del_ids:
                    action_log.warning(f"ActionRemote.del_repeat | No files available for deletion | save_amount:{save_amount} filename:{filename} etag:{etag} ids:{wait_del_ids}")
                    continue
                for _id in wait_del_ids:
                    action_log.info(f"ActionRemote.del_repeat | filename:{filename} file_id:{_id} etag:{etag}")
                true_del_ids.extend(wait_del_ids)
        endpoint = EndPointMap[remote]
        endpoint.delete_files(true_del_ids)
