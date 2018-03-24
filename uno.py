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
# 绑定函数到jinja模板
app.jinja_env.globals.update(get_static_file_url=get_static_file_url)
app.jinja_env.globals.update(get_bower_file_url=get_bower_file_url)


@app.errorhandler(404)
def error_page(error):
    return render_template('error.html', name="%d %s" % (error.code, error.name), content=error.description), error.code


# 首页，展示固定索引列表里的文件，如果没有就展示首页背景图
@uno.route('/')
def index():
    fixed_files = []
    sha1_data = get_sha1_data()
    if sha1_data:
        for file_path in uno_fixed_file_list:
            # 从索引文件中取出文件信息
            group = re.search(regexp_join("\[%s\]\((/%s/.*?)\)(.*?)\n", file_path, uno_articles_dir_name), sha1_data)
            if group:
                # 去前缀和后缀
                file_name = re.sub(uno_strip_prefix, "", os.path.splitext(file_path)[0])
                file_url = group.group(1)
                date_tags = group.group(2).split(" | ")[1:]
                date = date_tags[0]
                # 生成标签名列表(不含链接)
                tags = [re.search("\[(.*?)\]\(.*?\)", tag).group(1) for tag in date_tags[1:]]
                fixed_files.append([file_name, file_url, date, tags])
        # 根据时间倒叙排序
        fixed_files.sort(key=lambda o: o[2], reverse=True)
    return render_template('index.html', fixed_files=fixed_files)


# 索引页，通过索引文件名访问，展示索引文件内容，可通过url参数搜索
@uno.route('/%s' % uno_sha1_file_name)
def sha1_file_page():
    content = ""
    sha1_data = get_sha1_data()
    if sha1_data:
        search = [request.args.get('n', '').strip(),  # 搜索文件名
                  request.args.get('t', '').strip(),  # 搜索标签名
                  request.args.get('d', '').strip()]  # 搜索日期
        # 以上三种搜索的正则表达式，部分匹配，忽略大小写
        search_rule = [re.compile(regexp_join("\[.*?%s.*?\]\(/(?!%s)", search[0], uno_sha1_file_name), re.I),
                       # fixme: 搜索一些英文字母或数字会查询不准，估计是匹配到了hash里面
                       re.compile(regexp_join("\s\|\s.*\[.*?%s.*?\]\(/(?=%s)", search[1], uno_sha1_file_name), re.I),
                       re.compile(regexp_join("\|\s%s.*?\s\|", search[2]), re.I)]
        # 生成搜索参数不为空的正则规则列表
        rules = [search_rule[i] for i in range(len(search)) if search[i]]
        # 传递给内容过滤器筛选，拿到过滤后内容和内容的最大标签数量
        content, max_tag_num = content_filter(sha1_data, rules)
        # 根据最大标签数量生成md表格头部，加上切割分离前缀后的内容，进行markdown渲染
        content = md(get_sha1_data_table_header(max_tag_num) + split_pref(content))
    return render_template('article.html', name="Index", content=content, show_tags=False, no_sidebar=True,
                           have_search=True)


# 文章和附件页，通过对应的目录名和哈希值访问，文章展示markdown渲染结果，附件直接展示源文件
@uno.route('/<any("%s", "%s"):dir_name>/<file_sha1>' % (uno_articles_dir_name, uno_attachments_dir_name))
def article(dir_name, file_sha1):
    # 判断哈希格式
    if not check_sha1(file_sha1):
        abort(404)
    # 在索引文件中查找对应哈希的文件信息
    group = re.search(regexp_join('\[(.*?)\]\(/%s/%s\)(.*?)\n', dir_name, file_sha1), get_sha1_data())
    if not group:
        abort(404)
    # 判断文件是否存在
    file_path = group.group(1)
    file_abspath = os.path.join(get_articles_dir_abspath(), file_path)
    if not os.path.exists(file_abspath):
        abort(404)
    # 识别把文件加入忽略列表的url参数
    make_file_ignore_arg = request.args.get(uno_make_file_ignore_arg, "").strip()
    if make_file_ignore_arg == "1":
        # 加入忽略列表
        update_config_ignore_file_list(file_path)
        # 重建索引线程处理
        handle_thread(reindex_thread_limit, reindex_thread)
        abort(404)
    if dir_name == uno_articles_dir_name:
        with open(file_abspath, encoding='utf-8') as file:
            file_data = file.read()
        # 识别文章中的固定链接标识
        fixed = get_fixed_flag(file_data)
        if fixed:
            # 加入固定列表
            update_config_fixed_file_list(file_path, True)
        else:
            # 从固定列表移除
            update_config_fixed_file_list(file_path, False)
        # 识别文章中的隐藏侧边栏标识
        no_sidebar = get_no_sidebar_flag(file_data)
        # 识别文章中的自定义css文件，获取自定义css文件url列表
        css_urls = get_custom_css(file_data)
        # 识别文章中的自定义js文件，获取自定义js文件url列表
        js_urls = get_custom_js(file_data)
        # markdown渲染
        content = md(file_data)
        # 去前缀和后缀
        name = re.sub(uno_strip_prefix, "", os.path.splitext(file_path)[0])
        date_tags = group.group(2).split(" | ")[1:]
        date = date_tags[0]
        # 生成标签名列表(不含链接)
        tags = [re.search("\[(.*?)\]\(.*?\)", tag).group(1) for tag in date_tags[1:]]
        return render_template('article.html', name=name, content=content, date=date, tags=tags, show_tags=True,
                               css_urls=css_urls, js_urls=js_urls, no_sidebar=no_sidebar)
    else:
        # 识别把文件加入/移除固定列表的url参数
        make_file_url_fixed_arg = request.args.get(uno_make_file_url_fixed_arg, "").strip()
        if make_file_url_fixed_arg == "1":
            # 加入固定列表
            update_config_fixed_file_list(file_path, True)
        elif make_file_url_fixed_arg == "0":
            # 从固定列表移除
            update_config_fixed_file_list(file_path, False)
        # 定向到源文件
        file_dir, file = os.path.split(file_abspath)
        return send_from_directory(file_dir, file)


# 重建索引线程限制
reindex_thread_limit = []


# 重建索引线程函数
def reindex_thread():
    # 执行重建索引命令并打印日志
    app.logger.info(os.popen(get_reindex_cmd()).read().rstrip())
    articles_dir_abspath = get_articles_dir_abspath()
    sha1_data = "\n"
    old_sha1_data = get_sha1_data()
    max_tag_num = 0
    # 遍历文章目录下所有文件和子目录
    for root, dirs, files in os.walk(articles_dir_abspath):
        # 截取相对路径
        path = root.split(uno_articles_dir_name)[-1].lstrip(os.path.sep).replace("\\", "/")
        # 排除忽略目录，只能忽略文章目录的下一级目录，忽略附件目录等下一步处理
        if path.split("/")[0] in uno_ignore_dir_list + [uno_attachments_dir_name]:
            continue
        for file in files:
            # 组成文件路径
            file_path = "/".join([path, file]).lstrip("/")
            # 排除忽略文件
            if file_path in uno_ignore_file_list:
                continue
            with open(os.path.join(root, file), encoding='utf-8') as file_data:
                content = file_data.read()
            # 从文件内容获取标签并生成标签列表
            tags = ["[%s](/%s?t=%s)" % (tag, uno_sha1_file_name, tag) for tag in get_tags_flag(content)]
            # 判断最大标签数量
            max_tag_num = max(len(tags), max_tag_num)
            # 组成标签和日期附加字符串
            tags_date_append = " | ".join([get_date_flag(content), " | ".join(tags)])
            # 计算文件哈希
            file_sha1_data = sha1_digest_content(content)
            # 判断固定列表里的文件使用旧哈希
            if file_path in uno_fixed_file_list and old_sha1_data:
                # 从旧索引中取出文件旧哈希
                group = re.search(regexp_join("\[%s\]\(/%s/(.*?)\)", file_path, uno_articles_dir_name), old_sha1_data)
                if group:
                    file_sha1_data = group.group(1)
            # 组成一条索引数据
            first = "[%s](/%s/%s)" % (file_path, uno_articles_dir_name, file_sha1_data)
            sha1_data += " | ".join([first, tags_date_append]) + "\n"
    # 把文章部分和附加部分隔开
    sha1_data += "\n---\n| Name\n| -\n"
    # 遍历附件目录下所有文件和子目录
    for root, dirs, files in os.walk(get_attachments_dir_abspath()):
        # 截取相对路径
        path = root.split(uno_attachments_dir_name)[-1].lstrip(os.path.sep).replace("\\", "/")
        # 排除忽略目录，只能忽略附件目录的下一级目录
        if "/".join([uno_attachments_dir_name, path.split("/")[0]]).rstrip("/") in uno_ignore_dir_list:
            continue
        # 加上附件目录重组相对路径
        path = "/".join([uno_attachments_dir_name, path]).rstrip("/")
        for file in files:
            # 组成文件路径
            file_path = "/".join([path, file]).lstrip("/")
            # 排除忽略文件
            if file_path in uno_ignore_file_list:
                continue
            # 计算文件哈希
            file_sha1_data = sha1_digest_file(os.path.join(root, file))
            # 判断固定列表里的文件使用旧哈希
            if file_path in uno_fixed_file_list and old_sha1_data:
                group = re.search(regexp_join("\[%s\]\(/%s/(.*?)\)", file_path, uno_attachments_dir_name),
                                  old_sha1_data)
                if group:
                    file_sha1_data = group.group(1)
            # 组成一条索引数据
            sha1_data += "| [%s](/%s/%s)" % (file_path, uno_attachments_dir_name, file_sha1_data) + "\n"
    # 写入索引文件
    with open(os.path.join(articles_dir_abspath, uno_sha1_file_name), 'w', encoding='utf-8') as sha1_file:
        sha1_file.write(sha1_data)
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
