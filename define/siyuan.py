class SiyuanMessage:
    下载成功_单文件 = "已下载文件 file:{filename}"
    下载成功_汇总 = "已下载文件 amount:{amount}"
    下载成功_无更改 = "此次操作未下载任何文件"
    上传成功_单文件 = "已上传文件 file:{filename}"
    上传成功_单列文件 = "已上传文件 file:{filenames}"
    上传成功_汇总 = "已上传文件 amount:{amount}"
    上传成功_无更改 = "此次操作未上传任何文件"
    替换图标_无更改 = "没有找到需要替换的图标文档 icon:{icon}"
    替换图标_成功 = "替换图标成功, amount:{amount} old_icon:{old_icon} new_icon:{new_icon}"


class CheckMethod:
    远程重复文件 = "remote repeat"
    远程冗余文件 = "remote not ref"
    本地缺失文件 = "local not ref"


class SiyuanBlockType:
    av = 'av'


class DataBaseType:
    asset = "mAsset"
    file = "file"
    image = "image"
