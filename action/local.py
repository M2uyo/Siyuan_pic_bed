import json
import posixpath
from operator import itemgetter

import setting
from action.siyuan import renew_cache
from interface.remote import ICloud123
from log import get_logger
from tools.base import SingletonMeta

action_log = get_logger("action_check")


class CheckAction(metaclass=SingletonMeta):
    @classmethod
    def check_miss_in_remote(cls, **kwargs):
        """查看云端缺失文件"""
        cloud_123, siyuan = cls.load_cache()
        siyuan = [s["name"] for s in siyuan.values()]
        remote = [s["filename"] for s in cloud_123]
        miss = []
        for name in siyuan:
            if name not in remote:
                miss.append(name)
        action_log.info(f"CheckAction.check_miss_in_remote | amount:{len(miss)}")
        if len(miss):
            for filename in miss:
                action_log.info(f"CheckAction.check_miss_in_remote | filename:{filename}")
        return miss

    @classmethod
    def load_cache(cls):
        with open(posixpath.join(setting.RECORD_PATH, "cloud_123.json"), "r", encoding="utf8") as f:
            cloud_123 = json.load(f)
        with open(posixpath.join(setting.RECORD_PATH, "siyuan.json"), "r", encoding="utf8") as f:
            siyuan = json.load(f)
        return cloud_123, siyuan

    @classmethod
    async def check_repeat_cloud_123(cls, cloud_123, delete=False, save_amount=1, renew_siyuan=False):
        """
        Returns:
            del_info:
                 {filename: {etag: [file_ids]}, amount: 同名文件的数量}
        """
        if cache := await renew_cache(renew_siyuan, not cloud_123):
            if "cloud_123" in cache:
                cloud_123 = cache["cloud_123"]

        files = {}
        for file in sorted(cloud_123, key=itemgetter("fileID"), reverse=True):
            _file = files.setdefault(file["filename"], {})
            _file.setdefault(file["etag"], []).append(file["fileID"])
            _file.setdefault("amount", 0)
            _file["amount"] += 1
        repeats = {}
        for file, ids in files.items():
            if ids["amount"] > 1:
                repeats[file] = ids
            ids.pop("amount")
        if delete:
            cls.del_repeat_cloud_123(repeats, save_amount=save_amount)
        return repeats

    @classmethod
    async def check_no_ref_resource_in_cloud_123(cls, delete=False, save_amount=0, renew_siyuan=False, renew_cloud_123=False, show=True):
        """
        查看本地未引用的云盘资源
        Returns:
            (del_info): 删除信息, 总的无引用数量
        """
        cloud_123, siyuan = cls.load_cache()
        siyuan = [s["name"] for s in siyuan.values()]
        if cache := await renew_cache(renew_siyuan, renew_cloud_123):
            if "siyuan" in cache:
                siyuan = cache["siyuan"]
            if "cloud_123" in cache:
                cloud_123 = cache["cloud_123"]

        miss = {}
        amount = 0
        for file in cloud_123:
            if file["filename"] not in siyuan:
                _file = miss.setdefault(file["filename"], {})
                _file.setdefault(file["etag"], []).append(file["fileID"])
                amount += 1
        action_log.info(f"无引用资源数量 | amount:{amount}")
        if amount > 0:
            for filename, info in miss.items():
                action_log.info(f"无引用资源 | filename:{filename} info:{info}")
        if delete:
            cls.del_repeat_cloud_123(miss, save_amount=save_amount)
        if show:
            action_log.info(miss)
        return miss

    @classmethod
    def del_repeat_cloud_123(cls, del_info, save_amount=1):
        """
        Args:
            save_amount (int): 保存重复的副本数量
            del_info (dict): {filename: {etag: [file_ids]} }
        """
        true_del_ids = []
        for filename, info in del_info.items():
            for etag, repeat_ids in info.items():
                if etag == "amount":  # 跳过计数key
                    continue
                if save_amount:
                    wait_del_ids = repeat_ids[:-save_amount]
                else:
                    wait_del_ids = repeat_ids
                if not wait_del_ids:
                    action_log.warning(f"没有可删除的文件 | save_amount:{save_amount} filename:{filename} etag:{etag} ids:{wait_del_ids}")
                else:
                    for _id in wait_del_ids:
                        action_log.info(f"计划删除 | save_amount:{save_amount} filename:{filename} file_id:{_id} etag:{etag}")
                    true_del_ids.extend(wait_del_ids)
        if setting.cloud_123_history_dir_id:
            ICloud123.move_file_to_custom_history_dir(true_del_ids, setting.cloud_123_history_dir_id)
        else:
            ICloud123.move_file_to_trash(true_del_ids)
