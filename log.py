"""
日志处理
"""

import logging

import setting

file_handlers = {}


def get_logger(log_name):
    if logger := file_handlers.get(log_name):
        return logger
    # 创建一个日志记录器
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.DEBUG)

    # 创建一个控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # 创建一个文件处理器
    file_handler = logging.FileHandler(f'{setting.log_path}/{log_name}.log', encoding=setting.UTF8)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter('[%(asctime)s][%(levelname)s] %(name)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(file_formatter)

    # 创建一个格式器并为控制台处理器和文件处理器设置不同的格式
    console_formatter = logging.Formatter('%(asctime)s][%(levelname)s] - %(message)s')
    console_handler.setFormatter(console_formatter)

    # 将处理器添加到日志记录器
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    file_handlers[log_name] = logger
    return logger


def init_console_logger():
    log_name = "console out"
    logger = logging.getLogger(log_name)
    # 创建一个控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    # 创建一个格式器并为控制台处理器和文件处理器设置不同的格式
    console_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    # 将处理器添加到日志记录器
    logger.addHandler(console_handler)
    file_handlers[log_name] = logger
    return logger


_console_log = init_console_logger()


def just_console(*args, sep=" ", end="", **kwargs):
    def format_kwargs(ks):
        ret = []
        for k, v in ks.items():
            ret.append(f"{k}: {v}")
        return ret

    str_args = f"{sep}".join(map(str, args))
    str_kwargs = f"{sep}".join(format_kwargs(kwargs))
    _console_log.info(f"{str_args} {str_kwargs}{end}")
