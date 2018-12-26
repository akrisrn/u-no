import re

import pymdownx.emoji
import pymdownx.superfences
from markdown import markdown

from .const import index_url_key
from .index import get_item_by_path
from .util import regexp_join, get_articles_dir_abspath


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
        'pymdownx.snippets',
        'markdown.extensions.footnotes',
        'markdown.extensions.attr_list',
        'markdown.extensions.def_list',
        'markdown.extensions.abbr',
        'markdown.extensions.tables',
        'markdown.extensions.toc',
        'markdown.extensions.sane_lists',
    ]
    # 扩展配置
    extension_configs = {
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
            "pygments_style": "pastie"
        },
        # 自动链接配置
        "pymdownx.magiclink": {
            "repo_url_shortener": True,
            "repo_url_shorthand": True,
            "social_url_shorthand": True,
        },
        "pymdownx.superfences": {
            "custom_fences": [{
                'name': 'flow',
                'class': 'uml-flowchart',
                'format': pymdownx.superfences.fence_code_format
            }, {
                'name': 'sequence',
                'class': 'uml-sequence-diagram',
                'format': pymdownx.superfences.fence_code_format
            }]
        },
        "pymdownx.snippets": {
            "base_path": get_articles_dir_abspath()
        }
    }
    for ext in [clean_md, add_toc, inlink, table_increment, rate, steam, kindle]:
        text = ext(text)
    return markdown(text, extensions=extensions, extension_configs=extension_configs)


def get_snippet(file_name):
    if file_name:
        return '--8<-- "%s"' % file_name
    return ""


# 剔除\r和被<<>>包围的内容
def clean_md(text):
    return re.sub("(\r|<<.*?>>)", "", text)


# 如果标题数量在三个及三个以上，自动在开头加上目录
def add_toc(text):
    if len(re.findall(r"\n#+\s+.*", text)) >= 3:
        text = "[TOC]\n\n" + text
    return text


# 匹配[]()+语法为站内链接，小括号里填入文件相对路径，查找替换为索引文件中对应的url
def inlink(text):
    # 利用字典生成去重的匹配项，提高重复匹配的替换效率
    url_match_dict = {group.group(): [group.group(1), group.group(2)]
                      for group in re.finditer(r"\[(.*?)\]\((.*?)\)\+", text)}
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
    for group in re.finditer(r"\|\s*(:?-:?|1\.)\s*(.*)", text):
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
    rate_match_dict = {group.group(): group.group(1) for group in re.finditer(r"\*\[([0-9]|10)\]", text)}
    for match in rate_match_dict.keys():
        # 实际展示的评分为匹配数字的一半
        rate_num = int(rate_match_dict[match]) / 2
        text = re.sub(regexp_join("%s", match), '<div class="star" data-score="%f"></div>' % rate_num, text)
    return text


# 匹配steam[]语法为steam小部件，方括号内匹配游戏id
def steam(text):
    # 利用字典生成去重的匹配项，提高重复匹配的替换效率
    id_match_dict = {group.group(): group.group(1) for group in re.finditer(r"steam\[(\d+)\]", text)}
    for match in id_match_dict.keys():
        text = re.sub(regexp_join("%s", match),
                      '<iframe class="steam-widget" src="https://store.steampowered.com/widget/%s/"></iframe>' %
                      id_match_dict[match], text)
    return text


# 匹配kindle[]语法为亚马逊电子书小部件，方括号内匹配书籍id
def kindle(text):
    # 利用字典生成去重的匹配项，提高重复匹配的替换效率
    id_match_dict = {group.group(): group.group(1) for group in re.finditer(r"kindle\[(\w+)\]", text)}
    for match in id_match_dict.keys():
        text = re.sub(regexp_join("%s", match),
                      '<iframe class="kindle-widget" src="https://read.amazon.cn/kp/card?asin=%s&preview=inline" '
                      'frameborder="0" allowfullscreen></iframe>' % id_match_dict[match], text)
    return text
