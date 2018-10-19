import os
import re

from flask import Blueprint, abort, request, jsonify, url_for, redirect, render_template

from cache import get_file_cache
from const import flag_notags, flag_highlight, flag_top, flag_fixed, flag_unignore, flag_ignore, flag_tag, flag_date
from flag import get_flag_regexp
from index import reindex
from util import update_config_ignore_file_list, get_articles_dir_abspath

edit = Blueprint("edit", __name__)


def toggle_flag(item_path, flag, is_on, data=None, force_reindex=False, force_update=False):
    def toggle():
        item_abspath = os.path.join(get_articles_dir_abspath(), item_path)
        if not os.path.exists(item_abspath):
            abort(404)
        try:
            item_data = get_file_cache(item_abspath)
        except UnicodeDecodeError:
            return False
        flag_regexp = get_flag_regexp(flag)
        group = re.search(flag_regexp, item_data)
        if group:
            if not force_update and is_on:
                return False
            sub_text = ""
            if data is not None:
                if data == group.group(2):
                    return False
                sub_text = "%s%s%s" % (group.group(1), data, group.group(3))
            item_data = re.sub(flag_regexp, sub_text, item_data)
        else:
            if not force_update and not is_on:
                return False
            item_data += "%s<<%s(%s)>>" % ("" if item_data.endswith("\n") else "\n", flag, "" if data is None else data)
        with open(item_abspath, "w", encoding='utf-8') as item_file:
            item_file.write(item_data)
        return True

    is_reindex = toggle()
    if force_reindex or is_reindex:
        reindex()
    return is_reindex


@edit.route('/%s/<path:item_path>' % flag_ignore)
def ignore(item_path, is_ignore=True):
    # 加入忽略列表
    update_config_ignore_file_list(item_path, is_ignore)
    toggle_flag(item_path, flag_unignore if is_ignore else flag_ignore, False, None, True)
    return redirect(url_for('main.index_page'))


@edit.route('/%s/<path:item_path>' % flag_unignore)
def unignore(item_path):
    return ignore(item_path, False)


@edit.route('/%s/<path:item_path>' % flag_fixed)
def fixed(item_path, is_fixed=True):
    return jsonify(toggle_flag(item_path, flag_fixed, is_fixed))


@edit.route('/un%s/<path:item_path>' % flag_fixed)
def unfixed(item_path):
    return fixed(item_path, False)


@edit.route('/%s/<path:item_path>' % flag_top)
def top(item_path, is_top=True):
    return jsonify(toggle_flag(item_path, flag_top, is_top))


@edit.route('/un%s/<path:item_path>' % flag_top)
def untop(item_path):
    return top(item_path, False)


@edit.route('/%s/<path:item_path>' % flag_highlight)
def highlight(item_path, is_highlight=True):
    return jsonify(toggle_flag(item_path, flag_highlight, is_highlight))


@edit.route('/un%s/<path:item_path>' % flag_highlight)
def unhighlight(item_path):
    return highlight(item_path, False)


@edit.route('/%s/<path:item_path>' % flag_notags)
def notags(item_path, is_notags=True):
    return jsonify(toggle_flag(item_path, flag_notags, is_notags))


@edit.route('/un%s/<path:item_path>' % flag_notags)
def unnotags(item_path):
    return notags(item_path, False)


@edit.route('/%s/<path:item_path>' % flag_tag)
def tag(item_path):
    return jsonify(toggle_flag(item_path, flag_tag, False, request.args.get("data", ""), False, True))


@edit.route('/%s/<path:item_path>' % flag_date)
def date(item_path):
    return jsonify(toggle_flag(item_path, flag_date, False, request.args.get("data", ""), False, True))


@edit.route('/article/<path:item_path>')
def article(item_path):
    return render_template('edit.html', title=item_path)
