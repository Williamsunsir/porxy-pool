# Web_ProxyCool_Python_V1

### 介绍

基于fastapi 开发的代理池，用于维护自己购买的短效代理IP，提高代理IP利用率

### 功能描述

- [x] 代理池IP 获取
- [x] 代理IP检测
- [x] 代理IP获取预警
- [x] 代理IP获取
- [x] 压力测试

### 目录结构

```shell
├─api       # 存放代理IP检测
├─configs   # 配置文件
├─service   # service配置文件
├─spider    # 爬虫文件
└─utils     # 工具文件夹
```

### 使用方法

<b>请先在使用之前先进行安装Redis</b>

- 本地使用

```shell
cd /web_proxycool_python_v1
python main.py
```

- 线上部署
  
```shell
mkdir /var/www  # 创建网站根目录，将文件上传到该目录下
cd /var/www/porxy-pool

# 安装依赖
pip install -r requirements.txt

# 将服务添加到systemd中
cp service/proxy-pool.service /etc/systemd/system/

# 设置开机启动
systemctl enable proxy-pool.service

# 启动服务
systemctl start proxy-pool.service
```

### 接口介绍

详细的接口文档可以通过访问 http://127.0.0.1:8000/docs 查看, 因为有token 认证，所以需要在浏览器插件中安装"header'的插件，配置好token请求头才可以正常访问。

- / 
  
  - 获取所有的代理池

- /get_proxy 
  
  - 接口描述：获取代理,name=代理池的名称，count=获取代理的数量（默认为1，最大不超过100）
  
- /get_random_proxy
  
  - 接口描述：随机获取代理,count=获取代理的数量（默认为1，最大不超过100）

#### 二次开发
- 在spider文件夹下创建自己的爬虫文件，集成base_spider.Base_Spider类，实现main方法
```python
from spider.base_spider import Base_Spider

class my_spider(Base_Spider):
    
    def __init__(self):
        self.proxy_auth = ""        # 代理认证信息
        self.proxy_password = ""    # 代理密码
        self.proxy_protocol = ""    # 代理协议:http/socks5
        self.proxy_url = ""         # 代理接口地址
        super().__init__()
        
    def main(self):
        # 1.请求代理接口
        # 2.解析数据
        # 3.存储数据
        pass
```