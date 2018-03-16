import logging
import re
from logging import FileHandler, Formatter

from flask import Flask, render_template, send_from_directory, abort, Blueprint

from util import *

uno = Blueprint("uno", __name__)
main = Blueprint("main", __name__)

app = Flask(__name__, static_folder=uno_static_dir_name)
app.jinja_env.auto_reload = True

app.jinja_env.globals["site_name"] = uno_site_name

app.jinja_env.globals["favicon_img"] = uno_favicon_img
app.jinja_env.globals["to_top_img"] = uno_to_top_img
app.jinja_env.globals["background_img"] = uno_background_img

app.jinja_env.globals["font_file"] = uno_font_file
app.jinja_env.globals["font_type"] = uno_font_type
app.jinja_env.globals["font_name"] = uno_font_name

app.jinja_env.globals["index_show_text"] = uno_index_show_text
app.jinja_env.globals["sidebar_show_text"] = uno_sidebar_show_text
app.jinja_env.globals["error_show_text"] = uno_error_show_text
app.jinja_env.globals["error_title_show_text"] = uno_error_title_show_text
app.jinja_env.globals["copyright_show_text"] = uno_copyright_show_text
app.jinja_env.globals["markdown_toc_text"] = uno_markdown_toc_text

app.jinja_env.globals["index_cover_img"] = uno_index_cover_img
app.jinja_env.globals["index_cover_height"] = uno_index_cover_height
app.jinja_env.globals["sidebar_cover_a_img"] = uno_sidebar_cover_a_img
app.jinja_env.globals["sidebar_cover_b_img"] = uno_sidebar_cover_b_img
app.jinja_env.globals["sidebar_cover_c_img"] = uno_sidebar_cover_c_img
app.jinja_env.globals["sidebar_cover_height"] = uno_sidebar_cover_height
app.jinja_env.globals["error_cover_img"] = uno_error_cover_img
app.jinja_env.globals["error_cover_height"] = uno_error_cover_height

app.jinja_env.globals.update(get_static_file_url=get_static_file_url)
app.jinja_env.globals.update(get_bower_file_url=get_bower_file_url)


@app.errorhandler(403)
@app.errorhandler(404)
@app.errorhandler(500)
def error_page(error):
    return render_template('error.html', error=error), error.code


@uno.route('/')
def index():
    return render_template('index.html')


@uno.route('/%s' % uno_sha1_file_name)
def sha1_file_page():
    with open(os.path.join(get_articles_dir_abspath(), uno_sha1_file_name), encoding='utf-8') as sha1_file:
        sha1_data = sha1_file.read()
    new_sha1_data = ""
    another_sha1_data = ""
    for data in sha1_data.split("\n"):
        data = data.replace("\\", "/")
        if data.startswith("- [%s" % uno_uploads_dir_name):
            another_sha1_data += data + "\n"
        else:
            new_sha1_data += data + "\n"
    new_sha1_data += "---\n" + another_sha1_data
    sha1_data = md(new_sha1_data)
    return render_template('article.html', name=uno_sha1_file_name, content=sha1_data)


@uno.route('/<any("%s", "%s"):dir_name>/<file_sha1>' % (uno_articles_dir_name, uno_uploads_dir_name))
def article(dir_name, file_sha1):
    if len(file_sha1) != 40 or not file_sha1.isalnum():
        abort(404)
    articles_dir_abspath = get_articles_dir_abspath()
    with open(os.path.join(articles_dir_abspath, uno_sha1_file_name), encoding='utf-8') as sha1_file:
        sha1_data = sha1_file.read()
    group = re.search('- \[(.*?)\]\(/%s/%s\)\n' % (dir_name, file_sha1), sha1_data)
    if not group:
        abort(404)
    file_path = group.group(1)
    if dir_name == uno_articles_dir_name:
        with open(os.path.join(articles_dir_abspath, file_path), encoding='utf-8') as file:
            file_data = file.read()
        file_path = file_path.replace("\\", "/")
        file_data = md(file_data.replace("\r\n", "\n"))
        return render_template('article.html', name=file_path, content=file_data)
    else:
        file_dir, file = os.path.split(os.path.join(articles_dir_abspath, file_path))
        return send_from_directory(file_dir, file)


@uno.route('/%s' % uno_reindex_url_name)
def reindex():
    with os.popen(get_sync_cmd()) as p:
        app.logger.info(p.read().rstrip())
    articles_dir_abspath = get_articles_dir_abspath()
    sha1_data = ""
    for root, dirs, files in os.walk(articles_dir_abspath):
        path = root.split(uno_articles_dir_name)[1]
        path = path[1:] if path.startswith(os.path.sep) else path
        if path.split(os.path.sep)[0] in uno_ignore_dir_list:
            continue
        for file in files:
            if file in uno_ignore_file_list:
                continue
            file_abspath = os.path.join(root, file)
            file_path = os.path.join(path, file)
            dir_name = uno_uploads_dir_name if path.startswith(uno_uploads_dir_name) else uno_articles_dir_name
            sha1_data += "- [%s](/%s/%s)\n" % (file_path, dir_name, sha1_digest(file_abspath))
    with open(os.path.join(articles_dir_abspath, uno_sha1_file_name), 'w', encoding='utf-8') as sha1_file:
        sha1_file.write(sha1_data)
    abort(404)


# noinspection PyUnusedLocal
@main.route('/', defaults={'path': ''})
@main.route('/<path:path>')
def catch_all(path):
    return render_template('maintenance.html')


if __name__ == '__main__':
    handler = FileHandler(uno_log_file_name, encoding='UTF-8')
    handler.setLevel(logging.DEBUG)
    formatter = Formatter('%(asctime)s丨%(levelname)s丨%(filename)s丨%(funcName)s丨%(lineno)s丨%(message)s')
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.register_blueprint(main if uno_maintenance else uno)
    app.run(host=uno_host, port=uno_port, debug=uno_debug)
