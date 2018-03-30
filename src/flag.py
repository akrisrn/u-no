import re
from datetime import datetime

from config import uno_default_tag
from src.index import index_url_key, get_item_by_path
from src.util import clean_text, regexp_join


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
    tags = [tag for tag in clean_text(group.group(1)).split(",") if tag]
    if not tags:
        return default_tag
    return tags


# 获取文章里标记的日期，语法匹配<<date(%y-%m-%d)>>，如果没有则返回空
def get_date_flag(content):
    group = re.search(get_flag_regexp("date"), content)
    if not group:
        return ""
    date = str(clean_text(group.group(1)).split(",")[0])
    try:
        # 日期格式转换为%Y.%m.%d
        date = datetime.strptime(date, "%y-%m-%d").strftime("%Y.%m.%d")
    except ValueError:
        return ""
    return date


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
def get_custom_css_flag(content, custom_type="css"):
    group = re.search(get_flag_regexp(custom_type), content)
    if not group:
        return []
    css_urls = []
    for css_path in clean_text(group.group(1)).split(","):
        if css_path:
            # 根据css文件相对路径从索引文件中取出url
            item = get_item_by_path(css_path)
            if item:
                css_urls.append(item[index_url_key])
    return css_urls


# 获取文章里标记的自定义js文件列表，语法匹配<<js()>>，如果没有则返回空
def get_custom_js_flag(content):
    return get_custom_css_flag(content, "js")
