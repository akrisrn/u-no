import os

from flask import send_from_directory, Blueprint, render_template, request, abort, url_for, redirect, current_app

from ..cache import get_file_cache
from ..const import index_notags_key, index_parent_key, index_path_key, index_url_name, index_title_key, index_id_key, \
    index_tags_key, index_date_key, articles_url_name, attachments_url_name, tags_url_name, reindex_url_name
from ..flag import get_custom_js_flag, get_custom_css_flag, get_plugin_flag
from ..index import get_item_by_url, index_data_filter, get_fixed_articles, reindex
from ..md import render, get_snippet
from ..util import get_articles_dir_abspath, is_valid_hash, get_plugins_urls

main = Blueprint("main", __name__)


# 首页，展示固定索引的文章，如果没有就展示首页背景图
@main.route('/')
def home_page():
    return render_template('home.html', fixed_articles=get_fixed_articles())


# 索引页，通过索引文件名访问，展示索引文件内容，可通过传输url参数搜索
@main.route('/%s' % index_url_name)
def index_page():
    search = [request.args.get('i', '').strip(),  # 搜索编号
              request.args.get('n', '').strip(),  # 搜索标题
              request.args.get('t', '').strip(),  # 搜索标签名
              request.args.get('d', '').strip()]  # 搜索日期
    search_index = [index_id_key, index_title_key, index_tags_key, index_date_key]
    # 传递非空搜索给过滤器筛选，并得到最大标签数量
    data = index_data_filter([[search_index[i], search[i]] for i in range(len(search)) if search[i]])
    parents = []
    for each in [data[0], data[1]]:
        parent = {}
        for item in each:
            parent_dir = item[index_parent_key]
            if parent_dir not in parent:
                parent[parent_dir] = []
            parent[parent_dir].append(item)
        parents.append(parent)
    ignore_files = current_app.config["IGNORE_FILE_LIST"]
    return render_template('index.html', title=index_url_name.upper(),
                           data=[parents, ignore_files],
                           article_url=articles_url_name, attach_url=attachments_url_name,
                           ignore_tab_name="ignore_file")


@main.route('/%s' % reindex_url_name)
def reindex_page():
    reindex()
    return redirect(url_for(".index_page"))


# 文章和附件页，通过对应的目录名和哈希值访问，文章展示markdown渲染结果，附件直接展示源文件
@main.route('/<any("%s", "%s"):url_name>/<file_hash>' % (articles_url_name, attachments_url_name))
def article_page(url_name, file_hash):
    # 判断哈希格式
    if not is_valid_hash(file_hash):
        abort(404)
    # 在索引文件中查找对应哈希的项目信息
    item = get_item_by_url("/%s/%s" % (url_name, file_hash))
    if not item:
        abort(404)
    # 判断文件是否存在
    item_path = item[index_path_key]
    item_abspath = os.path.join(get_articles_dir_abspath(), item_path)
    if not os.path.exists(item_abspath):
        abort(404)
    if url_name == articles_url_name:
        data = get_file_cache(item_abspath)
        plugin_urls = get_plugins_urls(get_plugin_flag(data))
        # 识别文章中的自定义css文件，获取自定义css文件url列表
        css_urls = plugin_urls["css"] + get_custom_css_flag(data)
        # 识别文章中的自定义js文件，获取自定义js文件url列表
        js_urls = plugin_urls["js"] + get_custom_js_flag(data)
        # 添加页眉页脚
        snip_header = get_snippet(current_app.config["HEADER_FILE_NAME"])
        snip_footer = get_snippet(current_app.config["FOOTER_FILE_NAME"])
        if snip_header and not data.startswith("\n\n"):
            snip_header += ("" if data.startswith("\n") else "\n") + "\n"
        if snip_footer and not data.endswith("\n\n"):
            snip_footer = ("" if data.endswith("\n") else "\n") + "\n" + snip_footer
        data = "%s%s%s" % (snip_header, data, snip_footer)
        # markdown渲染
        data = render(data)
        # 去后缀
        title = os.path.splitext(item[index_title_key])[0]
        date = item[index_date_key]
        tags = item[index_tags_key]
        notags = item[index_notags_key]
        return render_template('article.html', title=title, data=data, date=date, tags=tags, css_urls=css_urls,
                               js_urls=js_urls, notags=notags)
    else:
        # 定向到源文件
        file_dir, file = os.path.split(item_abspath)
        return send_from_directory(file_dir, file)


# 标签页
@main.route('/%s/<tag_hash>' % tags_url_name)
def tag_page(tag_hash):
    # 判断哈希格式
    if not is_valid_hash(tag_hash):
        abort(404)
    new_fixed_articles = []
    fixed_articles = get_fixed_articles()
    tag_name = ""
    for article in fixed_articles:
        for key in article[index_tags_key]:
            if key == tag_hash:
                if not tag_name:
                    tag_name = article[index_tags_key][key]
                new_fixed_articles.append(article)
                break
    if not new_fixed_articles:
        abort(404)
    return render_template('home.html', fixed_articles=new_fixed_articles, tag_name=tag_name)
