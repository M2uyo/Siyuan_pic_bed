from define.base import EndPoint
from interface.local import ISiyuan
from interface.remote import ICloud123

EndPointMap = {
    EndPoint.CLOUD_123: ICloud123(),
    EndPoint.SIYUAN: ISiyuan()
}
