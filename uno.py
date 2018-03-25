import time

from flask import Flask, render_template, send_from_directory, abort, Blueprint, request

from util import *

# 主蓝图和维护蓝图
uno = Blueprint("uno", __name__)
main = Blueprint("main", __name__)

app = Flask(__name__, static_folder=uno_static_dir_name)
# 自动重载jinja环境
app.jinja_env.auto_reload = True

# 绑定变量到jinja模板
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
app.jinja_env.globals["json_id_name"] = json_id_name
app.jinja_env.globals["json_title_name"] = json_title_name
app.jinja_env.globals["json_url_name"] = json_url_name
app.jinja_env.globals["json_date_name"] = json_date_name
app.jinja_env.globals["json_tags_name"] = json_tags_name
# 绑定函数到jinja模板
app.jinja_env.globals.update(get_static_file_url=get_static_file_url)
app.jinja_env.globals.update(get_bower_file_url=get_bower_file_url)


@app.errorhandler(404)
def error_page(error):
    return render_template('error.html', title="%d %s" % (error.code, error.name), data=error.description), error.code


# 首页，展示固定索引列表里的文件，如果没有就展示首页背景图
@uno.route('/')
def index():
    return render_template('home.html', fixed_articles=get_fixed_articles())


# 索引页，通过索引文件名访问，展示索引文件内容，可通过url参数搜索
@uno.route('/%s' % uno_index_file_name)
def index_file_page():
    search = [request.args.get('i', '').strip(),  # 搜索编号
              request.args.get('n', '').strip(),  # 搜索标题
              request.args.get('t', '').strip(),  # 搜索标签名
              request.args.get('d', '').strip()]  # 搜索日期
    search_index = [json_id_name, json_title_name, json_tags_name, json_date_name]
    # 传递给过滤器筛选
    data, max_tag_num = index_data_filter([[search_index[i], search[i]] for i in range(len(search)) if search[i]])
    return render_template('index.html', title="Index", data=data, max_tag_num=max_tag_num, no_sidebar=True)


# 文章和附件页，通过对应的目录名和哈希值访问，文章展示markdown渲染结果，附件直接展示源文件
@uno.route('/<any("%s", "%s"):dir_name>/<file_hash>' % (uno_articles_dir_name, uno_attachments_dir_name))
def article_page(dir_name, file_hash):
    # 判断哈希格式
    if len(file_hash) != 40 or not file_hash.isalnum():
        abort(404)
    # 在索引文件中查找对应哈希的文件信息
    item, item_path = get_item_by_url("/%s/%s" % (dir_name, file_hash))
    if not item:
        abort(404)
    # 判断文件是否存在
    item_abspath = os.path.join(get_articles_dir_abspath(), item_path)
    if not os.path.exists(item_abspath):
        abort(404)
    # 识别把文件加入忽略列表的url参数
    make_file_ignore_arg = request.args.get(uno_make_file_ignore_arg, "").strip()
    if make_file_ignore_arg == "1":
        # 加入忽略列表
        update_config_ignore_file_list(item_path, True)
        # 重建索引线程处理
        handle_thread(reindex_thread_limit, reindex_thread)
        abort(404)
    if dir_name == uno_articles_dir_name:
        with open(item_abspath, encoding='utf-8') as file_data:
            data = file_data.read()
        # 识别文章中的隐藏侧边栏标识
        no_sidebar = get_no_sidebar_flag(data)
        # 识别文章中的自定义css文件，获取自定义css文件url列表
        css_urls = get_custom_css(data)
        # 识别文章中的自定义js文件，获取自定义js文件url列表
        js_urls = get_custom_js(data)
        # markdown渲染
        data = render(data)
        # 去后缀
        title = os.path.splitext(item[json_title_name])[0]
        date = item[json_date_name]
        # 生成标签名列表(不含链接)
        tags = item[json_tags_name].keys()
        return render_template('article.html', title=title, data=data, date=date, tags=tags,
                               css_urls=css_urls, js_urls=js_urls, no_sidebar=no_sidebar)
    else:
        # 定向到源文件
        file_dir, file = os.path.split(item_abspath)
        return send_from_directory(file_dir, file)


# 重建索引线程限制
reindex_thread_limit = []


# 重建索引线程函数
def reindex_thread():
    # 执行重建索引命令并打印日志
    app.logger.info(os.popen(get_reindex_cmd()).read().rstrip())
    articles_dir_abspath = get_articles_dir_abspath()
    articles_block = {}
    attachments_block = {}
    # 遍历文章目录下所有文件和子目录
    for root, dirs, files in os.walk(articles_dir_abspath):
        # 截取相对路径
        path = root.split(uno_articles_dir_name)[-1].lstrip(os.path.sep).replace("\\", "/")
        # 排除忽略目录
        is_ignore = False
        for ignore_dir in uno_ignore_dir_list:
            if path.startswith(ignore_dir):
                is_ignore = True
                break
        if is_ignore:
            continue
        for file in files:
            # 组成文件路径
            file_path = "/".join([path, file]).lstrip("/")
            file_abspath = os.path.join(root, file)
            if not path.startswith(uno_attachments_dir_name):
                # 忽略无法以unicode编码的文件
                try:
                    with open(file_abspath, encoding='utf-8') as file_data:
                        data = file_data.read()
                except UnicodeDecodeError:
                    continue
                # 识别文章中的忽略文件标识，来判断如何更新忽略列表
                if get_ignore_flag(data):
                    update_config_ignore_file_list(file_path, True)
                # 识别文章中的取消忽略文件标识，来判断如何更新忽略列表
                if get_unignore_flag(data):
                    update_config_ignore_file_list(file_path, False)
            # 排除忽略文件
            if file_path in uno_ignore_file_list:
                continue
            group = re.search("(%s)" % uno_strip_prefix, file_path)
            if group:
                num = group.group(1).strip("-")
                title = re.sub(group.group(1), "", file_path)
            else:
                num = ""
                title = file_path
            if not path.startswith(uno_attachments_dir_name):
                # 从文件内容获取标签并生成标签列表
                tags = {tag: "/%s?t=%s" % (uno_index_file_name, tag) for tag in get_tags_flag(data)}
                # 从文件内容获取日期
                date = get_date_flag(data)
                url = "/%s/%s" % (uno_articles_dir_name, compute_digest_by_data(data))
                fixed = False
                if get_fixed_flag(data):
                    item = get_item_by_path(file_path)
                    if item:
                        url = item[json_url_name]
                    fixed = True
                articles_block[file_path] = {json_id_name: num, json_title_name: title, json_url_name: url,
                                             json_date_name: date, json_tags_name: tags, json_fixed_name: fixed}
            else:
                url = "/%s/%s" % (uno_attachments_dir_name, compute_digest_by_abspath(file_abspath))
                attachments_block[file_path] = {json_id_name: num, json_title_name: title, json_url_name: url}
    # 写入索引文件
    index_data = json.dumps([articles_block,
                             attachments_block], indent=4, )  # separators=(',', ':'))
    with open(os.path.join(articles_dir_abspath, uno_index_file_name), 'w', encoding='utf-8') as index_file:
        index_file.write(index_data)
    # 冷却
    time.sleep(uno_reindex_limit_time)


# 重建索引页，通过重建索引url名访问，另开线程执行操作，出于保密url原因返回404
@uno.route('/%s' % uno_reindex_url_name)
def reindex():
    # 重建索引线程处理
    handle_thread(reindex_thread_limit, reindex_thread)
    abort(404)


# 更新程序线程限制
update_thread_limit = []


# 更新程序线程函数
def update_thread():
    # 执行更新程序命令并打印日志
    app.logger.info(os.popen(get_update_cmd()).read().rstrip())
    # 冷却
    time.sleep(uno_update_limit_time)


# 更新程序页，通过更新程序url名访问，另开线程执行操作，出于保密url原因返回404
@uno.route('/%s' % uno_update_url_name)
def update():
    # 重建索引线程处理
    handle_thread(update_thread_limit, update_thread)
    abort(404)


# 维护页面，配置中开启维护模式后所有访问都会定向到这里
# noinspection PyUnusedLocal
@main.route('/', defaults={'path': ''})
@main.route('/<path:path>')
def catch_all(path):
    return render_template('maintenance.html')


# 注册蓝图
app.register_blueprint(main if uno_maintenance else uno)

if __name__ == '__main__':
    app.run(host=uno_host, port=uno_port, debug=uno_debug)
