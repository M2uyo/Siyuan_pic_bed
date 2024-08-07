import re

import setting
from setting import num_tag


def remove_list_prefix(text: str):
    """
    1.1.1 Python编程  ->  Python编程
    """
    list_prefix = text.split()[0]
    if list_prefix.replace(".", "").isdigit():
        return " ".join(text.split()[1:])
    return text


def replace_special_characters(text: str):
    return re.sub(r'_+', '_', re.sub(setting.special_replace_pattern, '_', text))


def add_prefix(text: str, prefix: str):
    if prefix and not text.startswith(prefix + "_"):
        return f"{prefix}_{text}"
    return text


def unification_file_path(file_path):
    return file_path.strip().replace("\\", "/")


def get_true_file_name(filename):
    """
    将文件名和数字标识分开
    Python-1  ->  ('python', 1)
    """
    number = 0
    if num_tag in filename:
        tmp = filename.split(num_tag)
        _number = tmp[-1]
        if _number.isdigit() and int(_number) < 100:
            filename = num_tag.join(filename.split(num_tag)[:-1])
            number = _number
    return filename.replace(num_tag, "_"), int(number)


def get_suffix_by_num(number):
    return f"{num_tag}{number}" if number != 0 else ""
