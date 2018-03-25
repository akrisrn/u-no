import hashlib
import json
import os
import platform
import re
from datetime import datetime
from threading import Thread

import pymdownx.emoji
from flask import url_for
from markdown import markdown

from config import *

# 组成索引的JSON数据所用的键名
index_id_key = "id"
index_title_key = "title"
index_url_key = "url"
index_date_key = "date"
index_tags_key = "tags"
index_fixed_key = "fixed"


# 判断操作系统是否是Windows
def is_windows():
    return True if platform.system() == "Windows" else False


# 获取系统命令分隔符
def get_os_cmd_sep():
    return "&" if is_windows() else ";"


# 根据相对路径从索引文件中取出对应项目
def get_item_by_path(path):
    for block in get_index_data():
        if path in block:
            return block[path]
    return {}


# 根据url从索引文件中取出对应项目
def get_item_by_url(url):
    for block in get_index_data():
        for item_path in block:
            item = block[item_path]
            if item[index_url_key] == url:
                return item, item_path
    return {}, ""


# noinspection SpellCheckingInspection
# markdown渲染
def render(text):
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
        item = get_item_by_path(file_path)
        if item:
            text = re.sub(regexp_join("%s", match), "[%s](%s)" % (url_match_dict[match][0], item[index_url_key]), text)
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


# 获取索引文件数据
def get_index_data():
    # 组成索引文件绝对路径
    index_file_path = os.path.join(get_articles_dir_abspath(), uno_index_file_name)
    # 判断是否存在
    if os.path.exists(index_file_path):
        with open(index_file_path, encoding='utf-8') as index_file:
            index_data = index_file.read()
        return json.loads(index_data)
    return []


# 获取根目录绝对路径
def get_root_abspath():
    # 根据当前文件的位置进行切割
    return os.path.dirname(os.path.abspath(__file__)).split('util')[0]


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


# 获取文章里标记的固定索引标识，语法匹配<<fixed()>>
def get_fixed_flag(content):
    return re.search(get_flag_regexp("fixed"), content)


# 获取文章里标记的忽略文件标识，语法匹配<<ignore()>>
def get_ignore_flag(content):
    return re.search(get_flag_regexp("ignore"), content)


# 获取文章里标记的取消忽略文件标识，语法匹配<<unignore()>>
def get_unignore_flag(content):
    return re.search(get_flag_regexp("unignore"), content)


# 获取文章里标记的自定义css文件列表，语法匹配<<css()>>，如果没有则返回空
def get_custom_css(content, custom_type="css"):
    group = re.search(get_flag_regexp(custom_type), content)
    if not group:
        return []
    css_urls = []
    for css_path in clear_text(group.group(1)).split(","):
        if css_path:
            # 根据css文件相对路径从索引文件中取出url
            item = get_item_by_path(css_path)
            if item:
                css_urls.append(item[index_url_key])
    return css_urls


# 获取文章里标记的自定义js文件列表，语法匹配<<js()>>，如果没有则返回空
def get_custom_js(content):
    return get_custom_css(content, "js")


# 处理线程，在限制列表下只能同时运行一个线程任务
def handle_thread(thread_limit_list, target):
    # 如果线程结束了，清空限制列表
    if thread_limit_list and not thread_limit_list[0].is_alive():
        thread_limit_list.clear()
    # 如果限制列表为空，加入新任务到限制列表并启动
    if not thread_limit_list:
        thread_limit_list.append(Thread(target=target))
        thread_limit_list[0].start()


# 用于搜索索引的过滤器，接受一组索引键名和搜索项的列表，以AND模式运行，同时计算出文章的最大标签数
def index_data_filter(searches):
    articles = []
    attachments = []
    max_tag_num = 0
    index_data = get_index_data()
    if index_data:
        articles_block = index_data[0]
        attachments_block = index_data[1]
        # 先处理文章块
        for article_path in articles_block:
            article = articles_block[article_path]
            is_find = True
            for index, search in searches:
                # 根据搜索内容组成正则表达式，忽略大小写
                pattern = re.compile(regexp_join(".*%s.*", search), re.I)
                # 如果搜索的是标签则遍历所有标签进行匹配
                if index == index_tags_key:
                    is_tag_find = False
                    # 有一个匹配则视为找到标签，结束循环
                    for tag in article[index]:
                        if re.search(pattern, tag):
                            is_tag_find = True
                            break
                    # 如果标签都没匹配则视为没找到对应文章，结束循环
                    if not is_tag_find:
                        is_find = False
                        break
                else:
                    # 如果没匹配则视为没找到对应文章，结束循环
                    if not re.search(pattern, article[index]):
                        is_find = False
                        break
            # 如果找到则把文章加入列表
            if is_find:
                # 计算最大标签数量
                max_tag_num = max(max_tag_num, len(article[index_tags_key]))
                articles.append(article)
        # 处理附件块
        for attachment_path in attachments_block:
            attachment = attachments_block[attachment_path]
            is_find = True
            for index, search in searches:
                # 如果搜索的有日期或标签则视为没找到对应附件，结束循环
                if index in (index_date_key, index_tags_key):
                    is_find = False
                    break
                # 根据搜索内容组成正则表达式，忽略大小写
                pattern = re.compile(regexp_join(".*%s.*", search), re.I)
                # 如果没匹配则视为没找到对应附件，结束循环
                if not re.search(pattern, attachment[index]):
                    is_find = False
                    break
            # 如果找到则把附件加入列表
            if is_find:
                attachments.append(attachment)
    return [articles, attachments], max_tag_num


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


# 获取固定索引的文章列表
def get_fixed_articles():
    fixed_articles = []
    index_data = get_index_data()
    if index_data:
        articles_block = index_data[0]
        # 遍历文章块
        for article_path in articles_block:
            article = articles_block[article_path]
            # 把固定索引的文章加入列表
            if article[index_fixed_key]:
                fixed_articles.append(article)
        # 按照时间倒叙进行排序
        fixed_articles.sort(key=lambda o: o[index_date_key], reverse=True)
    return fixed_articles
