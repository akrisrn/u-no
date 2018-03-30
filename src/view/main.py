import json
import os
import re
import time

from flask import send_from_directory, Blueprint, render_template, request, abort

from config import uno_update_url_name, uno_update_limit_time, uno_reindex_url_name, uno_reindex_limit_time, \
    uno_index_file_name, uno_attachments_dir_name, uno_articles_dir_name, uno_strip_prefix, uno_ignore_file_list, \
    uno_ignore_dir_list, uno_make_file_ignore_arg
from src.flag import get_fixed_flag, get_date_flag, get_tags_flag, get_unignore_flag, get_ignore_flag, \
    get_custom_js_flag, get_custom_css_flag
from src.index import index_url_key, index_title_key, index_id_key, index_fixed_key, index_tags_key, index_date_key, \
    get_item_by_path, get_item_by_url, index_data_filter, get_fixed_articles
from src.md import render
from src.util import handle_thread, get_update_cmd, compute_digest_by_abspath, compute_digest_by_data, \
    update_config_ignore_file_list, get_articles_dir_abspath, get_reindex_cmd

main = Blueprint("main", __name__)


# 首页，展示固定索引的文章，如果没有就展示首页背景图
@main.route('/')
def index():
    return render_template('home.html', fixed_articles=get_fixed_articles())


# 索引页，通过索引文件名访问，展示索引文件内容，可通过传输url参数搜索
@main.route('/%s' % uno_index_file_name)
def index_file_page():
    search = [request.args.get('i', '').strip(),  # 搜索编号
              request.args.get('n', '').strip(),  # 搜索标题
              request.args.get('t', '').strip(),  # 搜索标签名
              request.args.get('d', '').strip()]  # 搜索日期
    search_index = [index_id_key, index_title_key, index_tags_key, index_date_key]
    # 传递非空搜索给过滤器筛选，并得到最大标签数量
    data, max_tag_num = index_data_filter([[search_index[i], search[i]] for i in range(len(search)) if search[i]])
    return render_template('index.html', title="Index", data=data, max_tag_num=max_tag_num)


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
        handle_thread(reindex_thread_limit, reindex_thread)
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
        return render_template('article.html', title=title, data=data, date=date, tags=tags,
                               css_urls=css_urls, js_urls=js_urls)
    else:
        # 定向到源文件
        file_dir, file = os.path.split(item_abspath)
        return send_from_directory(file_dir, file)


# 重建索引线程限制
reindex_thread_limit = []


# 重建索引线程函数
def reindex_thread():
    # 执行重建索引命令
    os.popen(get_reindex_cmd()).close()
    articles_dir_abspath = get_articles_dir_abspath()
    articles_block = {}
    attachments_block = {}
    # 遍历文章目录下所有文件和子目录
    for root, dirs, files in os.walk(articles_dir_abspath):
        # 截取相对路径
        # noinspection PyTypeChecker
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
            # 分离编号和标题
            group = re.search("(%s)" % uno_strip_prefix, file_path)
            if group:
                item_id = group.group(1).strip("-")
                title = re.sub(group.group(1), "", file_path)
            else:
                item_id = ""
                title = file_path
            if not path.startswith(uno_attachments_dir_name):
                # 获取标签并生成标签字典
                # noinspection PyUnboundLocalVariable
                tags = {tag: "/%s?t=%s" % (uno_index_file_name, tag) for tag in get_tags_flag(data)}
                # 获取日期
                date = get_date_flag(data)
                # 计算文章哈希组成url
                url = "/%s/%s" % (uno_articles_dir_name, compute_digest_by_data(data))
                fixed = False
                # 识别文章中固定索引标识，来判断是否更新哈希
                if get_fixed_flag(data):
                    # 查找旧索引中对应的项目，如果存在则沿用哈希
                    item = get_item_by_path(file_path)
                    if item:
                        url = item[index_url_key]
                    fixed = True
                # 组成一条文章索引
                articles_block[file_path] = {index_id_key: item_id, index_title_key: title, index_url_key: url,
                                             index_date_key: date, index_tags_key: tags, index_fixed_key: fixed}
            else:
                # 组成一条附件索引
                url = "/%s/%s" % (uno_attachments_dir_name, compute_digest_by_abspath(file_abspath))
                attachments_block[file_path] = {index_id_key: item_id, index_title_key: title, index_url_key: url}
    # 写入索引文件
    index_data = json.dumps([articles_block, attachments_block], separators=(',', ':'))
    with open(os.path.join(articles_dir_abspath, uno_index_file_name), 'w', encoding='utf-8') as index_file:
        index_file.write(index_data)
    # 冷却
    time.sleep(uno_reindex_limit_time)


# 重建索引页，通过重建索引url名访问，另开线程执行操作，出于保密url原因返回404
@main.route('/%s' % uno_reindex_url_name)
def reindex():
    # 重建索引线程处理
    handle_thread(reindex_thread_limit, reindex_thread)
    abort(404)


# 更新程序线程限制
update_thread_limit = []


# 更新程序线程函数
def update_thread():
    # 执行更新程序命令
    os.popen(get_update_cmd()).close()
    # 冷却
    time.sleep(uno_update_limit_time)


# 更新程序页，通过更新程序url名访问，另开线程执行操作，出于保密url原因返回404
@main.route('/%s' % uno_update_url_name)
def update():
    # 重建索引线程处理
    handle_thread(update_thread_limit, update_thread)
    abort(404)
