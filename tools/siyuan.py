import posixpath

import setting
from define.base import ResourceType


def convert_image_path(typ, filename) -> str:
    """
    如果是本地路径需要加上默认前缀路径
    Returns:
        实际能访问到的路径
    """
    if typ == ResourceType.SIYUAN:
        return str(posixpath.join(setting.ASSETS_SUB_DIR, filename))
    elif typ in (ResourceType.LOCAL, ResourceType.WEB):
        return filename
