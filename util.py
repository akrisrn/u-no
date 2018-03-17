import hashlib
import os
import platform

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


def sha1_digest(file):
    if os.path.isdir(file) or not os.path.exists(file):
        return ""
    with open(file, 'rb') as file:
        content = file.read()
    return hashlib.sha1(content).hexdigest()


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
    ver = uno_version if uno_version and not uno_debug else sha1_digest(os.path.join(get_root_abspath(), url[1:]))
    return "%s?v=%s" % (url, ver)


def get_reindex_cmd(dir_abspath=get_articles_dir_abspath()):
    return get_os_cmd_sep().join(["cd %s" % dir_abspath, "git pull"])


def get_update_cmd():
    restart_cmd = "" if is_windows() else "systemctl restart %s" % uno_update_service_name
    return get_os_cmd_sep().join([get_reindex_cmd(get_root_abspath()), restart_cmd])
