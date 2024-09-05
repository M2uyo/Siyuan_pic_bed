import datetime
import json
import posixpath

from api.base import CommonAsyncRequest, CommonRequest
from config import Cloud123Config, SiyuanConfig
from config.remote import PicGoConfig
from log import get_logger
from model.api_model import PicGoResponse
from model.response import Cloud123Response, APIErrorMessage
from tools.base import SingletonMeta
from tools.file import get_file_info

api_log = get_logger("api_remote")


def auto_header_response(func):
    def wrapper(cls, *args, **kwargs) -> Cloud123Response:
        token = APICloud123.get_token()
        header = {"Platform": "open_platform", "Authorization": token}
        for i in range(3):  # 超时检查三次
            result = func(cls, *args, header=header, **kwargs)
            callback = None
            if isinstance(result, tuple):
                callback, result = result
            response = Cloud123Response(result.json())
            if response.IsLimit(sleep=0.5):
                continue
            if callback:
                assert callback(response)
            else:
                assert response.Check(_from)
            return response

    @property
    def _from():
        return f"{func.__self__.__class__.__name__}.{func.__name__}"

    return wrapper


class APICloud123(metaclass=SingletonMeta):
    net = CommonRequest()
    _cfg = Cloud123Config()

    @classmethod
    def get_token(cls):
        """
        获取token, 先检查是否已经存在token,
        如果已经存在则检查有效期, 如果在有效期内直接返回, 否则请求接口获取
        """
        if token := _check_token():
            return token
        response = APICloud123.net.Post(
            f"{cls._cfg.api_url}/api/v1/access_token",
            "APICloud123.get_token",
            data=cls._cfg.key_dump(), headers=cls._cfg.default_header
        ).json()
        return _SaveToken(response)

    @classmethod
    @auto_header_response
    def upload_file(cls, file, filename, parent: int = None, header=None):
        if not parent:
            parent = cls._cfg.dir_id
        etag, file_size = get_file_info(file)

        def CallBack(response: Cloud123Response):
            if response.code == 1 and response.message == APIErrorMessage.文件重复:
                remote_file = cls.net.Get(posixpath.join(Cloud123Config().save_pre_path + filename), "APICloud123.upload_file")
                if remote_file and get_file_info(remote_file.content) == (etag, file_size):
                    response.reuse = True
                    return True
                from api.siyuan import APISiyuan
                APISiyuan.push_err_msg(f"远程目录下文件名重复无法创建: {filename}")
                return False
            return response.Check()

        return CallBack, cls.net.Post(
            f"{cls._cfg.api_url}/upload/v1/file/create",
            "APISyncCloud123.upload_file",
            data=json.dumps({
                "parentFileId": parent,
                "Etag": etag,
                "size": file_size,
                "filename": filename,
            }), headers=header
        )

    @classmethod
    @auto_header_response
    def get_slice_upload_url(cls, preuploadID, slice_no, header=None) -> Cloud123Response:
        return cls.net.Post(
            f"{cls._cfg.api_url}/upload/v1/file/get_upload_url",
            "APISyncCloud123.get_slice_upload_url",
            data=json.dumps({
                "preuploadID": preuploadID,
                "sliceNo": slice_no
            }), headers=header
        )

    @classmethod
    @auto_header_response
    def check_upload_integrity(cls, preuploadID, header=None) -> Cloud123Response:
        return cls.net.Post(
            f"{cls._cfg.api_url}/upload/v1/file/list_upload_parts",
            "APISyncCloud123.check_upload_integrity",
            headers=header,
            data=json.dumps({
                "preuploadID": preuploadID,
            })
        )

    @classmethod
    @auto_header_response
    def upload_complete(cls, preuploadID, header=None) -> Cloud123Response:
        return cls.net.Post(
            f"{cls._cfg.api_url}/upload/v1/file/upload_complete",
            "APICloud123.upload_complete",
            headers=header,
            data=json.dumps({
                "preuploadID": preuploadID,
            })
        )

    @classmethod
    @auto_header_response
    def upload_async_result(cls, preuploadID, header=None) -> Cloud123Response:
        return cls.net.Post(
            f"{cls._cfg.api_url}/upload/v1/file/upload_async_result",
            "APICloud123.upload_async_result",
            headers=header,
            data=json.dumps({
                "preuploadID": preuploadID,
            })
        )

    @classmethod
    @auto_header_response
    def get_file_list(cls, limit=100, last_file_id=None, parent=None, header=None) -> Cloud123Response:
        if not parent:  # 不能写在参数列表中给定默认值, 如果在参数列表中给定 则无法读取最新配置
            parent = cls._cfg.dir_id
        params = {
            "parentFileId": parent,
            "Limit": limit,
        }
        if last_file_id:
            params["LastFileId"] = last_file_id
        return cls.net.Get(
            f"{cls._cfg.api_url}/api/v2/file/list",
            "APICloud123.get_file_list",
            params=params,
            headers=header,
        )

    @classmethod
    @auto_header_response
    def move_file_to_trash(cls, file_ids, header=None):
        def Callback(response: Cloud123Response):
            if response.code == 0:
                api_log.debug(f"APICloud123.move_file_to_trash | 删除成功 | file_ids:{file_ids}")
            else:
                api_log.error(f"APICloud123.move_file_to_trash | 删除失败 | {response.info}")
            return response.Check()

        return Callback, cls.net.Post(
            f"{cls._cfg.api_url}/api/v1/file/trash",
            "APICloud123.move_file_to_trash",
            headers=header,
            data=json.dumps({"FileIds": file_ids})
        )

    @classmethod
    @auto_header_response
    def move_file_to_dest_dir(cls, file_ids, dest_dir, header=None):
        def Callback(response: Cloud123Response):
            if response.code == 1 and response.message == APIErrorMessage.文件移动_已在当前文件夹:
                cls.move_file_to_trash(file_ids)
                return True
            if response.code == 0:
                api_log.debug(f"APICloud123.move_file_to_dest_dir | 移动成功 | file_ids:{file_ids}")
            else:
                api_log.error(f"APICloud123.move_file_to_dest_dir | 移动失败 | {response.info}")

            return response.Check()

        return Callback, cls.net.Post(
            f"{cls._cfg.api_url}/api/v1/file/move",
            "APICloud123.move_file_to_dest_dir",
            headers=header,
            data=json.dumps({"FileIds": file_ids, "toParentFileId": dest_dir})
        )


class APISyncCloud123(APICloud123):
    net = CommonAsyncRequest()

    @classmethod
    @auto_header_response
    async def upload_file(cls, file, filename, parent: int = None, header=None):
        if not parent:
            parent = cls._cfg.dir_id
        etag, file_size = get_file_info(file)
        return await cls.net.Post(
            f"{cls._cfg.api_url}/upload/v1/file/create",
            "APISyncCloud123.upload_file",
            data=json.dumps({
                "parentFileId": parent,
                "Etag": etag,
                "size": file_size,
                "filename": filename,
            }), headers=header
        )

    @classmethod
    @auto_header_response
    async def get_slice_upload_url(cls, preuploadID, slice_no, header=None):
        return await cls.net.Post(
            f"{cls._cfg.api_url}/upload/v1/file/get_upload_url",
            "APISyncCloud123.get_slice_upload_url",
            data=json.dumps({
                "preuploadID": preuploadID,
                "sliceNo": slice_no
            }), headers=header
        )

    @classmethod
    @auto_header_response
    async def check_upload_integrity(cls, preuploadID, header=None):
        return await cls.net.Post(
            f"{cls._cfg.api_url}/upload/v1/file/list_upload_parts",
            "APISyncCloud123.check_upload_integrity",
            headers=header,
            data=json.dumps({
                "preuploadID": preuploadID,
            })
        )

    @classmethod
    @auto_header_response
    async def upload_complete(cls, preuploadID, header=None):
        return await cls.net.Post(
            f"{cls._cfg.api_url}/upload/v1/file/upload_complete",
            headers=header,
            data=json.dumps({
                "preuploadID": preuploadID,
            })
        )

    @classmethod
    @auto_header_response
    async def upload_async_result(cls, preuploadID, header=None):
        return await cls.net.Post(
            f"{cls._cfg.api_url}/upload/v1/file/upload_async_result",
            headers=header,
            data=json.dumps({
                "preuploadID": preuploadID,
            })
        )


class APIPicGo(metaclass=SingletonMeta):
    net = CommonRequest()

    # region request
    @classmethod
    def upload_file(cls, pic_path):
        try:
            response = cls.net.Post(PicGoConfig.picgo_url, data=json.dumps({
                "list": [
                    pic_path
                ]
            })).json()
        except Exception as e:
            api_log.error(f"上传失败 | pic_path:{pic_path} err:{e}")
            return PicGoResponse(False, None)
        return cls._on_upload_file(response, pic_path)

    # endregion request

    # region response
    @staticmethod
    def _on_upload_file(response, pic_path):
        if not response["success"]:
            api_log.error(f"{response['message']} | pic_path:{pic_path}")
            return PicGoResponse(False, None)
        return PicGoResponse(True, response["result"][0])
    # endregion response


def _check_token():
    token_save_path = f"{SiyuanConfig().config_path}/token.json"
    if not posixpath.exists(token_save_path):
        return
    with open(token_save_path, 'r') as fp:
        tokenInfo = json.load(fp)["data"]
    expire_time = datetime.datetime.fromisoformat(tokenInfo["expiredAt"])
    if expire_time.timestamp() < (datetime.datetime.now() + datetime.timedelta(hours=1)).timestamp():
        return
    return tokenInfo["accessToken"]


def _SaveToken(response):
    with open(f"{SiyuanConfig().config_path}/token.json", 'w') as fp:
        json.dump(response, fp, indent=4, ensure_ascii=False)
    token = response["data"]["accessToken"]
    expiredAt = response["data"]["expiredAt"]
    api_log.info(f"_SaveToken | 远程获取Token成功 | token:{token} expiredAt:{expiredAt}")
    return token
