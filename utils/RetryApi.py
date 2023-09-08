#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
# @FileName  :zhandaye.py
# @Time      :2023/9/6 18:31
# @Author    :William
# desc       :
'''

import time
from loguru import logger

def retry(max_retries, delay=0, default_result=None, log_message=''):
    """
    重试装饰器
    :param max_retries: 最大重试次数
    :param delay: 重试间隔时间（秒）
    :param default_result: 默认返回结果
    :param log_message: 日志信息
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 1
            while retries <= max_retries:
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    retries += 1
                    logger.error(f"{func.__name__}，最大重试次数：{max_retries}，当前：{retries}")
                    if log_message:
                        if retries == max_retries:
                            logger.exception(f"{log_message};{func.__name__};{e}")
                        else:
                            logger.error(f"{log_message};{func.__name__};{e}")
                    if retries < max_retries:
                        time.sleep(delay)
            return default_result
        return wrapper
    return decorator

if __name__ == '__main__':
    @retry(3, default_result="Error")
    def test():
        print(1 + "1")
    print(test())