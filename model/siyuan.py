import typing

from define.base import ResourceType


class ResourceCache(typing.TypedDict):
    filename: str
    image_path: str
    ori_image_path: str
    type: typing.Optional[ResourceType]
