import os
import re
import shutil

import src.util
from config import uno_frozen_dir_name, uno_static_dir_name, uno_articles_url_name, uno_attachments_url_name, \
    uno_articles_dir_abspath
from src.index import index_url_key, index_tags_key, index_title_key, get_item_by_url
from src.view.main import index, article_page, tag_page
from uno import app

uno_tags_url_name = "tags"


def replace_url(data, urls):
    for result in re.finditer("/(%s|%s|%s)/[0-9a-z]{40}" %
                              (uno_articles_url_name, uno_attachments_url_name, uno_tags_url_name), data):
        data = re.sub(result.group(), urls[result.group()], data)
    return data.replace("http:///", "/")


if __name__ == '__main__':
    app.config["SERVER_NAME"] = ""

    root_abspath = src.util.get_root_abspath()

    static_dir_abspath = os.path.join(root_abspath, uno_static_dir_name)

    frozen_dir_abspath = os.path.join(root_abspath, uno_frozen_dir_name)
    frozen_articles_dir_abspath = os.path.join(frozen_dir_abspath, uno_articles_url_name)
    frozen_attachments_dir_abspath = os.path.join(frozen_dir_abspath, uno_attachments_url_name)
    frozen_tags_dir_abspath = os.path.join(frozen_dir_abspath, uno_tags_url_name)
    frozen_static_dir_abspath = os.path.join(frozen_dir_abspath, uno_static_dir_name)

    if os.path.exists(frozen_dir_abspath):
        shutil.rmtree(frozen_articles_dir_abspath, True)
        shutil.rmtree(frozen_attachments_dir_abspath, True)
        shutil.rmtree(frozen_tags_dir_abspath, True)
        shutil.rmtree(frozen_static_dir_abspath, True)
    else:
        os.mkdir(frozen_dir_abspath)

    os.mkdir(frozen_articles_dir_abspath)
    os.mkdir(frozen_attachments_dir_abspath)
    os.mkdir(frozen_tags_dir_abspath)
    shutil.copytree(static_dir_abspath, frozen_static_dir_abspath,
                    ignore=shutil.ignore_patterns("bower_components", "node_modules", "*.json"))

    with app.app_context():
        data_list = {}
        page_urls = {}

        index_page_data = index()
        data_list[os.path.join(frozen_dir_abspath, "index.html")] = index_page_data
        for result_article in re.finditer("/%s/[0-9a-z]{40}" % uno_articles_url_name, index_page_data):
            article, _ = get_item_by_url(result_article.group())
            article_title = os.path.splitext(article[index_title_key])[0]
            article_hash = article[index_url_key].split("/")[2]
            article_page_data = article_page(uno_articles_url_name, article_hash)
            data_list[os.path.join(frozen_articles_dir_abspath, article_title + ".html")] = article_page_data
            page_urls[result_article.group()] = "/%s/%s" % (uno_articles_url_name, article_title + ".html")

            for result_attach in re.finditer("/%s/[0-9a-z]{40}" % uno_attachments_url_name, article_page_data):
                attach, attach_path = get_item_by_url(result_attach.group())
                attach_abspath = os.path.join(uno_articles_dir_abspath, attach_path)
                attach_filename = attach[index_title_key]
                new_attach_abspath = os.path.join(frozen_attachments_dir_abspath, attach_filename)
                shutil.copy(attach_abspath, new_attach_abspath)
                page_urls[result_attach.group()] = "/%s/%s" % (uno_attachments_url_name, attach_filename)

            tags = article[index_tags_key]
            for tag in tags:
                tag_abspath = os.path.join(frozen_tags_dir_abspath, tags[tag] + ".html")
                if tag_abspath not in data_list:
                    data_list[tag_abspath] = tag_page(tag)
                    page_urls["/%s/%s" % (uno_tags_url_name, tag)] = "/%s/%s.html" % (uno_tags_url_name, tags[tag])

        for path in data_list:
            with open(path, "w", encoding="utf-8") as f:
                f.write(replace_url(data_list[path], page_urls))
