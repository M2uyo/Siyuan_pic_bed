from typing import TypedDict, NotRequired, Optional


class FileInfo(TypedDict):
    text_image_path: str  # 文本中的文件路径
    image_path: str  # 原始的文件路径 (替换了空格后的)
    name: str  # 新的文件名称
    typ: str  # 原始的保存类型
    ori: NotRequired[str]  # 原始的文本, 替换原始路径变为新路径, 并保存到文档中


class UploadFileRes(TypedDict):
    new_path: str  # 新的文件路径
    completed: bool  # 是否上传完毕
    is_async: bool  # 是否需要异步查询上传结果。false为无需异步查询,已经上传完毕。true 为需要异步查询上传结果。
    preuploadID: str  # 预上传ID


class UploadFileInfo(TypedDict):
    info: FileInfo
    res: Optional[UploadFileRes]


CustomRecordT = dict[str, str]  # 块ID: 文件路径
