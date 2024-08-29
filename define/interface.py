class IMsg:
    HELLO_WORLD = "Hello World"
    GOOD_BYE = "Good Bye"
    OK = "Ok"
    BAN = "接口被禁用"
    ILLEGAL_PARAMETER = "非法参数 args:{args}"


class ConfigMsg:
    NOT_INIT = "{name} 配置未初始化"
    ILLEGAL_SOURCE = "来源配置非法"
    CONFIGURATION_ERROR = "配置错误"
    TOKEN_NOT_EXIST = "token 不存在"


class NotebookMethod:
    上传所有文档图片 = "uploadAll"
    下载所有文档图片 = "saveAll"
    下载指定文档图片 = "saveOne"
    上传指定文档图片 = "uploadOne"
    加载文件信息 = "reloadInfo"
    上传指定数据库中的所有资源文件 = "uploadDatabaseResource"

class BlockMethod:
    上传指定块资源 = "uploadBlockOne"
