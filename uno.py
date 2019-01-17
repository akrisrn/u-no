from flask import Flask, render_template

from src.const import index_url_key, index_title_key, index_id_key, index_tags_key, index_date_key, index_notags_key, \
    index_highlight_key, index_fixed_key, index_top_key, index_path_key, index_bereferenced_key
from src.util import get_static_file_url, get_static_lib_url, get_plugins_urls, get_plugin_urls, format_date
from src.view.edit import edit
from src.view.main import main

app = Flask(__name__)
# 载入配置
app.config.from_pyfile("config.py")
app.config["IS_FREEZE"] = False
# 指定静态文件目录
app.static_folder = app.config["STATIC_DIR_NAME"]
# 注册蓝图
app.register_blueprint(main)
app.register_blueprint(edit, url_prefix="/edit")

# 自动重载jinja环境
app.jinja_env.auto_reload = True
# 绑定变量到jinja模板
app.jinja_env.globals["site_name"] = app.config["SITE_NAME"]
app.jinja_env.globals["default_tag"] = app.config["DEFAULT_TAG"]
app.jinja_env.globals["page_size"] = app.config["PAGE_SIZE"]
app.jinja_env.globals["index_id_key"] = index_id_key
app.jinja_env.globals["index_title_key"] = index_title_key
app.jinja_env.globals["index_path_key"] = index_path_key
app.jinja_env.globals["index_url_key"] = index_url_key
app.jinja_env.globals["index_date_key"] = index_date_key
app.jinja_env.globals["index_tags_key"] = index_tags_key
app.jinja_env.globals["index_notags_key"] = index_notags_key
app.jinja_env.globals["index_highlight_key"] = index_highlight_key
app.jinja_env.globals["index_fixed_key"] = index_fixed_key
app.jinja_env.globals["index_top_key"] = index_top_key
app.jinja_env.globals["index_bereferenced_key"] = index_bereferenced_key
# 绑定函数到jinja模板
app.jinja_env.globals.update(format_date=format_date)
app.jinja_env.globals.update(get_static_file_url=get_static_file_url)
app.jinja_env.globals.update(get_static_lib_url=get_static_lib_url)
app.jinja_env.globals.update(get_plugin_urls=get_plugin_urls)
app.jinja_env.globals.update(get_plugins_urls=get_plugins_urls)
# jinja循环控制扩展
app.jinja_env.add_extension('jinja2.ext.loopcontrols')


@app.errorhandler(404)
def error_page(error):
    return render_template('error.html', title="%d %s" % (error.code, error.name)), error.code


if __name__ == '__main__':
    app.run(host=app.config["HOST"], port=app.config["PORT"], debug=app.config["DEBUG"])
