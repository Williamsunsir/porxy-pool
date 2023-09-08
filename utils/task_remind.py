#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
# @FileName  :task_remind.py
# @Time      :2023/9/6 19:03
# @Author    :William
# desc       :
'''
import requests
from utils.RetryApi import retry
from configs.settings import logger

@retry(2)
def qywx_robot(url,text,type="text"):
    try:
        assert type in ["text","markdown"], "消息类型错误！"
        json_data = {
            "msgtype": type,
            type: {
                "content": text
            }
        }
        response = requests.post(url,json=json_data,timeout=(6,10))
        assert response.status_code == 200,f"企业微信机器人发送消息失败:{response.text}"
        return True
    except Exception as e:
        logger.debug(e)
        return False

@retry(2)
def feishu_robot(url,text,type="text"):
    json_data = {
        "msg_type": "text",
        "content": {
            "text": text
        }
    }
    response = requests.post(url,json=json_data,timeout=(6,10))
    assert response.status_code == 200,f"飞书机器人发送消息失败:{response.text}"
    return True

if __name__ == '__main__':
    from configs.settings import notice
    for k,v in notice.items():
        if k == "qywx_webhook":
            result = qywx_robot(v,"测试企业微信机器人")
            print(result)
        elif k == "feishu_webhook":
            feishu_robot(v,"测试飞书机器人")
