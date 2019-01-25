import os
import re

from flask import Blueprint, abort, request, jsonify, url_for, redirect, render_template

from ..cache import get_file_cache
from ..const import flag_notags, flag_highlight, flag_top, flag_fixed, flag_unignore, flag_ignore, flag_tag, \
    flag_date, index_url_key, articles_url_name
from ..flag import get_flag_regexp
from ..index import reindex, get_item_by_path
from ..util import update_config_ignore_file_list, get_articles_dir_abspath

edit = Blueprint("edit", __name__)


def toggle_flag(item_path, flag, is_on, data=None, force_reindex=False, force_update=False, check_index=True):
    def toggle():
        if check_index and not get_item_by_path(item_path) if item_path else None:
            abort(404)
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
                sub_text = "%s%s%s" % (group.group(1).rstrip(),
                                       "" if data == "" else " " + data, group.group(3).lstrip())
            item_data = re.sub(flag_regexp, sub_text, item_data)
        else:
            if not force_update and not is_on:
                return False
            item_data += "%s{{%s%s}}" % ("" if item_data.endswith("\n") else "\n", flag,
                                         "" if data is None or data == "" else " " + data)
        with open(item_abspath, "w", encoding='utf-8') as item_file:
            item_file.write(item_data)
        return True

    is_reindex = toggle()
    if force_reindex or is_reindex:
        reindex()
    return is_reindex


@edit.route('/%s' % flag_ignore)
def ignore(item_path=None, is_ignore=True):
    if not item_path:
        item_path = request.args.get("item_path")
    if item_path:
        # 加入忽略列表
        update_config_ignore_file_list(item_path, is_ignore)
        toggle_flag(item_path, flag_unignore if is_ignore else flag_ignore, False, None, True, False, False)
    return redirect(url_for('main.index_page'))


@edit.route('/%s' % flag_unignore)
def unignore():
    return ignore(request.args.get("item_path"), False)


@edit.route('/%s' % flag_fixed)
def fixed(item_path=None, is_fixed=True):
    if not item_path:
        item_path = request.args.get("item_path")
    return jsonify(toggle_flag(item_path, flag_fixed, is_fixed))


@edit.route('/un%s' % flag_fixed)
def unfixed():
    return fixed(request.args.get("item_path"), False)


@edit.route('/%s' % flag_top)
def top(item_path=None, is_top=True):
    if not item_path:
        item_path = request.args.get("item_path")
    return jsonify(toggle_flag(item_path, flag_top, is_top))


@edit.route('/un%s' % flag_top)
def untop():
    return top(request.args.get("item_path"), False)


@edit.route('/%s' % flag_highlight)
def highlight(item_path=None, is_highlight=True):
    if not item_path:
        item_path = request.args.get("item_path")
    return jsonify(toggle_flag(item_path, flag_highlight, is_highlight))


@edit.route('/un%s' % flag_highlight)
def unhighlight():
    return highlight(request.args.get("item_path"), False)


@edit.route('/%s' % flag_notags)
def notags(item_path=None, is_notags=True):
    if not item_path:
        item_path = request.args.get("item_path")
    return jsonify(toggle_flag(item_path, flag_notags, is_notags))


@edit.route('/un%s' % flag_notags)
def unnotags():
    return notags(request.args.get("item_path"), False)


@edit.route('/%s' % flag_tag)
def tag():
    return jsonify(toggle_flag(request.args.get("item_path"),
                               flag_tag, False, request.args.get("data", ""), False, True))


@edit.route('/%s' % flag_date)
def date():
    return jsonify(toggle_flag(request.args.get("item_path"),
                               flag_date, False, request.args.get("data", ""), False, True))


@edit.route('/%s' % articles_url_name, methods=["GET", "POST"])
def article():
    item_path = request.args.get("item_path")
    item = get_item_by_path(item_path) if item_path else None
    if not item:
        abort(404)
    item_abspath = os.path.join(get_articles_dir_abspath(), item_path)
    if not os.path.exists(item_abspath):
        abort(404)
    if request.method == "POST":
        with open(item_abspath, "w", encoding='utf-8') as item_file:
            item_file.write(request.form["data"])
        reindex()
        return jsonify(get_item_by_path(item_path)[index_url_key])
    else:
        return render_template('edit.html', title=item_path, url=item[index_url_key], data=get_file_cache(item_abspath))
