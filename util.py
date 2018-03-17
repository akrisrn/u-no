import hashlib
import os
import platform
import re

from flask import url_for
from markdown import markdown
from pymdownx import extra, mark, caret

from config import *


def is_windows():
    return True if platform.system() == "Windows" else False


def get_os_cmd_sep():
    return "&" if is_windows() else ";"


def md(text):
    return markdown(text, extensions=[
        extra.ExtraExtension(),
        mark.makeExtension(),
        caret.makeExtension(),
        'markdown.extensions.toc'
    ])


def sha1_digest_file(file_abspath):
    if os.path.isdir(file_abspath) or not os.path.exists(file_abspath):
        return ""
    with open(file_abspath, 'rb') as file:
        content = file.read()
    return hashlib.sha1(content).hexdigest()


def sha1_digest_str(string, random=True):
    return hashlib.sha1(string.encode("utf-8") + os.urandom(24) if random else "").hexdigest()


def get_root_abspath():
    return os.path.dirname(os.path.abspath(__file__)).split('util')[0]


def get_articles_dir_abspath():
    return os.path.join(get_root_abspath(), uno_articles_dir_name)


def get_static_dir_abspath():
    return os.path.join(get_root_abspath(), uno_static_dir_name)


def get_static_file_url(filename):
    return version(url_for("static", filename=filename))


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


def get_tags(article_abspath):
    with open(article_abspath, encoding='utf-8') as article:
        content = article.read()
    return render_tags(content, False)


def render_tags(content, clear_content=True):
    group = re.search("<<\s*Tag\((.*?)\)\s*>>", content)
    if not group:
        return (content, [uno_default_tag]) if clear_content else [uno_default_tag]
    tags = group.group(1)
    tags = re.sub("(\s|\"|\')", "", tags).split(",")
    if len(tags) == 1 and not tags[0]:
        tags = [uno_default_tag]
    return (re.sub("(<<\s*Tag\(.*?\)\s*>>)", "", content), tags) if clear_content else tags
