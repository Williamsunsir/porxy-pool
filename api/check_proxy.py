#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
# @FileName  :check_proxy.py
# @Time      :2023/9/6 20:20
# @Author    :William
# desc       :
'''
import json

import requests
from concurrent.futures import ThreadPoolExecutor,as_completed
from configs.settings import logger,redis_client


def check_proxy(redis_key,proxy):
    try:
        url = "https://www.baidu.com"
        response = requests.head(url,proxies=proxy,timeout=(3,6))
        if response.status_code == 200:
            return True,redis_key
        return False,redis_key
    except Exception as e:
        # logger.debug(e)
        return False,redis_key


def check_main():
    try:
        # 从redis中获取所有的代理
        keys = redis_client.keys("proxy:*")
        if not keys:
            logger.warning("暂无代理！")
            return
        proxys = redis_client.mget(keys)
        assert proxys, "获取key值失败！"
        logger.debug(f"共获取到{len(proxys)}个代理！")
        all_task = []
        with ThreadPoolExecutor(max_workers=20) as executor:
            for proxy in proxys:
                proxy = str(proxy,encoding="utf-8")
                proxy = json.loads(proxy)
                task_name = proxy["task_name"]
                proxy_ip = proxy["proxy_ip"]
                proxy_port = proxy["proxy_port"]
                proxy_protocol = proxy["proxy_protocol"]
                proxy_auth = proxy["proxy_auth"]
                proxy_password = proxy["proxy_password"]
                redis_key = f"proxy:{task_name}:{proxy_ip}"
                p = f"{proxy_auth}:{proxy_password}@{proxy_ip}:{proxy_port}"
                pproxy_dict = {
                    "http":f"{proxy_protocol}://{p}",
                    "https":f"{proxy_protocol}://{p}",
                }
                all_task.append(executor.submit(check_proxy,redis_key,pproxy_dict))
            # 删除失效的代理
            result = [item.result() for item in as_completed(all_task)]
            lapse_keys = [item[1] for item in result if not item[0]]
            [redis_client.delete(item) for item in lapse_keys]
            logger.success(f"共删除：{len(lapse_keys)}个失效代理！")
    except Exception as e:
        logger.error(f"检测代理失败，错误信息：{e}")

if __name__ == '__main__':
    check_main()