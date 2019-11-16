# RefluxPipe
----
一款基于`Django2.2`开发的监控HTTP访问记录和DNS解析记录的工具。

[![License](https://img.shields.io/badge/license-GPLv3-red.svg)](https://github.com/faz658026/RefluxPipe/blob/master/LICENSE) [![Python 3.7](https://img.shields.io/badge/python-3.7-yellow.svg)](https://www.python.org/) [![Mongodb 4.0](https://img.shields.io/badge/mongodb-4.0-blue.svg)](https://www.mongodb.com/)  [![Redis 5.0](https://img.shields.io/badge/redis-5.0-red.svg)](https://redis.io/)  
----------
**本工具只做日志记录，无攻击性行为。请使用者遵守《[中华人民共和国网络安全法](http://www.npc.gov.cn/npc/xinwen/2016-11/07/content_2001605.htm)》，勿将本系统用于非授权的测试，作者不负任何连带法律责任。**
## 安装指南
----
### 1.获取源码

```shell
$ git clone git@github.com:faz658026/RefluxPipe.git
```
### 2.安装依赖

```shell
$ cd RefluxPipe
$ pip install -r requirements.txt
```

### 3.安装数据库

RefluxPipe使用mongodb存储日志数据，使用redis缓存websocket数据。如已安装可以略过。

\# Ubuntu 18.04 (Bionic)

```shell
$ apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 9DA31620334BD75D9DCB49F368818C72E52529D4
$ echo "deb [ arch=amd64 ] https://repo.mongodb.org/apt/ubuntu bionic/mongodb-org/4.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-4.0.list
$ apt install -y mongodb-org redis
```

### 4.域名以及服务器准备
您需要两个域名，一个域名作为NS服务器域名，另一个则用来解析域名。

简单的来说，NS服务器域名需要配置两个A记录指向您的服务器IP。

例如:
>设置`ns1.a.cn`的A记录为`1.1.1.1（您的服务器IP）`

>设置`ns2.a.cn`的A记录为`1.1.1.1（您的服务器IP）`

另一个域名的NS记录设定为`ns1.a.cn`和`ns2.a.cn`。

这样的话，如果其他人想解析你的的域名就会访问`ns1.a.cn`和`ns2.a.cn`所配置的ip地址。

**当然，如果您在完全隔离的网络进行渗透测试，完全可以把本系统搭建在内网，只需要两个域名和一台服务器 :)**

### 5.修改配置文件

修改`RefluxPipe/RefluxPipe/setting.py`文件的配置:

```python
# 在第47行修改您的redis数据库配置
"hosts": ["redis://127.0.0.1:6379/0"]

# 在第87-94行修改您的mongodb数据库配置
'ENGINE': 'djongo',
'ENFORCE_SCHEMA': False,
'NAME': 'RefluxPipe',
'HOST': '127.0.0.1',
'PORT': 27017,
'USER': '',
'PASSWORD': '',
'AUTH_SOURCE': '',

# 在第142行修改您的服务器外网ip
SERVER_IP = "127.0.0.1"

#在第144行填写您的解析域名
SERVER_DOMAIN = "yourdomain.com"
```

### 6.运行服务

```shell
# 第一次运行请初始化数据库
$ python manage.py makemigrations
$ python manage.py migrate

# 运行
$ python manage.py runserver 0.0.0.0:80 --insecure
```

## 使用帮助
----
服务运行后，访问`http://registe.{您的域名}:端口号/admin/`进入注册页面。

>首次注册邀请码为`admin`，默认为管理员权限（仅可使用一次）

注册成功之后，再次登录请访问`http://{您设置的别名}.{您的域名}:端口号/admin/`进入后台。

## 问题相关
----
有任何问题欢迎提Issue，或者将问题描述发送至我邮箱 `faz658026#gmail.com` :)

