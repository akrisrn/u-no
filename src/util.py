import hashlib
import os
import platform
import re
from threading import Thread

from flask import url_for

from config import uno_ignore_file_list, uno_update_service_name, uno_debug, uno_version, uno_articles_dir_name, \
    uno_use_cdn


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
def clean_text(text):
    return re.sub("(\s|\"|\')", "", text)


# 获取bower包文件url
def get_bower_file_url(filename):
    return url_for("static", filename="bower_components/%s" % filename)


# 获取cdnjs上文件url
def get_cdnjs_file_url(filename):
    return "https://cdnjs.cloudflare.com/ajax/libs/" + filename


# 根据是否使用cdn选择本地bower路径或cdnjs链接
def get_static_lib_url(name):
    return {
        'pace.js': get_bower_file_url("PACE/pace.min.js"),
        'pace.css': get_bower_file_url("PACE/themes/blue/pace-theme-flash.css"),
        'mathjax.js': get_bower_file_url("MathJax/MathJax.js") + "?config=TeX-MML-AM_CHTML",
        'raphael.js': get_bower_file_url("raphael/raphael.min.js"),
        'underscore.js': get_bower_file_url("underscore/underscore-min.js"),
        'sequence-diagram.js': get_bower_file_url("js-sequence-diagrams/dist/sequence-diagram-min.js"),
        'flowchart.js': get_bower_file_url("flowchart/release/flowchart.min.js"),
        'jquery.js': get_bower_file_url("jquery/dist/jquery.min.js"),
        'jquery-tablesorter.js': get_bower_file_url("tablesorter/dist/js/jquery.tablesorter.min.js"),
        'jquery-raty.js': get_bower_file_url("raty/lib/jquery.raty.js"),
        'jquery-raty.css': get_bower_file_url("raty/lib/jquery.raty.css"),
        'github-markdown.css': get_bower_file_url("github-markdown-css/github-markdown.css"),
        'buttons.css': get_bower_file_url("Buttons/css/buttons.min.css"),
        'font-awesome.css': get_bower_file_url("Font-Awesome/web-fonts-with-css/css/fontawesome-all.min.css"),
        'source-code-pro.ttf': get_bower_file_url("sourcecodepro-googlefont/SourceCodePro-Regular.ttf"),
    }[name] if not uno_use_cdn else {
        'pace.js': get_cdnjs_file_url("pace/1.0.2/pace.min.js"),
        'pace.css': get_cdnjs_file_url("pace/1.0.2/themes/blue/pace-theme-flash.css"),
        'mathjax.js': get_cdnjs_file_url("mathjax/2.7.3/MathJax.js?config=TeX-MML-AM_CHTML"),
        'raphael.js': get_cdnjs_file_url("raphael/2.2.7/raphael.min.js"),
        'underscore.js': get_cdnjs_file_url("underscore.js/1.8.3/underscore-min.js"),
        'sequence-diagram.js': get_cdnjs_file_url("js-sequence-diagrams/1.0.6/sequence-diagram-min.js"),
        'flowchart.js': get_cdnjs_file_url("flowchart/1.10.0/flowchart.min.js"),
        'jquery.js': get_cdnjs_file_url("jquery/3.3.1/jquery.min.js"),
        'jquery-tablesorter.js': get_cdnjs_file_url("jquery.tablesorter/2.30.1/js/jquery.tablesorter.min.js"),
        'jquery-raty.js': get_cdnjs_file_url("raty/2.8.0/jquery.raty.min.js"),
        'jquery-raty.css': get_cdnjs_file_url("raty/2.8.0/jquery.raty.min.css"),
        'github-markdown.css': get_cdnjs_file_url("github-markdown-css/2.10.0/github-markdown.min.css"),
        'buttons.css': get_cdnjs_file_url("Buttons/2.0.0/css/buttons.min.css"),
        'font-awesome.css': get_cdnjs_file_url("font-awesome/4.7.0/css/font-awesome.min.css"),
        'source-code-pro.ttf': "https://fonts.gstatic.com/s/sourcecodepro/v7/HI_SiYsKILxRpg3hIP6sJ7fM7PqlPevW.woff2",
    }[name]
