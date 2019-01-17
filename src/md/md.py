import re

import pymdownx.emoji
import pymdownx.superfences
from markdown import markdown

import src.flag
import src.index
from ..const import index_url_key
from ..util import regexp_join, get_articles_dir_abspath, get_unique_find_dict


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
        'src.md.ext.cleanup',
        'src.md.ext.symbols_extend',
        'src.md.ext.lazy_img',
        'src.md.ext.force_del_ins'
    ]
    # 扩展配置
    extension_configs = {
        # 使用GitHub的emoji
        "pymdownx.emoji": {
            "emoji_index": pymdownx.emoji.gemoji,
            "emoji_generator": pymdownx.emoji.to_png,
            "options": {
                "attributes": {
                    "align": "absmiddle",
                    "height": "20px",
                    "width": "20px"
                },
            }
        },
        "pymdownx.escapeall": {
            "hardbreak": True,  # 转义换行符为<br>
            "nbsp": True  # 转义空格为&nbsp;
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
    for ext in [inlink, inline_quote, table_increment, rate, steam, kindle, music, music_list]:
        text = ext(text)
    return markdown(text, extensions=extensions, extension_configs=extension_configs)


def get_snippet(file_name):
    if file_name:
        return '--8<-- "%s"' % file_name
    return ""


# 匹配[]()+语法为站内链接，小括号里填入文件相对路径，查找替换为索引文件中对应的url
def inlink(text, is_return_path=False):
    file_path_list = []
    url_match_dict = get_unique_find_dict(r"\[(.*?)\]\((.*?)\)\+", text, 2)
    for match in url_match_dict:
        file_path = url_match_dict[match][1].replace("../", "")
        # 根据文件相对路径从索引文件中取出url
        item = src.index.get_item_by_path(file_path)
        if item:
            text = re.sub(regexp_join("%s", match), "[%s](%s)" % (url_match_dict[match][0], item[index_url_key]), text)
            file_path_list.append(file_path)
    return text if not is_return_path else file_path_list


# 匹配____text____语法为行内引用
def inline_quote(text):
    text_match_dict = get_unique_find_dict(r"____(.+)____", text)
    for match in text_match_dict:
        text = re.sub(regexp_join("%s", match), '*%s*{:.inline-quote}' % text_match_dict[match], text)
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
    rate_match_dict = get_unique_find_dict(r"\*\[([0-9]|10)\]", text)
    for match in rate_match_dict:
        # 实际展示的评分为匹配数字的一半
        rate_num = int(rate_match_dict[match]) / 2
        text = re.sub(regexp_join("%s", match), '<div class="star" data-score="%f"></div>' % rate_num, text)
    return text


# 匹配steam[]语法为steam小部件，方括号内匹配游戏id
def steam(text):
    id_match_dict = get_unique_find_dict(r"steam\[(\d+)\]", text)
    for match in id_match_dict:
        text = re.sub(regexp_join("%s", match),
                      '<iframe class="steam-widget" data-id="%s"></iframe>' % id_match_dict[match], text)
    return text


# 匹配kindle[]语法为亚马逊电子书小部件，方括号内匹配书籍id
def kindle(text):
    id_match_dict = get_unique_find_dict(r"kindle\[(\w+)\]", text)
    for match in id_match_dict:
        text = re.sub(regexp_join("%s", match),
                      '<iframe class="kindle-widget" data-id="%s"></iframe>' % id_match_dict[match], text)
    return text


# 匹配music[]语法为网易云音乐单曲小部件，方括号内匹配单曲id
def music(text):
    id_match_dict = get_unique_find_dict(r"music\[(\d+)\]", text)
    for match in id_match_dict:
        text = re.sub(regexp_join("%s", match),
                      '<iframe class="music-widget" data-id="%s"></iframe>' % id_match_dict[match], text)
    return text


# 匹配music_list[]语法为网易云音乐歌单小部件，方括号内匹配歌单id
def music_list(text):
    id_match_dict = get_unique_find_dict(r"music_list\[(\d+)\]", text)
    for match in id_match_dict:
        text = re.sub(regexp_join("%s", match),
                      '<iframe class="music-list-widget" data-id="%s"></iframe>' % id_match_dict[match], text)
    return text
