from flask import Flask, render_template

from config import uno_debug, uno_port, uno_host, uno_error_cover_height, uno_error_cover_img, \
    uno_sidebar_cover_height, uno_sidebar_cover_c_img, uno_sidebar_cover_b_img, uno_sidebar_cover_a_img, \
    uno_index_cover_height, uno_index_cover_img, uno_markdown_toc_text, uno_copyright_show_text, \
    uno_sidebar_show_text, uno_index_show_text, uno_background_img, uno_favicon_img, uno_site_name, uno_maintenance, \
    uno_static_dir_name
from src.index import index_url_key, index_title_key, index_id_key, index_tags_key, index_date_key
from src.util import get_static_file_url, get_static_lib_url
from src.view.main import main
from src.view.maintenance import maintenance

app = Flask(__name__, static_folder=uno_static_dir_name)
# 注册蓝图
app.register_blueprint(maintenance if uno_maintenance else main)

# 自动重载jinja环境
app.jinja_env.auto_reload = True
# 绑定变量到jinja模板
app.jinja_env.globals["site_name"] = uno_site_name
app.jinja_env.globals["favicon_img"] = uno_favicon_img
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
app.jinja_env.globals["index_id_name"] = index_id_key
app.jinja_env.globals["index_title_name"] = index_title_key
app.jinja_env.globals["index_url_name"] = index_url_key
app.jinja_env.globals["index_date_name"] = index_date_key
app.jinja_env.globals["index_tags_name"] = index_tags_key
# 绑定函数到jinja模板
app.jinja_env.globals.update(get_static_file_url=get_static_file_url)
app.jinja_env.globals.update(get_static_lib_url=get_static_lib_url)


@app.errorhandler(404)
def error_page(error):
    return render_template('error.html', title="%d %s" % (error.code, error.name), data=error.description), error.code


if __name__ == '__main__':
    app.run(host=uno_host, port=uno_port, debug=uno_debug)
