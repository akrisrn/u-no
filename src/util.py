import hashlib
import os
import platform
import re
from threading import Thread

from flask import url_for

from config import uno_ignore_file_list, uno_update_service_name, uno_debug, uno_version, uno_articles_dir_name


# 判断操作系统是否是Windows
def is_windows():
    return True if platform.system() == "Windows" else False


# 获取系统命令分隔符
def get_os_cmd_sep():
    return "&" if is_windows() else ";"


# 获取根目录绝对路径
def get_root_abspath():
    # 根据当前目录的位置进行切割
    return os.path.dirname(os.path.abspath(__file__)).split(__package__)[0]


# 获取文章目录绝对路径
def get_articles_dir_abspath():
    return os.path.join(get_root_abspath(), uno_articles_dir_name)


# 获取静态文件url
def get_static_file_url(filename, have_version=True):
    # 判断是否在url尾部加上版本号
    if have_version:
        return get_version(url_for("static", filename=filename))
    return url_for("static", filename=filename)


# 获取bower包文件url
def get_bower_file_url(filename):
    return url_for("static", filename="bower_components/%s" % filename)


# 根据文件绝对路径计算哈希
def compute_digest_by_abspath(abspath):
    # 判断文件是否存在
    if os.path.isdir(abspath) or not os.path.exists(abspath):
        raise Exception("No such file")
    with open(abspath, 'rb') as file:
        data = file.read()
    return hashlib.sha1(data).hexdigest()


# 根据文件内容计算哈希
def compute_digest_by_data(data):
    return hashlib.sha1(data.encode("utf-8")).hexdigest()


# 获取版本号
def get_version(url):
    # 在调试模式和没有配置版本号的情况下计算文件哈希作为版本号
    file_abspath = os.path.join(get_root_abspath(), url[1:])
    ver = uno_version if uno_version and not uno_debug else compute_digest_by_abspath(file_abspath)
    return "%s?v=%s" % (url, ver)


# 获取重建索引命令
def get_reindex_cmd(dir_abspath=get_articles_dir_abspath()):
    # 移动到文章目录执行git pull
    return get_os_cmd_sep().join(["cd %s" % dir_abspath, "git pull"])


# 获取更新程序命令
def get_update_cmd():
    # 移动到根目录执行git pull，如果不是Windows，尝试重启systemd服务
    restart_cmd = "" if is_windows() else "systemctl restart %s" % uno_update_service_name
    return get_os_cmd_sep().join([get_reindex_cmd(get_root_abspath()), restart_cmd])


# 处理线程，在限制列表下只能同时运行一个线程任务
def handle_thread(thread_limit_list, target):
    # 如果线程结束了，清空限制列表
    if thread_limit_list and not thread_limit_list[0].is_alive():
        thread_limit_list.clear()
    # 如果限制列表为空，加入新任务到限制列表并启动
    if not thread_limit_list:
        thread_limit_list.append(Thread(target=target))
        thread_limit_list[0].start()


# 更新配置文件中的忽略文件列表
def update_config_ignore_file_list(file_path, is_add):
    # 判断是添加还是移除
    if is_add and file_path not in uno_ignore_file_list:
        uno_ignore_file_list.append(file_path)
    elif not is_add and file_path in uno_ignore_file_list:
        uno_ignore_file_list.remove(file_path)
    else:
        return None
    # 读取配置文件数据
    config_abspath = os.path.join(get_root_abspath(), "config.py")
    with open(config_abspath, encoding="utf-8") as config_file:
        config_data = config_file.read()
    # 用新列表替换旧列表
    replace = "%s = %s" % ("uno_ignore_file_list", uno_ignore_file_list)
    config_data = re.sub("%s\s*=\s*\[.*?\]" % "uno_ignore_file_list", replace, config_data)
    # 重新写入配置文件
    with open(config_abspath, "w", encoding="utf-8") as config_file:
        config_file.write(config_data)


# 把字符串拼接参数转义后组进正则表达式
def regexp_join(regexp_str, *args):
    args = list(args)
    # 需要在正则中转义的特殊字符列表
    special_char = ["\\", "$", "(", ")", "*", "+", ".", "[", "]", "?", "^", "{", "}", "|"]
    for i in range(len(args)):
        for char in special_char:
            # 找到特殊字符后加入反斜杠进行转义
            if args[i].find(char) != -1:
                args[i] = args[i].replace(char, "\\" + char)
    return regexp_str % tuple(args)


# 清洗文本，剔除空白、双引号、单引号
def clear_text(text):
    return re.sub("(\s|\"|\')", "", text)
