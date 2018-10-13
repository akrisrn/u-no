import hashlib
import os
import re

from flask import url_for

from config import uno_ignore_file_list, uno_debug, uno_version, uno_use_cdn, uno_articles_dir_abspath


# 获取根目录绝对路径
def get_root_abspath():
    # 根据当前目录的位置进行切割
    return os.path.dirname(os.path.abspath(__file__)).split(__package__)[0]


# 获取文章目录绝对路径
def get_articles_dir_abspath():
    return uno_articles_dir_abspath


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
    url = url.replace("http://", "")
    # 在调试模式和没有配置版本号的情况下计算文件哈希作为版本号
    file_abspath = os.path.join(get_root_abspath(), url[1:])
    ver = uno_version if uno_version and not uno_debug else compute_digest_by_abspath(file_abspath)
    return "%s?v=%s" % (url, ver)


def update_config(origin, replace):
    # 读取配置文件数据
    config_abspath = os.path.join(get_root_abspath(), "config.py")
    with open(config_abspath, encoding="utf-8") as config_file:
        config_data = config_file.read()
    # 用新数据替换旧数据
    config_data = re.sub(origin, replace, config_data)
    # 重新写入配置文件
    with open(config_abspath, "w", encoding="utf-8") as config_file:
        config_file.write(config_data)


# 更新配置文件中的忽略文件列表
def update_config_ignore_file_list(file_path, is_add):
    # 判断是添加还是移除
    if is_add and file_path not in uno_ignore_file_list:
        uno_ignore_file_list.append(file_path)
    elif not is_add and file_path in uno_ignore_file_list:
        uno_ignore_file_list.remove(file_path)
    else:
        return None
    # 用新列表替换旧列表
    replace = "%s = %s" % ("uno_ignore_file_list", uno_ignore_file_list)
    origin = "%s\s*=\s*\[.*?\]" % "uno_ignore_file_list"
    update_config(origin, replace)


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


# 检查哈希值是否有效
def is_valid_hash(hash_value):
    return len(hash_value) == 40 and hash_value.isalnum()


# 获取本地包中文件url
def get_module_file_url(filename, is_npm=True):
    dir_name = "node_modules" if is_npm else "bower_components"
    return url_for("static", filename="%s/%s" % (dir_name, filename))


# 获取cdn中文件url
def get_cdn_file_url(filename, is_npm=True):
    cdn_type = "npm" if is_npm else "gh"
    return "https://cdn.jsdelivr.net/%s/%s" % (cdn_type, filename)


lib = {}
remoteOrLocal = "remote" if uno_use_cdn else "local"


# 根据是否使用cdn选择本地包路径或cdn链接
def get_static_lib_url(name):
    global lib
    if not lib:
        lib = {
            "vue.js": {
                "local": get_module_file_url("vue/dist/vue." + ("js" if uno_debug else "min.js")),
                "remote": get_cdn_file_url("vue@2.5.17/dist/vue." + ("js" if uno_debug else "min.js"))
            },
            "pace.js": {
                "local": get_module_file_url("pace-js/pace.min.js"),
                "remote": get_cdn_file_url("pace-js@1.0.2/pace.min.js")
            },
            "pace-theme-flash.css": {
                "local": get_module_file_url("pace-js/themes/blue/pace-theme-flash.css"),
                "remote": get_cdn_file_url("pace-js@1.0.2/themes/blue/pace-theme-flash.css")
            },
            "mathjax.js": {
                "local": get_module_file_url("mathjax/unpacked/MathJax.js") + "?config=TeX-MML-AM_CHTML",
                "remote": get_cdn_file_url("mathjax@2.7.5/unpacked/MathJax.js?config=TeX-MML-AM_CHTML")
            },
            "raphael.js": {
                "local": get_module_file_url("raphael/raphael.min.js"),
                "remote": get_cdn_file_url("raphael@2.2.7/raphael.min.js")
            },
            "underscore.js": {
                "local": get_module_file_url("underscore/underscore-min.js"),
                "remote": get_cdn_file_url("underscore@1.9.1/underscore-min.js")
            },
            "sequence-diagram.js": {
                "local": get_module_file_url("js-sequence-diagrams/dist/sequence-diagram-min.js", False),
                "remote": get_cdn_file_url("bramp/js-sequence-diagrams@2.0.1/dist/sequence-diagram-min.js", False)
            },
            "flowchart.js": {
                "local": get_module_file_url("flowchart.js/release/flowchart.min.js"),
                "remote": get_cdn_file_url("flowchart.js@1.11.3/release/flowchart.min.js")
            },
            "jquery.js": {
                "local": get_module_file_url("jquery/dist/jquery.min.js"),
                "remote": get_cdn_file_url("jquery@3.3.1/dist/jquery.min.js")
            },
            "jquery-tablesorter.js": {
                "local": get_module_file_url("tablesorter/dist/js/jquery.tablesorter.min.js"),
                "remote": get_cdn_file_url("tablesorter@2.31.0/dist/js/jquery.tablesorter.min.js")
            },
            "jquery-raty.js": {
                "local": get_module_file_url("raty-js/lib/jquery.raty.js"),
                "remote": get_cdn_file_url("raty-js@2.8.0/lib/jquery.raty.min.js")
            },
            "jquery-raty.css": {
                "local": get_module_file_url("raty-js/lib/jquery.raty.css"),
                "remote": get_cdn_file_url("raty-js@2.8.0/lib/jquery.raty.min.css")
            },
            "github-markdown.css": {
                "local": get_module_file_url("github-markdown-css/github-markdown.css"),
                "remote": get_cdn_file_url("github-markdown-css@2.10.0/github-markdown.min.css")
            },
            "font-awesome-all.css": {
                "local": get_module_file_url("@fortawesome/fontawesome-free/css/all.min.css"),
                "remote": get_cdn_file_url("@fortawesome/fontawesome-free@5.4.1/css/all.min.css")
            },
            "source-code-pro.css": {
                "local": get_module_file_url("source-code-pro/source-code-pro.css"),
                "remote": get_cdn_file_url("source-code-pro@2.30.1/source-code-pro.min.css")
            }
        }
    return lib[name][remoteOrLocal]
