import re

import pymdownx.emoji
from markdown import markdown

from src.index import index_url_key, get_item_by_path
from src.util import regexp_join


# noinspection SpellCheckingInspection
# markdown渲染
def render(text):
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
    return markdown(rate(table_increment(inlink(add_toc(clear_md(text))))), extensions, extension_config)


# 剔除\r和被<<>>包围的内容
def clear_md(text):
    return re.sub("(\r|<<.*?>>)", "", text)


# 如果标题数量在三个及三个以上，自动在开头加上目录
def add_toc(text):
    if len(re.findall("\n#+\s+.*", text)) >= 3:
        text = "[TOC]\n\n" + text
    return text


# 匹配[]()+语法为站内链接，小括号里填入文件相对路径，查找替换为索引文件中对应的url
def inlink(text):
    # 利用字典生成去重的匹配项，提高重复匹配的替换效率
    url_match_dict = {group.group(): [group.group(1), group.group(2)]
                      for group in re.finditer("\[(.*?)\]\((.*?)\)\+", text)}
    for match in url_match_dict:
        file_path = url_match_dict[match][1]
        # 根据文件相对路径从索引文件中取出url
        item = get_item_by_path(file_path)
        if item:
            text = re.sub(regexp_join("%s", match), "[%s](%s)" % (url_match_dict[match][0], item[index_url_key]), text)
    return text


# 匹配md表格语法中| 1. |部分为自增序列
def table_increment(text):
    num = 1
    for group in re.finditer("\|\s*(:?-:?|1\.)\s*(.*)", text):
        # 进入新表格后计数重置
        if group.group(1).strip(":") == "-":
            num = 1
        else:
            # 仅替换第一次查找结果
            text = re.sub(regexp_join("%s", group.group()), "| %d %s" % (num, group.group(2)), text, 1)
            num += 1
    return text


# 匹配*[]语法为评分标签，方括号内匹配0-10
def rate(text):
    # 利用字典生成去重的匹配项，提高重复匹配的替换效率
    rate_match_dict = {group.group(): group.group(1) for group in re.finditer("\*\[([0-9]|10)\]", text)}
    for match in rate_match_dict.keys():
        # 实际展示的评分为匹配数字的一半
        rate_num = int(rate_match_dict[match]) / 2
        text = re.sub(regexp_join("%s", match), '<div class="star" data-score="%f"></div>' % rate_num, text)
    return text
