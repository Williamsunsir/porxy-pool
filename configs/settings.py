#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
# @FileName  :settings.py
# @Time      :2023/9/6 1:24
# @Author    :William
# desc       :
'''
import os
import redis
from loguru import logger


# 配置接口认证
web_author = ["qq123456"]

Base_Path = os.path.dirname(os.path.abspath(__file__))
# 配置日志
logger.add(
    os.path.join(Base_Path, "../logs", "{time:YYYY-MM-DD}.log"),
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {function}-{line}-{module}-{name}-{process}-{thread} | {message}",
    rotation="00:00",
    retention="10 days",
    encoding="utf-8",
    enqueue=True,
)

# 配置redis
redis_config = {
    "host":"",
    "port":6379,
    "db":0,
    "password":"",
}
redis_client = redis.Redis(**redis_config)


# 配置你需要开启的任务
task_list = [
    ("spider.zhandaye","Zhandaye"),
]

# 填写要进行提醒的群机器人的webhook
notice = {
    "feishu_webhook":"",
    "qywx_webhook":"",
}