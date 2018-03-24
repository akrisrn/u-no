## 依赖安装

```
pip install -r requirements.txt
```

```
bower install
```

## 运行

- 复制`config-simple.py`为`config.py`并填入相关配置

```
python uno.py
```

## 部署（VirtualEnv + uWSGI + systemd + Nginx）

### VirtualEnv

```
pip install virtualenv
virtualenv --no-site-packages .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### uWSGI + systemd

#### uWSGI

- 根据实际情况修改`uno-uwsgi.ini`文件

```
pip install uwsgi
```

#### systemd

- 根据实际情况修改`uno-uwsgi.service`文件

```
cp uno-uwsgi.service /usr/lib/systemd/system/
```

#### 启动服务

```
systemctl start uno-uwsgi
# 加入开机启动
systemctl enable uno-uwsgi
```

### Nginx

- 根据实际情况修改`uno-nginx.conf`文件

```
cp uno-nginx.conf /etc/nginx/conf.d/
```
