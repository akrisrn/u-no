import hashlib
import os
import platform

from flask import url_for
from markdown import markdown
from pymdownx import extra, mark, caret

from config import *


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
    return url_for("static", filename=filename)


def version(url):
    ver = uno_version if uno_version and not uno_debug else sha1_digest(os.path.join(get_root_abspath(), url[1:]))
    return "%s?v=%s" % (url, ver)


def get_sync_cmd():
    return "cd %s %s git pull" % (uno_articles_dir_name, "&" if platform.system() == "Windows" else ";")
