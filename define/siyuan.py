class SiyuanMessage:
    下载成功_单文件 = "已下载文件 file:{filename}"
    下载成功_汇总 = "已下载文件 amount:{amount}"
    下载成功_无更改 = "此次操作未下载任何文件"
    上传成功_单文件 = "已上传文件 file:{filename}"
    上传成功_汇总 = "已上传文件 amount:{amount}"
    上传成功_无更改 = "此次操作未上传任何文件"


class CheckMethod:
    远程重复文件 = "remote repeat"
    远程冗余文件 = "remote not ref"
    本地缺失文件 = "local not ref"
