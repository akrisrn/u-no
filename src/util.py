import hashlib
import json
import os
import re

from flask import url_for, current_app


# 获取根目录绝对路径
def get_root_abspath():
    # 根据当前目录的位置进行切割
    return os.path.dirname(os.path.abspath(__file__)).split("src")[0]


# 获取静态目录绝对路径
def get_static_abspath():
    return os.path.join(get_root_abspath(), current_app.config["STATIC_DIR_NAME"])


# 获取文章目录绝对路径
def get_articles_dir_abspath():
    return current_app.config["ARTICLES_DIR_ABSPATH"]


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
    version = current_app.config["VERSION"]
    ver = version if version and not current_app.config["DEBUG"] else compute_digest_by_abspath(file_abspath)
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
    ignore_file_list = current_app.config["IGNORE_FILE_LIST"]
    if is_add and file_path not in ignore_file_list:
        ignore_file_list.append(file_path)
    elif not is_add and file_path in ignore_file_list:
        ignore_file_list.remove(file_path)
    else:
        return None
    current_app.config["IGNORE_FILE_LIST"] = ignore_file_list
    # 用新列表替换旧列表
    replace = "%s = %s" % ("IGNORE_FILE_LIST", ignore_file_list)
    origin = "%s\s*=\s*\[.*?\]" % "IGNORE_FILE_LIST"
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


package_json_data = {}
bower_json_data = {}


def get_lib_version(name):
    global package_json_data
    global bower_json_data
    if not package_json_data:
        static_abspath = get_static_abspath()
        with open(os.path.join(static_abspath, "package.json"), encoding="utf-8") as package_json_file:
            package_json_data = json.loads(package_json_file.read())
        with open(os.path.join(static_abspath, "bower.json"), encoding="utf-8") as bower_json_file:
            bower_json_data = json.loads(bower_json_file.read())
    version = "^"
    name = name.split("|")[0]
    package_dep = package_json_data["dependencies"]
    if name in package_dep:
        version = package_dep[name]
    else:
        bower_dep = bower_json_data["dependencies"]
        if name in bower_dep:
            version = bower_dep[name]
    return version.split("^")[1]


lib = {}


# 根据是否使用cdn选择本地包路径或cdn链接
def get_static_lib_url(name):
    global lib
    if not lib:
        libs = ["vue",
                "pace-js",
                "pace-js|css",
                "mathjax",
                "raphael",
                "underscore",
                "js-sequence-diagrams",
                "flowchart.js",
                "jquery",
                "tablesorter",
                "raty-js",
                "raty-js|css",
                "github-markdown-css",
                "@fortawesome/fontawesome-free",
                "source-code-pro"]
        lib = {
            libs[0]: {
                "local": get_module_file_url("vue/dist/vue.min.js"),
                "remote": get_cdn_file_url("vue@%s/dist/vue.min.js" % get_lib_version(libs[0]))
            },
            libs[1]: {
                "local": get_module_file_url("pace-js/pace.min.js"),
                "remote": get_cdn_file_url("pace-js@%s/pace.min.js" % get_lib_version(libs[1]))
            },
            libs[2]: {
                "local": get_module_file_url("pace-js/themes/blue/pace-theme-flash.css"),
                "remote": get_cdn_file_url("pace-js@%s/themes/blue/pace-theme-flash.css" % get_lib_version(libs[2]))
            },
            libs[3]: {
                "local": get_module_file_url("mathjax/unpacked/MathJax.js") + "?config=TeX-MML-AM_CHTML",
                "remote": get_cdn_file_url(
                    "mathjax@%s/unpacked/MathJax.js?config=TeX-MML-AM_CHTML" % get_lib_version(libs[3]))
            },
            libs[4]: {
                "local": get_module_file_url("raphael/raphael.min.js"),
                "remote": get_cdn_file_url("raphael@%s/raphael.min.js" % get_lib_version(libs[4]))
            },
            libs[5]: {
                "local": get_module_file_url("underscore/underscore-min.js"),
                "remote": get_cdn_file_url("underscore@%s/underscore-min.js" % get_lib_version(libs[5]))
            },
            libs[6]: {
                "local": get_module_file_url("js-sequence-diagrams/dist/sequence-diagram-min.js", False),
                "remote": get_cdn_file_url(
                    "bramp/js-sequence-diagrams@%s/dist/sequence-diagram-min.js" % get_lib_version(libs[6]), False)
            },
            libs[7]: {
                "local": get_module_file_url("flowchart.js/release/flowchart.min.js"),
                "remote": get_cdn_file_url("flowchart.js@%s/release/flowchart.min.js" % get_lib_version(libs[7]))
            },
            libs[8]: {
                "local": get_module_file_url("jquery/dist/jquery.min.js"),
                "remote": get_cdn_file_url("jquery@%s/dist/jquery.min.js" % get_lib_version(libs[8]))
            },
            libs[9]: {
                "local": get_module_file_url("tablesorter/dist/js/jquery.tablesorter.min.js"),
                "remote": get_cdn_file_url(
                    "tablesorter@%s/dist/js/jquery.tablesorter.min.js" % get_lib_version(libs[9]))
            },
            libs[10]: {
                "local": get_module_file_url("raty-js/lib/jquery.raty.js"),
                "remote": get_cdn_file_url("raty-js@%s/lib/jquery.raty.min.js" % get_lib_version(libs[10]))
            },
            libs[11]: {
                "local": get_module_file_url("raty-js/lib/jquery.raty.css"),
                "remote": get_cdn_file_url("raty-js@%s/lib/jquery.raty.min.css" % get_lib_version(libs[11]))
            },
            libs[12]: {
                "local": get_module_file_url("github-markdown-css/github-markdown.css"),
                "remote": get_cdn_file_url("github-markdown-css@%s/github-markdown.min.css" % get_lib_version(libs[12]))
            },
            libs[13]: {
                "local": get_module_file_url("@fortawesome/fontawesome-free/css/all.min.css"),
                "remote": get_cdn_file_url(
                    "@fortawesome/fontawesome-free@%s/css/all.min.css" % get_lib_version(libs[13]))
            },
            libs[14]: {
                "local": get_module_file_url("source-code-pro/source-code-pro.css"),
                "remote": get_cdn_file_url("source-code-pro@%s/source-code-pro.min.css" % get_lib_version(libs[14]))
            }
        }
    return lib[name]["remote" if current_app.config["USE_CDN"] else "local"]
