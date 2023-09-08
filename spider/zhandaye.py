#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
# @FileName  :zhandaye.py
# @Time      :2023/9/6 18:31
# @Author    :William
# desc       :
'''

from spider.base_spider import Base_Spider
from configs.settings import logger


class Zhandaye(Base_Spider):

    def __init__(self):
        self.proxy_auth = ""
        self.proxy_password = ""
        self.proxy_protocol = ""
        self.proxy_url = ""
        super().__init__()

    def main(self):
        try:
            response = self.requests2(self.proxy_url)
            if response is None:
                return
            proxys = []
            data = response.json()
            logger.debug(data)
            proxy_list = data["data"]["proxy_list"]
            for item in proxy_list:
                proxy_ip = item.get("ip","")
                proxy_port = item.get("port", "")
                data = self.create_data(proxy_ip=proxy_ip,proxy_port=proxy_port)
                if not data:
                    continue
                proxys.append(data)
            # 代理存储
            self.save_data(proxys)
            logger.success(f"{self.task_name} 任务执行成功！")
        except Exception as e:
            logger.error(f"{self.task_name} 任务执行失败，错误信息：{e}")

if __name__ == '__main__':
    zhandaye = Zhandaye()
    zhandaye.main()