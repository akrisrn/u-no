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


def is_windows():
    return True if platform.system() == "Windows" else False


def get_os_cmd_sep():
    return "&" if is_windows() else ";"


def get_url_from_file_path(file_path):
    group = re.search(regexp_join("\[%s\]\((.*?)\)", file_path), get_sha1_data())
    if group:
        return group.group(1)
    return ""


# noinspection SpellCheckingInspection
def md(text):
    text = re.sub("(\r|<<.*?>>)", "", text)
    if len(re.findall("#+\s+.*", text)) >= 3:
        text = "[TOC]\n\n" + text
    for group in re.finditer("\[(.*?)\]\((.*?)\)\+", text):
        des = group.group(1)
        file_path = group.group(2)
        url = get_url_from_file_path(file_path)
        if url:
            text = re.sub(regexp_join("\[%s\]\(%s\)\+", des, file_path), "[%s](%s)" % (des, url), text)
    num = 1
    for group in re.finditer("\|\s*(:?-:?|1\.)\s*(.*)", text):
        append = group.group(2)
        if group.group(1).strip(":") == "-":
            num = 1
        else:
            text = re.sub(regexp_join("\|\s*1\.\s*%s", append), "| %d %s" % (num, append), text, 1)
            num += 1
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
    extension_config = {
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
            "hardbreak": True,
            "nbsp": True
        },
        "pymdownx.highlight": {
            "noclasses": True,
            "pygments_style": "friendly"
        },
        "pymdownx.magiclink": {
            "repo_url_shortener": True,
            "repo_url_shorthand": True,
            "social_url_shorthand": True,
        }
    }
    return markdown(text, extensions, extension_config)


def sha1_digest_file(file_abspath):
    if os.path.isdir(file_abspath) or not os.path.exists(file_abspath):
        return ""
    with open(file_abspath, 'rb') as file:
        content = file.read()
    return hashlib.sha1(content).hexdigest()


def sha1_digest_content(content):
    return hashlib.sha1(content.encode("utf-8")).hexdigest()


def check_sha1(sha1):
    if len(sha1) != 40 or not sha1.isalnum():
        return False
    return True


def get_sha1_data():
    sha1_file_path = os.path.join(get_articles_dir_abspath(), uno_sha1_file_name)
    if os.path.exists(sha1_file_path):
        with open(sha1_file_path, encoding='utf-8') as sha1_file:
            sha1_data = sha1_file.read()
        return sha1_data
    else:
        return None


def get_root_abspath():
    return os.path.dirname(os.path.abspath(__file__)).split('util')[0]


def get_articles_dir_abspath():
    return os.path.join(get_root_abspath(), uno_articles_dir_name)


def get_uploads_dir_abspath():
    return os.path.join(get_root_abspath(), uno_articles_dir_name, uno_uploads_dir_name)


def get_static_dir_abspath():
    return os.path.join(get_root_abspath(), uno_static_dir_name)


def get_static_file_url(filename, have_version=True):
    if have_version:
        return version(url_for("static", filename=filename))
    return url_for("static", filename=filename)


def get_bower_file_url(filename):
    return url_for("static", filename="bower_components/%s" % filename)


def version(url):
    ver = uno_version if uno_version and not uno_debug else sha1_digest_file(os.path.join(get_root_abspath(), url[1:]))
    return "%s?v=%s" % (url, ver)


def get_reindex_cmd(dir_abspath=get_articles_dir_abspath()):
    return get_os_cmd_sep().join(["cd %s" % dir_abspath, "git pull"])


def get_update_cmd():
    restart_cmd = "" if is_windows() else "systemctl restart %s" % uno_update_service_name
    return get_os_cmd_sep().join([get_reindex_cmd(get_root_abspath()), restart_cmd])


def clear_text(text):
    return re.sub("(\s|\"|\')", "", text)


def get_flag_regexp(flag):
    return re.compile(regexp_join("<<\s*%s\((.*?)\)\s*>>", flag), re.I)


def get_tags(content):
    default_tag = [uno_default_tag]
    group = re.search(get_flag_regexp("tag"), content)
    if not group:
        return default_tag
    tags = [tag for tag in clear_text(group.group(1)).split(",") if tag]
    if not tags:
        return default_tag
    return tags


def get_date(content):
    group = re.search(get_flag_regexp("date"), content)
    if not group:
        return ""
    date = str(clear_text(group.group(1)).split(",")[0])
    try:
        date = datetime.strptime(date, "%y-%m-%d").strftime("%Y.%m.%d")
    except ValueError:
        return ""
    return date


def get_no_sidebar(content):
    return re.search(get_flag_regexp("nosidebar"), content)


def get_custom_css(content, custom_type="css"):
    group = re.search(get_flag_regexp(custom_type), content)
    if not group:
        return []
    css_urls = []
    for css_path in clear_text(group.group(1)).split(","):
        if css_path:
            css_url = get_url_from_file_path(css_path)
            if css_url:
                css_urls.append(css_url)
    return css_urls


def get_custom_js(content):
    return get_custom_css(content, "js")


def get_sha1_data_table_header(tag_num):
    table_header = " | ".join(["Name", "Date", " | ".join(["Tag-%d" % (i + 1) for i in range(tag_num)])]) + "\n"
    table_format = " | ".join(["-"] * (tag_num + 2)) + "\n"
    return table_header + table_format


def handle_thread(thread_limit_list, target):
    if thread_limit_list and not thread_limit_list[0].is_alive():
        thread_limit_list.clear()
    if not thread_limit_list:
        thread_limit_list.append(Thread(target=target))
        thread_limit_list[0].start()


def split_pref(content):
    new_content = ""
    line_num = 1
    if content.find("---") != -1:
        blocks = content.split("---")
        article_block = blocks[0]
        uploads_block = blocks[1]
    else:
        article_block = content
        uploads_block = ""
    for data in article_block.split("\n"):
        if line_num == 1:
            new_content += "No. | " + data + "\n"
        elif line_num == 2:
            new_content += "- | " + data + "\n"
        else:
            group = re.search("\[(%s)(.*?)\]" % uno_strip_prefix, data)
            if group:
                rep = "%s | [%s]" % (group.group(1).strip("-"), os.path.splitext(group.group(2))[0])
                new_content += re.sub("\[%s.*?\]" % uno_strip_prefix, rep, data) + "\n"
            else:
                if data:
                    new_content += " | " + data + "\n"
        line_num += 1
    new_content += "\n---" + uploads_block if uploads_block else ""
    return new_content


def content_filter(content, rules):
    if not rules:
        return content
    new_content = ""
    max_tag_num = 0
    for line in content.split("\n"):
        is_find = True
        for rule in rules:
            if not re.search(rule, line):
                is_find = False
                break
        if is_find:
            new_content += line + "\n"
            max_tag_num = max(len(line.split(" | ")) - 2, max_tag_num)
    return get_sha1_data_table_header(max_tag_num) + new_content


def regexp_join(regexp_str, *args):
    args = list(args)
    special_char = ["\\", "$", "(", ")", "*", "+", ".", "[", "]", "?", "^", "{", "}", "|"]
    for i in range(len(args)):
        for char in special_char:
            if args[i].find(char) != -1:
                args[i] = args[i].replace(char, "\\%s" % char)
    return regexp_str % tuple(args)


def update_config_fixed_file_list(file_path, is_add):
    if is_add is True and file_path not in uno_fixed_file_list:
        uno_fixed_file_list.append(file_path)
    elif is_add is False and file_path in uno_fixed_file_list:
        uno_fixed_file_list.remove(file_path)
    else:
        return None
    config_path = os.path.join(get_root_abspath(), "config.py")
    with open(config_path, encoding="utf-8") as config_file:
        config_data = config_file.read()
    config_data = re.sub("uno_fixed_file_list\s*=\s*\[.*?\]",
                         "uno_fixed_file_list = %s" % uno_fixed_file_list, config_data)
    with open(config_path, "w", encoding="utf-8") as config_file:
        config_file.write(config_data)
