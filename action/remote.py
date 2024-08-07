import json
import posixpath

import setting
from interface.remote import ICloud123
from tools.base import SingletonMeta


class ActionCloud123(metaclass=SingletonMeta):

    @classmethod
    def get_file_list_info(cls):
        files = ICloud123.cloud_123_get_all_file()
        with open(posixpath.join(setting.RECORD_PATH, "cloud_123.json"), "w", encoding="utf8") as f:
            json.dump(files, f, ensure_ascii=False, indent=4)

        name_md5_map = {
            file["filename"]: file["etag"]
            for file in files
        }

        with open(posixpath.join(setting.RECORD_PATH, "name_md5_map.json"), "w", encoding="utf8") as f:
            json.dump(name_md5_map, f, ensure_ascii=False, indent=4)
        return files
