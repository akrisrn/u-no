import os
import re

from flask import Blueprint, redirect, url_for, abort

from cache import get_file_cache
from const import flag_notags, flag_highlight, flag_top, flag_fixed, flag_unignore, flag_ignore
from flag import get_flag_regexp
from util import update_config_ignore_file_list, get_articles_dir_abspath

edit = Blueprint("edit", __name__)


def toggle_flag(item_path, flag, is_on):
    item_abspath = os.path.join(get_articles_dir_abspath(), item_path)
    if not os.path.exists(item_abspath):
        abort(404)
    try:
        item_data = get_file_cache(item_abspath)
    except UnicodeDecodeError:
        return
    flag_regexp = get_flag_regexp(flag)
    if re.search(flag_regexp, item_data):
        if is_on:
            return
        item_data = re.sub(flag_regexp, "", item_data)
    else:
        if not is_on:
            return
        item_data += "\n<<%s()>>" % flag
    with open(item_abspath, "w", encoding='utf-8') as item_file:
        item_file.write(item_data)


@edit.route('/%s/<path:item_path>' % flag_ignore)
def ignore(item_path, is_ignore=True):
    # 加入忽略列表
    update_config_ignore_file_list(item_path, is_ignore)
    toggle_flag(item_path, flag_unignore if is_ignore else flag_ignore, False)
    return redirect(url_for('main.reindex_page'))


@edit.route('/%s/<path:item_path>' % flag_unignore)
def unignore(item_path):
    return ignore(item_path, False)
