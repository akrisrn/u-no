import time

from flask import Flask, render_template, send_from_directory, abort, Blueprint, request

from util import *

uno = Blueprint("uno", __name__)
main = Blueprint("main", __name__)

app = Flask(__name__, static_folder=uno_static_dir_name)
app.jinja_env.auto_reload = True

app.jinja_env.globals["site_name"] = uno_site_name

app.jinja_env.globals["favicon_img"] = uno_favicon_img
app.jinja_env.globals["to_top_img"] = uno_to_top_img
app.jinja_env.globals["background_img"] = uno_background_img

app.jinja_env.globals["index_show_text"] = uno_index_show_text
app.jinja_env.globals["sidebar_show_text"] = uno_sidebar_show_text
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
    return render_template('error.html', name="%d %s" % (error.code, error.name), content=error.description), error.code


@uno.route('/')
def index():
    return render_template('index.html')


@uno.route('/%s' % uno_sha1_file_name)
def sha1_file_page():
    search = [request.args.get('n', '').strip(),
              request.args.get('t', '').strip(),
              request.args.get('d', '').strip()]
    search_rule = [re.compile("\[.*?%s.*?\]\(/(?!%s)" % (search[0], uno_tags_url_name), re.I),
                   re.compile("\[.*?%s.*?\]\(/(?=%s)" % (search[1], uno_tags_url_name), re.I),
                   re.compile("\|\s%s.*?\s\|" % search[2], re.I)]
    rules = [search_rule[i] for i in range(len(search)) if search[i]]
    content = md(split_pref(content_filter(get_sha1_data(), rules)))
    return render_template('article.html', name=uno_sha1_file_name, content=content, show_tags=False, no_sidebar=True)


@uno.route('/<any("%s", "%s"):dir_name>/<file_sha1>' % (uno_articles_dir_name, uno_uploads_dir_name))
def article(dir_name, file_sha1):
    if not check_sha1(file_sha1):
        abort(404)
    group = re.search('\[(.*?)\]\(/%s/%s\)(.*?)\n' % (dir_name, file_sha1), get_sha1_data())
    if not group:
        abort(404)
    file_path = group.group(1)
    articles_dir_abspath = get_articles_dir_abspath()
    file_abspath = os.path.join(articles_dir_abspath, file_path)
    if not os.path.exists(file_abspath):
        abort(404)
    if dir_name == uno_articles_dir_name:
        with open(file_abspath, encoding='utf-8') as file:
            file_data = file.read()
        content = md(file_data)
        name = re.sub(uno_strip_prefix, "", os.path.splitext(file_path)[0])
        date_tags = group.group(2).split(" | ")[1:]
        date = date_tags[0]
        tags = [re.search("\[(.*?)\]\(.*?\)", tag).group(1) for tag in date_tags[1:]]
        return render_template('article.html', name=name, content=content, date=date, tags=tags, show_tags=True)
    else:
        file_dir, file = os.path.split(file_abspath)
        return send_from_directory(file_dir, file)


@uno.route('/%s/<tag_sha1>' % uno_tags_url_name)
def tag_page(tag_sha1):
    if not check_sha1(tag_sha1):
        abort(404)
    sha1_data = get_sha1_data()
    group = re.search('\s\|\s.*\[(.*?)\]\(/%s/%s\)' % (uno_tags_url_name, tag_sha1), sha1_data)
    if not group:
        abort(404)
    tag_name = group.group(1)
    new_sha1_data = ""
    max_tag_num = 0
    for data in sha1_data.split("\n"):
        if data.find("[%s]" % tag_name) != -1:
            new_sha1_data += data + "\n"
            tag_num = len(data.split(" | ")) - 1
            if tag_num > max_tag_num:
                max_tag_num = tag_num
    content = md(split_pref(get_sha1_data_table_header(max_tag_num - 1) + new_sha1_data))
    return render_template('article.html', name="Tag: %s" % tag_name, content=content, show_tags=False, no_sidebar=True)


reindex_thread_limit = []


def reindex_thread():
    app.logger.info(os.popen(get_reindex_cmd()).read().rstrip())
    articles_dir_abspath = get_articles_dir_abspath()
    sha1_data = ""
    max_tag_num = 0
    for root, dirs, files in os.walk(articles_dir_abspath):
        path = root.split(uno_articles_dir_name)[1]
        path = path[1:] if path.startswith(os.path.sep) else path
        if path.split(os.path.sep)[0] in uno_ignore_dir_list:
            continue
        tags_sha1_dict = {}
        dir_name = uno_uploads_dir_name if path.startswith(uno_uploads_dir_name) else uno_articles_dir_name
        if dir_name == uno_uploads_dir_name:
            sha1_data += "\n---\n| Title\n| -\n"
        for file in files:
            if file in uno_ignore_file_list:
                continue
            file_abspath = os.path.join(root, file)
            file_path = os.path.join(path, file).replace("\\", "/")
            tags_date_append = ""
            if dir_name != uno_uploads_dir_name:
                with open(file_abspath, encoding='utf-8') as article_data:
                    content = article_data.read()
                tags = []
                for tag in get_tags(content):
                    if tag not in tags_sha1_dict.keys():
                        tag_sha1 = sha1_digest_str(tag)
                        tags_sha1_dict[tag] = tag_sha1
                    else:
                        tag_sha1 = tags_sha1_dict[tag]
                    tags.append("[%s](/%s/%s)" % (tag, uno_tags_url_name, tag_sha1))
                tags_append = " | ".join(tags)
                if len(tags) > max_tag_num:
                    max_tag_num = len(tags)
                date_append = get_date(content)
                tags_date_append = " | ".join([date_append, tags_append])
            file_sha1_data = sha1_digest_file(file_abspath)
            if file_path in uno_fixed_file_list:
                group = re.search("\[%s\]\(/%s/(.*?)\)" % (file_path, dir_name), get_sha1_data())
                if group:
                    file_sha1_data = group.group(1)
            first = "[%s](/%s/%s)" % (file_path, dir_name, file_sha1_data)
            if dir_name == uno_uploads_dir_name:
                first = "| " + first
            sha1_data += (" | ".join([first, tags_date_append]) if tags_date_append else first) + "\n"
    sha1_data = get_sha1_data_table_header(max_tag_num) + sha1_data
    with open(os.path.join(articles_dir_abspath, uno_sha1_file_name), 'w', encoding='utf-8') as sha1_file:
        sha1_file.write(sha1_data)
    time.sleep(uno_reindex_limit_time)


@uno.route('/%s' % uno_reindex_url_name)
def reindex():
    handle_thread(reindex_thread_limit, reindex_thread)
    abort(404)


update_thread_limit = []


def update_thread():
    app.logger.info(os.popen(get_update_cmd()).read().rstrip())
    time.sleep(uno_update_limit_time)


@uno.route('/%s' % uno_update_url_name)
def update():
    handle_thread(update_thread_limit, update_thread)
    abort(404)


# noinspection PyUnusedLocal
@main.route('/', defaults={'path': ''})
@main.route('/<path:path>')
def catch_all(path):
    return render_template('maintenance.html')


app.register_blueprint(main if uno_maintenance else uno)

if __name__ == '__main__':
    app.run(host=uno_host, port=uno_port, debug=uno_debug)
