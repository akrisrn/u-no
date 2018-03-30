from flask import Flask, render_template

from config import uno_debug, uno_port, uno_host, uno_site_name, uno_static_dir_name
from src.index import index_url_key, index_title_key, index_id_key, index_tags_key, index_date_key, \
    get_about_article_url
from src.util import get_static_file_url, get_static_lib_url
from src.view.main import main

app = Flask(__name__, static_folder=uno_static_dir_name)
# 注册蓝图
app.register_blueprint(main)

# 自动重载jinja环境
app.jinja_env.auto_reload = True
# 绑定变量到jinja模板
app.jinja_env.globals["site_name"] = uno_site_name
app.jinja_env.globals["index_id_name"] = index_id_key
app.jinja_env.globals["index_title_name"] = index_title_key
app.jinja_env.globals["index_url_name"] = index_url_key
app.jinja_env.globals["index_date_name"] = index_date_key
app.jinja_env.globals["index_tags_name"] = index_tags_key
# 绑定函数到jinja模板
app.jinja_env.globals.update(get_static_file_url=get_static_file_url)
app.jinja_env.globals.update(get_static_lib_url=get_static_lib_url)
app.jinja_env.globals.update(get_about_article_url=get_about_article_url)


@app.errorhandler(404)
def error_page(error):
    return render_template('error.html', title="%d %s" % (error.code, error.name)), error.code


if __name__ == '__main__':
    app.run(host=uno_host, port=uno_port, debug=uno_debug)
