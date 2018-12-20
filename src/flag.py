import re
from datetime import datetime

from flask import current_app

import src.index
from .const import index_url_key, flag_js, flag_css, flag_unignore, flag_ignore, flag_highlight, flag_top, \
    flag_fixed, flag_notags, flag_tag, flag_date, flag_plugin
from .util import clean_text, regexp_join


# 获取匹配flag的正则表达式，忽略大小写
def get_flag_regexp(flag):
    return re.compile(regexp_join(r"(\s*<<\s*%s\()(.*?)(\)\s*>>)", flag), re.I)


# 获取文章里标记的标签列表，语法匹配<<tag()>>，如果没有则返回默认标签
def get_tags_flag(data):
    default_tag = [current_app.config["DEFAULT_TAG"]]
    group = re.search(get_flag_regexp(flag_tag), data)
    if not group:
        return default_tag
    # 生成标签列表
    tags = [tag for tag in re.split("[,，]", clean_text(group.group(2))) if tag]
    if not tags:
        return default_tag
    return tags


# 获取文章里标记的日期，语法匹配<<date(%y-%m-%d)>>，如果没有则返回空
def get_date_flag(data):
    group = re.search(get_flag_regexp(flag_date), data)
    if not group:
        return ""
    date = str(clean_text(group.group(2)).split(",")[0])
    new_date = ""
    date_formats = ["%Y-%m-%d", "%y-%m-%d"]
    for date_format in date_formats:
        try:
            new_date = datetime.strptime(date, date_format).strftime("%Y-%m-%d")
            break
        except ValueError:
            continue
    return new_date


# 获取文章里标记的不展示标签标识，语法匹配<<notags()>>
def get_notags_flag(data):
    return True if re.search(get_flag_regexp(flag_notags), data) else False


# 获取文章里标记的固定索引标识，语法匹配<<fixed()>>
def get_fixed_flag(data):
    return True if re.search(get_flag_regexp(flag_fixed), data) else False


# 获取文章里标记的置顶标识，语法匹配<<top()>>
def get_top_flag(data):
    return True if re.search(get_flag_regexp(flag_top), data) else False


# 获取文章里标记的高亮标识，语法匹配<<highlight()>>
def get_highlight_flag(data):
    return True if re.search(get_flag_regexp(flag_highlight), data) else False


# 获取文章里标记的忽略文件标识，语法匹配<<ignore()>>
def get_ignore_flag(data):
    return True if re.search(get_flag_regexp(flag_ignore), data) else False


# 获取文章里标记的取消忽略文件标识，语法匹配<<unignore()>>
def get_unignore_flag(data):
    return True if re.search(get_flag_regexp(flag_unignore), data) else False


# 获取文章里标记的自定义css文件列表，语法匹配<<css()>>，如果没有则返回空
def get_custom_css_flag(data, custom_type=flag_css):
    group = re.search(get_flag_regexp(custom_type), data)
    if not group:
        return []
    css_urls = []
    for css_path in clean_text(group.group(2)).split(","):
        if css_path:
            # 根据css文件相对路径从索引文件中取出url
            item = src.index.get_item_by_path(css_path)
            if item:
                css_urls.append(item[index_url_key])
    return css_urls


# 获取文章里标记的自定义js文件列表，语法匹配<<js()>>，如果没有则返回空
def get_custom_js_flag(data):
    return get_custom_css_flag(data, flag_js)


# 获取文章里标记的插件列表，语法匹配<<plugin()>>，如果没有则返回空
def get_plugin_flag(data):
    group = re.search(get_flag_regexp(flag_plugin), data)
    if not group:
        return []
    return [plugin_name for plugin_name in clean_text(group.group(2)).split(",") if plugin_name]
