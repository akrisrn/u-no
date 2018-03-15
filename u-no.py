import re

from flask import Flask, render_template, send_from_directory, abort

from util import *

app = Flask(__name__)
app.jinja_env.auto_reload = True
app.jinja_env.filters['version'] = version
app.jinja_env.globals.update(get_static_file_url=get_static_file_url)
app.jinja_env.globals.update(now_year=now_year)


@app.errorhandler(404)
def error_page(error):
    return render_template('error.html', error=error), 404


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/%s' % sha1_file_name)
def sha1_file_page():
    with open(os.path.join(get_articles_dir_abspath(), sha1_file_name), encoding='utf-8') as sha1_file:
        sha1_data = sha1_file.read()
    new_sha1_data = ""
    another_sha1_data = ""
    for data in sha1_data.split("\n"):
        data = data.replace("\\", "/")
        if data.startswith("- [%s" % uploads_dir_name):
            another_sha1_data += data + "\n"
        else:
            new_sha1_data += data + "\n"
    new_sha1_data += "---\n" + another_sha1_data
    sha1_data = md(new_sha1_data)
    return render_template('article.html', name=sha1_file_name, content=sha1_data)


@app.route('/<any("%s", "%s"):dir_name>/<file_sha1>' % (articles_dir_name, uploads_dir_name))
def article(dir_name, file_sha1):
    if len(file_sha1) != 40 or not file_sha1.isalnum():
        abort(404)
    articles_dir_abspath = get_articles_dir_abspath()
    with open(os.path.join(articles_dir_abspath, sha1_file_name), encoding='utf-8') as sha1_file:
        sha1_data = sha1_file.read()
    group = re.search('- \[(.*?)\]\(/%s/%s\)\n' % (dir_name, file_sha1), sha1_data)
    if not group:
        abort(404)
    file_path = group.group(1)
    if dir_name == articles_dir_name:
        with open(os.path.join(articles_dir_abspath, file_path), encoding='utf-8') as file:
            file_data = file.read()
        file_path = file_path.replace("\\", "/")
        file_data = md(file_data.replace("\r\n", "\n"))
        return render_template('article.html', name=file_path, content=file_data)
    else:
        file_dir, file = os.path.split(os.path.join(articles_dir_abspath, file_path))
        return send_from_directory(file_dir, file)


@app.route('/%s' % reindex_url_name)
def reindex():
    with os.popen(get_sync_cmd()) as p:
        for line in p.readlines():
            print(line, end="")
    articles_dir_abspath = get_articles_dir_abspath()
    sha1_data = ""
    for root, dirs, files in os.walk(articles_dir_abspath):
        path = root.split(articles_dir_name)[1]
        path = path[1:] if path.startswith(os.path.sep) else path
        if path.split(os.path.sep)[0] in ignore_dir_list:
            continue
        for file in files:
            if file in ignore_file_list:
                continue
            file_abspath = os.path.join(root, file)
            file_path = os.path.join(path, file)
            dir_name = uploads_dir_name if path.startswith(uploads_dir_name) else articles_dir_name
            sha1_data += "- [%s](/%s/%s)\n" % (file_path, dir_name, sha1_digest(file_abspath))
    with open(os.path.join(articles_dir_abspath, sha1_file_name), 'w', encoding='utf-8') as sha1_file:
        sha1_file.write(sha1_data)
    abort(404)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(get_static_dir_abspath(), "favicon.ico")


if __name__ == '__main__':
    app.run(host=uno_host, port=uno_port, debug=uno_debug)
