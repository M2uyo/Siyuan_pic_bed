import hashlib
import os.path
import pathlib
import posixpath
from typing import Optional

import aiofiles

from api.base import CommonAsyncRequest
from config import SiyuanConfig
from define.base import ResourceType, CommonStr
from log import get_logger

file_tools_log = get_logger('file_tools')

common_extension = {"bmp", "jpg", "png", "tif", "gif", "pcx", "tga", "exif", "fpx", "svg", "psd", "cdr", "pcd", "dxf", "ufo", "eps", "ai", "raw", "wmf", "webp", "avif", "apng"}


def get_file_name_and_extension(file_path) -> tuple[str, str, str]:
    """获取文件夹名 文件名 扩展名"""
    dir_name = "/".join(file_path.split("/")[:-1])
    path = pathlib.Path(file_path)
    if path.suffix.lower()[1:] in common_extension:
        file_name = path.stem
        file_extension = path.suffix
    else:
        file_name = f"{path.stem}{path.suffix}"
        file_extension = ""
    return dir_name, file_name, file_extension


def get_file_typ(image_path, text=None) -> Optional[ResourceType]:
    if image_path.startswith(CommonStr.HTTP):
        return ResourceType.WEB
    elif image_path.startswith(SiyuanConfig.assets_sub_dir):
        return ResourceType.SIYUAN
    elif os.path.exists(image_path):
        return ResourceType.LOCAL
    else:
        file_tools_log.error(f"get_file_typ | 不支持的图片类型 | path:{image_path} {text}")


def get_file_info(file) -> tuple[str, int]:
    """
    Returns:
        (str, int): 文件md5  文件长度
    """
    md5_hash = hashlib.md5()
    md5_hash.update(file)
    return md5_hash.hexdigest(), len(file)


async def get_file_info_by_type(file_path, typ):
    file_data = await async_get_file_data(os.path.join(file_path), typ)
    if not file_data:
        return
    return file_data, *get_file_info(file_data)


async def async_get_file_data(file_path, typ=ResourceType.LOCAL):
    if typ == ResourceType.WEB:
        if response := await CommonAsyncRequest.Get(file_path, "async_get_file_data"):
            return await response.read()
    elif typ == ResourceType.LOCAL:
        async with aiofiles.open(file_path, "rb") as f:
            return await f.read()
    elif typ == ResourceType.SIYUAN:
        async with aiofiles.open(os.path.join(SiyuanConfig().data_dir, file_path), "rb") as f:
            return await f.read()


def get_file_path_by_type(file_path, typ):
    if typ == ResourceType.SIYUAN:
        return posixpath.join(SiyuanConfig().data_dir, file_path)
    return file_path


async def async_save_data_to_local_file(file_path, data):
    async with aiofiles.open(file_path, "wb") as f:
        return await f.write(data)


def split_file_context(file, slice_size):
    chunk_numer = 0
    split_file = []
    while data := file[chunk_numer * slice_size: (chunk_numer + 1) * slice_size]:
        chunk_numer += 1
        split_file.append(data)
    return split_file, chunk_numer
