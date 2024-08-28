import enum


class EndPoint(enum.Enum):
    NONE = 0
    CLOUD_123 = 1
    PICGO = 2
    SIYUAN = 3


class ResourceType:
    LOCAL = "local"
    SIYUAN = "siyuan"
    WEB = "web"


class CommonStr:
    HTTP = "http"


class SQLWhere:
    blocks_b = "blocks b"
    sep_and = " and "
    type_in = "b.type in ('p')"
    type_in_f = "b.type in ({types})"
    notebook_id = "b.id='{notebook_id}'"
    root_id = "b.root_id='{root_id}'"
    _id = "b.id='{id}'"
    ial_like = "b.ial like '{like}'"
