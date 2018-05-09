import os
from operator import itemgetter

from flask import send_from_directory, Blueprint, render_template, request, abort, url_for, redirect, session

from config import uno_index_file_name, uno_attachments_dir_name, uno_articles_dir_name, uno_make_file_ignore_arg, \
    uno_password
from src.flag import get_custom_js_flag, get_custom_css_flag
from src.index import index_title_key, index_id_key, index_tags_key, index_date_key, get_item_by_url, \
    index_data_filter, get_fixed_articles, index_notags_key, reindex, index_parent_key, index_secret_key
from src.md import render
from src.util import update_config_ignore_file_list, get_articles_dir_abspath, logged, auth

main = Blueprint("main", __name__)


# 首页，展示固定索引的文章，如果没有就展示首页背景图
@main.route('/')
def index():
    return render_template('home.html', fixed_articles=get_fixed_articles())


# 索引页，通过索引文件名访问，展示索引文件内容，可通过传输url参数搜索
@main.route('/%s' % uno_index_file_name)
@auth
def index_file_page():
    search = [request.args.get('i', '').strip(),  # 搜索编号
              request.args.get('n', '').strip(),  # 搜索标题
              request.args.get('t', '').strip(),  # 搜索标签名
              request.args.get('d', '').strip()]  # 搜索日期
    search_index = [index_id_key, index_title_key, index_tags_key, index_date_key]
    # 传递非空搜索给过滤器筛选，并得到最大标签数量
    data = index_data_filter([[search_index[i], search[i]] for i in range(len(search)) if search[i]])
    parents = {}
    for item in data[0]:
        parent = item[index_parent_key]
        if parent not in parents:
            parents[parent] = []
        parents[parent].append(item)
    return render_template('index.html', title="Index", data=[parents, sorted(data[1], key=itemgetter(index_id_key))],
                           article_dir=uno_articles_dir_name, attach_dir=uno_attachments_dir_name)


# 文章和附件页，通过对应的目录名和哈希值访问，文章展示markdown渲染结果，附件直接展示源文件
@main.route('/<any("%s", "%s"):dir_name>/<file_hash>' % (uno_articles_dir_name, uno_attachments_dir_name))
def article_page(dir_name, file_hash):
    # 判断哈希格式
    if len(file_hash) != 40 or not file_hash.isalnum():
        abort(404)
    # 在索引文件中查找对应哈希的项目信息
    item, item_path = get_item_by_url("/%s/%s" % (dir_name, file_hash))
    if not item:
        abort(404)
    if not logged() and item[index_secret_key]:
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
        # 重建索引
        reindex()
        abort(404)
    if dir_name == uno_articles_dir_name:
        with open(item_abspath, encoding='utf-8') as file_data:
            data = file_data.read()
        # 识别文章中的自定义css文件，获取自定义css文件url列表
        css_urls = get_custom_css_flag(data)
        # 识别文章中的自定义js文件，获取自定义js文件url列表
        js_urls = get_custom_js_flag(data)
        # markdown渲染
        data = render(data)
        # 去后缀
        title = os.path.splitext(item[index_title_key])[0]
        date = item[index_date_key]
        tags = item[index_tags_key].keys()
        notags = item[index_notags_key]
        return render_template('article.html', title=title, data=data, date=date, tags=tags, css_urls=css_urls,
                               js_urls=js_urls, notags=notags)
    else:
        # 定向到源文件
        file_dir, file = os.path.split(item_abspath)
        return send_from_directory(file_dir, file)


# 标签页
@main.route('/tags/<tag_name>')
def tag_page(tag_name):
    new_fixed_articles = []
    fixed_articles = get_fixed_articles()
    for article in fixed_articles:
        for tag in article[index_tags_key]:
            if tag.upper() == tag_name.upper():
                new_fixed_articles.append(article)
    if not new_fixed_articles:
        abort(404)
    return render_template('home.html', fixed_articles=new_fixed_articles, tag_name=tag_name)


# 登陆页
@main.route('/login', methods=['POST', 'GET'])
def login():
    referrer = request.referrer
    if not referrer or referrer.split('/')[-2] == url_for(".login")[1:-1]:
        referrer = ""
    if logged():
        if referrer:
            return redirect(referrer)
        else:
            return redirect(url_for('.index'))
    error = False
    if request.method == 'POST':
        referrer = request.form['referrer']
        if not referrer:
            referrer = request.args.get('ref')
        if request.form['password'] == uno_password:
            session['password'] = uno_password
            if referrer:
                return redirect(referrer)
            else:
                return redirect(url_for('.index'))
        else:
            error = True
    return render_template('login.html', referrer=referrer, error=error)


# 登出页
@main.route('/logout')
def logout():
    session.pop('password', None)
    referrer = request.referrer
    if referrer:
        return redirect(referrer)
    else:
        return redirect(url_for('.index'))
