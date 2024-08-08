class IMsg:
    HELLO_WORLD = "Hello World"
    GOOD_BYE = "Good Bye"
    OK = "Ok"
    BAN = "接口被禁用"
    ILLEGAL_PARAMETER = "非法参数 args:{args}"


class ConfigMsg:
    NOT_INIT = "配置未初始化"
    ILLEGAL_SOURCE = "来源配置非法"


class NotebookMethod:
    上传所有文档图片 = "uploadAll"
    下载所有文档图片 = "saveAll"
    下载指定文档图片 = "saveOne"
    上传指定文档图片 = "uploadOne"
    加载文件信息 = "reloadInfo"
