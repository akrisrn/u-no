import hashlib
import os
import platform
import re
from datetime import datetime
from threading import Thread

import pymdownx.emoji
from flask import url_for
from markdown import markdown

from config import *


# 判断操作系统是否是Windows
def is_windows():
    return True if platform.system() == "Windows" else False


# 获取系统命令分隔符
def get_os_cmd_sep():
    return "&" if is_windows() else ";"


# 根据文件相对路径从索引文件中取出url
def get_url_from_file_path(file_path):
    group = re.search(regexp_join("\[%s\]\((.*?)\)", file_path), get_sha1_data())
    if group:
        return group.group(1)
    return ""


# noinspection SpellCheckingInspection
# markdown渲染
def md(text):
    # 剔除\r和被<<>>包围的内容
    text = re.sub("(\r|<<.*?>>)", "", text)
    # 如果标题数量在三个及三个以上，自动在开头加上目录
    if len(re.findall("#+\s+.*", text)) >= 3:
        text = "[TOC]\n\n" + text
    # 匹配[]()+语法为站内链接，小括号里填入文件相对路径，查找替换为索引文件中对应的url
    # 利用字典生成去重的匹配项，提高重复匹配的替换效率
    url_match_dict = {group.group(): [group.group(1), group.group(2)]
                      for group in re.finditer("\[(.*?)\]\((.*?)\)\+", text)}
    for match in url_match_dict:
        file_path = url_match_dict[match][1]
        # 根据文件相对路径从索引文件中取出url
        url = get_url_from_file_path(file_path)
        if url:
            text = re.sub(regexp_join("%s", match), "[%s](%s)" % (url_match_dict[match][0], url), text)
    # 匹配md表格语法中| 1. |部分为自增序列
    num = 1
    for group in re.finditer("\|\s*(:?-:?|1\.)\s*(.*)", text):
        # 进入新表格后计数重置
        if group.group(1).strip(":") == "-":
            num = 1
        else:
            # 仅替换第一次查找结果
            text = re.sub(regexp_join("%s", group.group()), "| %d %s" % (num, group.group(2)), text, 1)
            num += 1
    # 匹配*[]语法为评分标签，方括号内匹配0-10
    # 利用字典生成去重的匹配项，提高重复匹配的替换效率
    rate_match_dict = {group.group(): group.group(1) for group in re.finditer("\*\[([0-9]|10)\]", text)}
    for match in rate_match_dict.keys():
        # 实际展示的评分为匹配数字的一半
        rate = int(rate_match_dict[match]) / 2
        text = re.sub(regexp_join("%s", match), '<div class="star" data-score="%f"></div>' % rate, text)
    # markdown扩展
    extensions = [
        'pymdownx.arithmatex',
        'pymdownx.betterem',
        'pymdownx.caret',
        'pymdownx.critic',
        'pymdownx.details',
        'pymdownx.emoji',
        'pymdownx.escapeall',
        'pymdownx.extrarawhtml',
        'pymdownx.highlight',
        'pymdownx.inlinehilite',
        'pymdownx.keys',
        'pymdownx.magiclink',
        'pymdownx.mark',
        'pymdownx.progressbar',
        'pymdownx.smartsymbols',
        'pymdownx.striphtml',
        'pymdownx.superfences',
        'pymdownx.tasklist',
        'pymdownx.tilde',
        'markdown.extensions.footnotes',
        'markdown.extensions.attr_list',
        'markdown.extensions.def_list',
        'markdown.extensions.tables',
        'markdown.extensions.abbr',
        'markdown.extensions.toc',
    ]
    # 扩展配置
    extension_config = {
        # 使用GitHub的emoji
        "pymdownx.emoji": {
            "emoji_index": pymdownx.emoji.gemoji,
            "emoji_generator": pymdownx.emoji.to_png,
            "alt": "short",
            "options": {
                "attributes": {
                    "align": "absmiddle",
                    "height": "20px",
                    "width": "20px"
                },
                "image_path": "https://assets-cdn.github.com/images/icons/emoji/unicode/",
                "non_standard_image_path": "https://assets-cdn.github.com/images/icons/emoji/"
            }
        },
        "pymdownx.escapeall": {
            "hardbreak": True,  # 转义换行符为<br>
            "nbsp": True  # 转义空格为&nbsp;
        },
        # 代码高亮配置
        "pymdownx.highlight": {
            "noclasses": True,
            "pygments_style": "friendly"
        },
        # 自动链接配置
        "pymdownx.magiclink": {
            "repo_url_shortener": True,
            "repo_url_shorthand": True,
            "social_url_shorthand": True,
        }
    }
    return markdown(text, extensions, extension_config)


# 根据文件绝对路径计算哈希
def sha1_digest_file(file_abspath):
    # 判断文件是否存在
    if os.path.isdir(file_abspath) or not os.path.exists(file_abspath):
        return ""
    with open(file_abspath, 'rb') as file:
        content = file.read()
    return hashlib.sha1(content).hexdigest()


# 根据文件内容计算哈希
def sha1_digest_content(content):
    return hashlib.sha1(content.encode("utf-8")).hexdigest()


# 判断哈希格式
def check_sha1(sha1):
    # 40位且由字母数字组成
    if len(sha1) != 40 or not sha1.isalnum():
        return False
    return True


# 获取索引文件数据
def get_sha1_data():
    # 组成索引文件绝对路径
    sha1_file_path = os.path.join(get_articles_dir_abspath(), uno_sha1_file_name)
    # 判断是否存在
    if os.path.exists(sha1_file_path):
        with open(sha1_file_path, encoding='utf-8') as sha1_file:
            sha1_data = sha1_file.read()
        return sha1_data
    else:
        return None


# 获取根目录绝对路径
def get_root_abspath():
    # 根据当前文件的位置进行切割
    return os.path.dirname(os.path.abspath(__file__)).split('util')[0]


# 获取文章目录绝对路径
def get_articles_dir_abspath():
    return os.path.join(get_root_abspath(), uno_articles_dir_name)


# 获取附件目录绝对路径
def get_attachments_dir_abspath():
    return os.path.join(get_root_abspath(), uno_articles_dir_name, uno_attachments_dir_name)


# 获取静态目录绝对路径
def get_static_dir_abspath():
    return os.path.join(get_root_abspath(), uno_static_dir_name)


# 获取静态文件url
def get_static_file_url(filename, have_version=True):
    # 判断是否在url尾部加上版本号
    if have_version:
        return get_version(url_for("static", filename=filename))
    return url_for("static", filename=filename)


# 获取bower包文件url
def get_bower_file_url(filename):
    return url_for("static", filename="bower_components/%s" % filename)


# 获取版本号
def get_version(url):
    # 在调试模式和没有配置版本号的情况下计算文件哈希作为版本号
    ver = uno_version if uno_version and not uno_debug else sha1_digest_file(os.path.join(get_root_abspath(), url[1:]))
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


# 清洗文本，剔除空白、双引号、单引号
def clear_text(text):
    return re.sub("(\s|\"|\')", "", text)


# 获取匹配flag的正则表达式，忽略大小写
def get_flag_regexp(flag):
    return re.compile(regexp_join("<<\s*%s\((.*?)\)\s*>>", flag), re.I)


# 获取文章里标记的标签列表，语法匹配<<tag()>>，如果没有则返回默认标签
def get_tags_flag(content):
    default_tag = [uno_default_tag]
    group = re.search(get_flag_regexp("tag"), content)
    if not group:
        return default_tag
    # 生成标签列表
    tags = [tag for tag in clear_text(group.group(1)).split(",") if tag]
    if not tags:
        return default_tag
    return tags


# 获取文章里标记的日期，语法匹配<<date(%y-%m-%d)>>，如果没有则返回空
def get_date_flag(content):
    group = re.search(get_flag_regexp("date"), content)
    if not group:
        return ""
    date = str(clear_text(group.group(1)).split(",")[0])
    try:
        # 日期格式转换为%Y.%m.%d
        date = datetime.strptime(date, "%y-%m-%d").strftime("%Y.%m.%d")
    except ValueError:
        return ""
    return date


# 获取文章里标记的关闭侧边栏标识，语法匹配<<nosidebar()>>
def get_no_sidebar_flag(content):
    return re.search(get_flag_regexp("nosidebar"), content)


# 获取文章里标记的固定链接标识，语法匹配<<fixed()>>
def get_fixed_flag(content):
    return re.search(get_flag_regexp("fixed"), content)


# 获取文章里标记的自定义css文件列表，语法匹配<<css()>>，如果没有则返回空
def get_custom_css(content, custom_type="css"):
    group = re.search(get_flag_regexp(custom_type), content)
    if not group:
        return []
    css_urls = []
    for css_path in clear_text(group.group(1)).split(","):
        if css_path:
            # 根据css文件相对路径从索引文件中取出url
            css_url = get_url_from_file_path(css_path)
            if css_url:
                css_urls.append(css_url)
    return css_urls


# 获取文章里标记的自定义js文件列表，语法匹配<<js()>>，如果没有则返回空
def get_custom_js(content):
    return get_custom_css(content, "js")


# 根据传入的标签数量生成md语法的表格头部
def get_sha1_data_table_header(tag_num):
    table_header = " | ".join(["No.", "Name", "Date", " | ".join(["Tag-%d" % (i + 1) for i in range(tag_num)])]) + "\n"
    table_format = " | ".join(["-"] * (tag_num + 3))
    return table_header + table_format


# 处理线程，在限制列表下只能同时运行一个线程任务
def handle_thread(thread_limit_list, target):
    # 如果线程结束了，清空限制列表
    if thread_limit_list and not thread_limit_list[0].is_alive():
        thread_limit_list.clear()
    # 如果限制列表为空，加入新任务到限制列表并启动
    if not thread_limit_list:
        thread_limit_list.append(Thread(target=target))
        thread_limit_list[0].start()


# 切割提取出文件前缀组成索引文件表格的第一列
def split_pref(content):
    new_content = "\n"
    # 根据水平线分离出文章块和附件块，如果没有水平线则附件块为空
    if content.find("---") != -1:
        blocks = content.split("---")
        article_block = blocks[0]
        attachments_block = blocks[1]
    else:
        article_block = content
        attachments_block = ""
    for data in article_block.split("\n"):
        # 匹配包含前缀的行
        group = re.search("\[(%s)(.*?)\]" % uno_strip_prefix, data)
        if group:
            # 提取出前缀
            replace = "%s | [%s]" % (group.group(1).strip("-"), os.path.splitext(group.group(2))[0])
            new_content += re.sub(regexp_join("%s", group.group()), replace, data) + "\n"
        else:
            new_content += (" | " + data + "\n") if data else ""
    # 重新组合文章块和附件块
    new_content += ("\n---" + attachments_block) if attachments_block else ""
    return new_content


# 用于搜索的内容过滤器，接受一组正则规则列表，以AND模式运行，同时会计算内容的最大标签数
def content_filter(content, rules):
    new_content = "\n"
    max_tag_num = 0
    # 如果没有规则列表则只计算最大标签数
    if rules:
        for line in content.split("\n"):
            # 匹配到水平线时还原附件块的表头和与文章块的分隔
            if line == "---":
                new_content += "\n---\n| Name\n| -\n"
            is_find = True
            for rule in rules:
                # 只要一个规则没匹配就跳出
                if not re.search(rule, line):
                    is_find = False
                    break
            if is_find:
                new_content += line + "\n"
                # 计算最大标签数
                max_tag_num = max(len(line.split(" | ")) - 2, max_tag_num)
    else:
        for line in content.split("\n"):
            # 计算最大标签数
            max_tag_num = max(len(line.split(" | ")) - 2, max_tag_num)
    return new_content if rules else content, max_tag_num


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


# 更新配置文件中的固定文件列表
def update_config_fixed_file_list(file_path, is_add, var=uno_fixed_file_list, name="uno_fixed_file_list"):
    # 判断是添加还是移除
    if is_add is True and file_path not in var:
        var.append(file_path)
    elif is_add is False and file_path in var:
        var.remove(file_path)
    else:
        return None
    # 读取配置文件数据
    config_abspath = os.path.join(get_root_abspath(), "config.py")
    with open(config_abspath, encoding="utf-8") as config_file:
        config_data = config_file.read()
    # 用新列表替换旧列表
    config_data = re.sub("%s\s*=\s*\[.*?\]" % name, "%s = %s" % (name, var), config_data)
    # 重新写入配置文件
    with open(config_abspath, "w", encoding="utf-8") as config_file:
        config_file.write(config_data)


# 更新配置文件中的忽略文件列表
def update_config_ignore_file_list(file_path):
    update_config_fixed_file_list(file_path, True, uno_ignore_file_list, "uno_ignore_file_list")
