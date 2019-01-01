import json
import os
import re

from flask import current_app

import src.flag
import src.md
from .cache import get_file_cache
from .const import index_url_key, index_title_key, index_parent_key, index_id_key, index_highlight_key, \
    index_top_key, index_notags_key, index_fixed_key, index_tags_key, index_date_key, index_path_key, \
    articles_url_name, attachments_url_name, index_bereferenced_key
from .util import regexp_join, get_articles_dir_abspath, compute_digest_by_abspath, compute_digest_by_data, \
    update_config_ignore_file_list


# 获取索引文件数据
def get_index_data():
    # 组成索引文件绝对路径
    index_file_path = os.path.join(get_articles_dir_abspath(), current_app.config["INDEX_FILE_NAME"])
    return json.loads(get_file_cache(index_file_path))


# 根据相对路径从索引文件中取出对应项目
def get_item_by_path(path):
    for block in get_index_data():
        if path in block:
            return block[path]
    return {}


# 根据url从索引文件中取出对应项目
def get_item_by_url(url):
    for block in get_index_data():
        for item_path in block:
            item = block[item_path]
            if item[index_url_key] == url:
                return item
    return {}


# 获取固定索引的文章列表
def get_fixed_articles():
    fixed_articles = []
    top_articles = []
    index_data = get_index_data()
    if index_data:
        articles_block = index_data[0]
        # 遍历文章块
        for article_path in articles_block:
            article = articles_block[article_path]
            # 把固定索引的文章加入列表
            if article[index_fixed_key]:
                if article[index_top_key]:
                    top_articles.append(article)
                else:
                    fixed_articles.append(article)
        # 按照时间倒叙进行排序
        fixed_articles.sort(key=lambda o: o[index_date_key], reverse=True)
        top_articles.sort(key=lambda o: o[index_date_key], reverse=True)
        fixed_articles = top_articles + fixed_articles
    return fixed_articles


# 用于搜索索引的过滤器，接受一组索引键名和搜索项的列表，以AND模式运行，同时计算出文章的最大标签数
def index_data_filter(searches):
    articles = []
    attachments = []
    index_data = get_index_data()
    if index_data:
        articles_block = index_data[0]
        attachments_block = index_data[1]
        # 先处理文章块
        for article_path in articles_block:
            article = articles_block[article_path]
            is_find = True
            for index, search in searches:
                # 根据搜索内容组成正则表达式，忽略大小写
                pattern = re.compile(regexp_join(".*%s.*", search), re.I)
                # 如果搜索的是标签则遍历所有标签进行匹配
                if index == index_tags_key:
                    is_tag_find = False
                    # 有一个匹配则视为找到标签，结束循环
                    for key in article[index]:
                        if re.search(pattern, article[index][key]):
                            is_tag_find = True
                            break
                    # 如果标签都没匹配则视为没找到对应文章，结束循环
                    if not is_tag_find:
                        is_find = False
                        break
                else:
                    # 如果没匹配则视为没找到对应文章，结束循环
                    if not re.search(pattern, str(article[index])):
                        is_find = False
                        break
            # 如果找到则把文章加入列表
            if is_find:
                articles.append(article)
        # 处理附件块
        for attachment_path in attachments_block:
            attachment = attachments_block[attachment_path]
            is_find = True
            for index, search in searches:
                # 如果搜索的有日期或标签则视为没找到对应附件，结束循环
                if index in (index_date_key, index_tags_key):
                    is_find = False
                    break
                # 根据搜索内容组成正则表达式，忽略大小写
                pattern = re.compile(regexp_join(".*%s.*", search), re.I)
                # 如果没匹配则视为没找到对应附件，结束循环
                if not re.search(pattern, str(attachment[index])):
                    is_find = False
                    break
            # 如果找到则把附件加入列表
            if is_find:
                attachments.append(attachment)
    return [articles, attachments]


# 重建索引
def reindex():
    articles_dir_abspath = get_articles_dir_abspath()
    articles_block = {}
    attachments_block = {}
    reference_dict = {}
    # 遍历文章目录下所有文件和子目录
    for root, dirs, files in os.walk(articles_dir_abspath):
        # 截取相对路径
        path = root.split(articles_dir_abspath)[-1].lstrip(os.path.sep).replace("\\", "/")
        # 排除忽略目录
        is_ignore = False
        for ignore_dir in current_app.config["IGNORE_DIR_LIST"]:
            if path.startswith(ignore_dir):
                is_ignore = True
                break
        if is_ignore:
            continue
        index = 1
        for file in files:
            # 组成文件路径
            file_path = "/".join([path, file]).lstrip("/")
            file_abspath = os.path.join(root, file)
            if not path.startswith(current_app.config["ATTACHMENTS_DIR_NAME"]):
                # 忽略无法以unicode编码的文件
                try:
                    with open(file_abspath, encoding='utf-8') as file_data:
                        data = file_data.read()
                except UnicodeDecodeError:
                    continue
                # 识别文章中的忽略文件标识，来判断如何更新忽略列表
                if src.flag.get_ignore_flag(data):
                    update_config_ignore_file_list(file_path, True)
                # 识别文章中的取消忽略文件标识，来判断如何更新忽略列表
                if src.flag.get_unignore_flag(data):
                    update_config_ignore_file_list(file_path, False)
            # 排除忽略文件
            if file_path in current_app.config["IGNORE_FILE_LIST"]:
                continue
            parent, title = os.path.split(file_path.replace("+：", ":"))
            if not path.startswith(current_app.config["ATTACHMENTS_DIR_NAME"]):
                # 获取标签并生成标签字典
                tags = {compute_digest_by_data(tag): tag for tag in src.flag.get_tags_flag(data)}
                # 获取日期
                date = src.flag.get_date_flag(data)
                # 计算文章哈希组成url
                url = "/%s/%s" % (articles_url_name, compute_digest_by_data(data))
                # 识别文章中固定索引标识，来判断是否更新哈希
                fixed = src.flag.get_fixed_flag(data)
                if fixed:
                    # 查找旧索引中对应的项目，如果存在则沿用哈希
                    item = get_item_by_path(file_path)
                    if item:
                        url = "/%s/%s" % (articles_url_name, item[index_url_key].split("/")[-1])
                reference_dict[file_path] = src.md.inlink(data, True)
                # 组成一条文章索引
                articles_block[file_path] = {index_id_key: index, index_parent_key: parent, index_title_key: title,
                                             index_path_key: file_path, index_url_key: url, index_date_key: date,
                                             index_tags_key: tags, index_fixed_key: fixed,
                                             index_notags_key: src.flag.get_notags_flag(data),
                                             index_top_key: src.flag.get_top_flag(data),
                                             index_highlight_key: src.flag.get_highlight_flag(data),
                                             index_bereferenced_key: []}
            else:
                # 组成一条附件索引
                url = "/%s/%s" % (attachments_url_name, compute_digest_by_abspath(file_abspath))
                attachments_block[file_path] = {index_id_key: index, index_parent_key: parent, index_title_key: title,
                                                index_path_key: file_path, index_url_key: url,
                                                index_bereferenced_key: []}
            index += 1
    be_referenced_dict = {}
    for key in reference_dict:
        for value in reference_dict[key]:
            if value not in be_referenced_dict:
                be_referenced_dict[value] = []
            be_referenced_dict[value].append(key)
    for key in be_referenced_dict:
        for block in [articles_block, attachments_block]:
            if key in block:
                block[key][index_bereferenced_key] = be_referenced_dict[key]
                break
    # 写入索引文件
    index_data = json.dumps([articles_block, attachments_block], separators=(',', ':'))
    with open(os.path.join(articles_dir_abspath, current_app.config["INDEX_FILE_NAME"]), 'w',
              encoding='utf-8') as index_file:
        index_file.write(index_data)
