import enum


class EndPoint(enum.Enum):
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
    sep = " and "
    type_in = "b.type in ('p', 'l')"
    notebook_id = "b.id='{notebook_id}'"
    root_id = "b.root_id='{root_id}'"
