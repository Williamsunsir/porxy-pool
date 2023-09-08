#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
# @FileName  :main.py
# @Time      :2023/9/6 1:35
# @Author    :William
# desc       :
'''
import json
import random
import atexit
import uvicorn
import datetime
import socket
import importlib
from fastapi import FastAPI,Request
from fastapi.responses import JSONResponse
from collections import Counter
from api.check_proxy import check_main
from apscheduler.schedulers.background import BackgroundScheduler
from configs.settings import web_author,logger,redis_client,task_list

scheduler = BackgroundScheduler()
scheduler.start()
atexit.register(lambda: scheduler.shutdown())
app = FastAPI(title='Proxy-Cool', description='Proxy-Cool API', version='0.1.0')

@app.middleware("http")
async def auth(request: Request, call_next):
    token = request.headers.get("token","")
    if token not in web_author:
        return JSONResponse({"code":401,'message': '认证失败'})
    response = await call_next(request)
    return response

@app.get('/')
def index():
    try:
        keys = redis_client.scan(0,"proxy:*:*",count=100000)[1]
        keys = [str(item.decode('utf-8')).rsplit(":",1)[0].replace("proxy:","") for item in keys]
        element_count = dict(Counter(keys))
        return {"code":200,'message': 'success','data':element_count}
    except Exception as e:
        logger.exception(f"获取代理名称失败，错误信息：{e}")
        return {"code":500,'message': '获取代理名称失败'}

@app.get('/get_proxy',summary="接口描述：获取代理,name=代理池的名称，count=获取代理的数量（默认为1，最大不超过100）")
def get_proxy(name:str,count:int=1):
    try:
        count = 100 if count > 100 else count if count > 0 else 1
        keys = redis_client.scan(0, f"proxy:{name}:*", count=count)[1][:count]
        assert keys, "代理为空！"
        proxy_list = redis_client.mget(keys)
        proxy_list = [json.loads(str(item.decode('utf-8'))) for item in proxy_list]
        return {"code":200,'message': 'success','data':proxy_list}
    except AssertionError as e:
        logger.error(e)
        return {"code":101,'message': e}
    except Exception as e:
        logger.exception(f"获取代理失败，错误信息：{e}")
        return {"code":102,'message': f'获取代理失败{e}'}


@app.get('/get_random_proxy',summary="接口描述：随机获取代理,count=获取代理的数量（默认为1，最大不超过100）")
def get_random_proxy(count:int=1):
    try:
        count = 100 if count > 100 else count if count > 0 else 1
        keys = redis_client.scan(0, f"proxy:*:*", count=count*10)[1][:count]
        random_keys = random.sample(keys,count)
        proxy_list = redis_client.mget(random_keys)
        proxy_list = [json.loads(str(item.decode('utf-8'))) for item in proxy_list]
        return {"code": 200, 'message': 'success', 'data': proxy_list}
    except AssertionError as e:
        logger.error(e)
        return {"code": 101, 'message': e}
    except Exception as e:
        logger.exception(f"获取代理失败，错误信息：{e}")
        return {"code": 102, 'message': f'获取代理失败{e}'}

if __name__ == '__main__':

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("127.0.0.1", 47200))
    except socket.error:
        print("!!!scheduler already started, DO NOTHING")
    else:
        try:
            now_date = datetime.datetime.now()
            for task in task_list:
                model_name = task[0]
                class_name = task[1]
                module = importlib.import_module(model_name)
                class_object = getattr(module, class_name)
                scheduler.add_job(class_object().main, "cron", second="*/12", id=class_name,next_run_time=now_date)
            scheduler.add_job(check_main,"cron",second="*/10",id="check_proxy",next_run_time=now_date)
        except Exception as e:
            logger.exception(f"定时任务添加失败，错误信息：{e}")

    uvicorn.run(app, host='0.0.0.0', port=8000)