#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
# @FileName  :Proxy.py
# @Time      :2023/9/8 17:14
# @Author    :William
# desc       :
'''
import requests
from loguru import logger

class Proxy:

    def __init__(self):
        self.base_url = ""
        self.headers = {"token":""}

    def requests2(self,url,method="get",**kwargs):
        error_msg = ""
        for x in range(3):
            try:
                response = requests.request(method,url,**kwargs)
                if response.status_code != 200:
                    return
                return response
            except Exception as e:
                error_msg = str(e)
        logger.error(f"请求代理接口失败，错误信息：{error_msg}")
        return

    def get_proxy(self,name=None,count=1):
        if name==None:
            url = f"{self.base_url}/get_random_proxy?count={count}"
        else:
            url = f"{self.base_url}/get_proxy?name={name}&count={count}"
        response = self.requests2(url,headers=self.headers,timeout=(3,6))
        if not response:
            return
        data = response.json()
        if data["code"] != 200:
            logger.error(f"获取代理失败，错误信息：{data['message']}")
            return

        proxys = data["data"]
        proxys_list = []
        for proxy in proxys:
            proxy_ip = proxy["proxy_ip"]
            proxy_port = proxy["proxy_port"]
            proxy_protocol = proxy["proxy_protocol"]
            proxy_auth = proxy["proxy_auth"]
            proxy_password = proxy["proxy_password"]
            auth = f"{proxy_auth}:{proxy_password}@" if proxy_auth else ""
            proxy_url = f"{proxy_protocol}://{auth}{proxy_ip}:{proxy_port}"
            proxys_list.append({
                "http":proxy_url,
                "https":proxy_url,
            })
        if count == 1 and proxys_list:
            return proxys_list[0]
        return proxys_list

if __name__ == '__main__':
    from collections import Counter
    from concurrent.futures import ThreadPoolExecutor,as_completed
    def test():
        try:
            url = "https://www.baidu.com"
            proxy_obj = Proxy()
            proxy = proxy_obj.get_proxy()
            response = proxy_obj.requests2(url,method="get",proxies=proxy,timeout=(3,6))
            if not response:
                return False
            response.encoding = response.apparent_encoding
            if response.status_code != 200:
                return False
            return True
        except Exception as e:
            logger.error(f"测试代理失败，错误信息：{e}")
            return False

    max_workers = 20
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_list = []
        for x in range(20):
            future = executor.submit(test)
            future_list.append(future)
        result = [future.result() for future in as_completed(future_list)]
    result = Counter(result)
    logger.debug(f"测试结果：{result}")

