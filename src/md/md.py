import pymdownx.emoji
import pymdownx.superfences
from markdown import markdown

import src.flag
import src.index
from ..util import get_articles_dir_abspath, get_unique_find_dict


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
        'markdown.extensions.abbr',
        'markdown.extensions.tables',
        'markdown.extensions.toc',
        'markdown.extensions.sane_lists',
        'src.md.ext.cleanup',
        'src.md.ext.symbols_extend',
        'src.md.ext.lazy_img',
        'src.md.ext.force_del_ins',
        'src.md.ext.steam_widget',
        'src.md.ext.kindle_widget',
        'src.md.ext.music_widget',
        'src.md.ext.music_list_widget',
        'src.md.ext.rate',
        'src.md.ext.inlink',
        'src.md.ext.inline_quote',
        'src.md.ext.table_increment',
        'src.md.ext.template',
        'src.md.ext.eval_python',
        'src.md.ext.fontawesome',
        'src.md.ext.script',
        'src.md.ext.magiclink',
    ]
    # 扩展配置
    extension_configs = {
        # 使用GitHub的emoji
        "pymdownx.emoji": {
            "emoji_index": pymdownx.emoji.emojione,
            "emoji_generator": pymdownx.emoji.to_png,
            "options": {
                "attributes": {
                    "width": "20px"
                },
            }
        },
        "pymdownx.escapeall": {
            "hardbreak": True,  # 转义换行符为<br>
            "nbsp": True  # 转义空格为&nbsp;
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
        "src.md.ext.template": {
            "base_path": get_articles_dir_abspath()
        },
        # 自动链接配置
        "src.md.ext.magiclink": {
            "repo_url_shortener": True,
            "repo_url_shorthand": True,
            "social_url_shorthand": True,
        },
    }
    return markdown(text, extensions=extensions, extension_configs=extension_configs)


def get_template(file_name, params=None):
    if params is None:
        params = []
    params.insert(0, "")
    if file_name:
        return r'{%% %s%s %%}' % (file_name, "|".join(params))
    return ""


def get_reference(text):
    file_path_list = []
    url_match_dict = get_unique_find_dict(r"\[(.*?)\]\((.*?)\)\+", text, 2)
    for match in url_match_dict:
        file_path = url_match_dict[match][1].replace("../", "")
        if src.index.get_item_by_path(file_path):
            file_path_list.append(file_path)
    return file_path_list
