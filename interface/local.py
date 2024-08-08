import logging
import posixpath

import setting
from base.interface import IBase
from entity.siyuan import SiyuanBlockResource
from log import get_logger
from tools.file import get_file_info, get_file_info_by_type, async_save_data_to_local_file
from tools.string import unification_file_path

interface_log = get_logger("interface_local")


class ISiyuan(IBase):

    @classmethod
    def is_same_as_record(cls, filename, record_path):
        if posixpath.join(setting.ASSETS_SUB_DIR, filename) == record_path:
            interface_log.debug("ICloud123.already_in | filename")
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
            interface_log.warning(f"SiyuanTools.save_download_resource | info:图片在本地已经存在 img_url:{resource.url} save_path:{save_path}")
        else:
            await async_save_data_to_local_file(save_path, web_file_data)
        interface_log.log(log_level, f"SiyuanTools.save_download_resource | info:图片已成功保存 img_url:{resource.url} save_path:{save_path}")
        return new_url

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
