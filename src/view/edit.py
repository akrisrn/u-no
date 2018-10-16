from flask import Blueprint, redirect, url_for

from util import update_config_ignore_file_list

edit = Blueprint("edit", __name__)


@edit.route('/ignore/<path:item_path>')
def ignore(item_path, is_ignore=True):
    # 加入忽略列表
    update_config_ignore_file_list(item_path, is_ignore)
    return redirect(url_for('main.reindex_page'))


@edit.route('/unignore/<path:item_path>')
def unignore(item_path):
    return ignore(item_path, False)
