#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
# @FileName  :base_spider.py
# @Time      :2023/9/6 18:26
# @Author    :William
# desc       :
'''
import datetime
import json

import requests
from typing import List
from utils.task_remind import qywx_robot,feishu_robot
from configs.settings import logger,redis_client,notice

class Base_Spider:

    def __init__(self):
        task_name = self.__class__.__name__
        self.task_name = str(task_name).lower()
        self.task_key = f"proxy:{self.task_name}"
        assert self.task_name != "Base_Spider", "请不要直接使用父类的方法"

        self.is_auth = self.is_auth if hasattr(self,"is_auth") else True
        self.proxy_auth = self.proxy_auth if hasattr(self,"proxy_auth") else ""
        self.proxy_password = self.proxy_password if hasattr(self,"proxy_password") else ""
        self.proxy_url = self.proxy_url if hasattr(self,"proxy_url") else ""
        self.proxy_protocol = self.proxy_protocol if hasattr(self,"proxy_protocol") else ""
        assert self.proxy_protocol in ["http","socks5"], "代理协议错误！"
        if self.is_auth:
            assert self.proxy_auth != "" and self.proxy_password != "", "请设置代理的账号密码, 或者关闭代理认证！"
        assert self.proxy_url != "", "请设置代理接口的url"

    def create_data(self,**kwargs):
        try:
            create_time = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            proxy_ip = kwargs.get("proxy_ip","")
            proxy_port = kwargs.get("proxy_port","")
            assert proxy_ip, "请设置代理ip！"
            assert proxy_port and isinstance(proxy_port,int), "请设置代理端口！"
            return {
                "task_name":self.task_name,
                "create_time":create_time,
                "proxy_ip":proxy_ip,
                "proxy_port":proxy_port,
                "proxy_protocol":self.proxy_protocol,   # http/socks5
                "proxy_auth":self.proxy_auth,
                "proxy_password":self.proxy_password,
            }
        except Exception as e:
            logger.error(f"创建数据失败，错误信息：{e}")
            return None

    def save_data(self,data:List[dict]):
        try:
            # 如果当数据为空时，会进行计数，当计数到达3次时，会发送飞书或者企业微信的提醒功能
            if not data:
                num = redis_client.get(self.task_key)
                num = 0 if not num else int(num)
                redis_client.set(self.task_key,num+1)
                if num >= 3:
                    for name,url in notice.items():
                        if name == "qywx_webhook" and url:
                            qywx_robot(url,f"代理池任务：{self.task_name}，爬取数据为空！")
                        elif name == "feishu_webhook" and url:
                            feishu_robot(url,f"代理池任务：{self.task_name}，爬取数据为空！")
                    redis_client.delete(self.task_key)

            # 添加任务队列
            redis_pip = redis_client.pipeline()
            [redis_pip.set(self.task_key+f":{x.get('proxy_ip')}", json.dumps(x, ensure_ascii=False)) for x in data]
            redis_pip.execute()
            redis_client.delete(self.task_key)
        except Exception as e:
            logger.error(f"保存数据失败，错误信息：{e}")
            return

    def requests2(self,url,method="get",**kwargs):
        for x in range(3):
            try:
                if method == "get":
                    response = requests.get(url,**kwargs)
                elif method == "post":
                    response = requests.post(url,**kwargs)
                else:
                    raise Exception("不支持的请求方式")
                return response
            except Exception as e:
                logger.error(f"请求失败，错误信息：{e}")
                continue
        return None

    def main(self):
        # 1.请求代理接口
        # 2.解析数据
        # 3.存储数据
        pass