import json
import os
import re

from config import uno_index_file_name, uno_about_file_name
from src.util import regexp_join, get_articles_dir_abspath

# 组成索引的JSON数据所用的键名
index_id_key = "id"
index_title_key = "title"
index_url_key = "url"
index_date_key = "date"
index_tags_key = "tags"
index_fixed_key = "fixed"


# 获取索引文件数据
def get_index_data():
    # 组成索引文件绝对路径
    index_file_path = os.path.join(get_articles_dir_abspath(), uno_index_file_name)
    # 判断是否存在
    if os.path.exists(index_file_path):
        with open(index_file_path, encoding='utf-8') as index_file:
            index_data = index_file.read()
        return json.loads(index_data)
    return []


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
                return item, item_path
    return {}, ""


# 获取固定索引的文章列表
def get_fixed_articles():
    fixed_articles = []
    index_data = get_index_data()
    if index_data:
        articles_block = index_data[0]
        # 遍历文章块
        for article_path in articles_block:
            article = articles_block[article_path]
            # 把固定索引的文章加入列表
            if article[index_fixed_key]:
                fixed_articles.append(article)
        # 按照时间倒叙进行排序
        fixed_articles.sort(key=lambda o: o[index_date_key], reverse=True)
    return fixed_articles


# 用于搜索索引的过滤器，接受一组索引键名和搜索项的列表，以AND模式运行，同时计算出文章的最大标签数
def index_data_filter(searches):
    articles = []
    attachments = []
    max_tag_num = 0
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
                    for tag in article[index]:
                        if re.search(pattern, tag):
                            is_tag_find = True
                            break
                    # 如果标签都没匹配则视为没找到对应文章，结束循环
                    if not is_tag_find:
                        is_find = False
                        break
                else:
                    # 如果没匹配则视为没找到对应文章，结束循环
                    if not re.search(pattern, article[index]):
                        is_find = False
                        break
            # 如果找到则把文章加入列表
            if is_find:
                # 计算最大标签数量
                max_tag_num = max(max_tag_num, len(article[index_tags_key]))
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
                if not re.search(pattern, attachment[index]):
                    is_find = False
                    break
            # 如果找到则把附件加入列表
            if is_find:
                attachments.append(attachment)
    return [articles, attachments], max_tag_num


def get_about_article_url():
    article = get_item_by_path(uno_about_file_name)
    if not article:
        return []
    return article[index_url_key].split("/")[1:]
