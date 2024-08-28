from config import SiyuanConfig, PicGoConfig, Cloud123Config
from define.base import EndPoint
from interface.local import ISiyuan
from interface.remote import ICloud123, ICloudPicGo

EndPointMap = {
    EndPoint.CLOUD_123: ICloud123(),
    EndPoint.SIYUAN: ISiyuan(),
    EndPoint.PICGO: ICloudPicGo()
}

EndPointConfigMap = {
    EndPoint.CLOUD_123: Cloud123Config(),
    EndPoint.PICGO: PicGoConfig(),
    EndPoint.SIYUAN: SiyuanConfig()
}
