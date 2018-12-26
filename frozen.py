import os
import re
import shutil

from src.const import index_path_key, index_url_key, index_tags_key, index_title_key, hash_length
from src.index import get_item_by_url, reindex
from src.util import get_root_abspath
from src.view.main import home_page, article_page, tag_page, articles_url_name, attachments_url_name, tags_url_name
from uno import app

if __name__ == '__main__':
    static_dir_name = app.config["STATIC_DIR_NAME"]
    frozen_dir_name = app.config["FROZEN_DIR_NAME"]
    articles_dir_abspath = app.config["ARTICLES_DIR_ABSPATH"]
    app.config["SERVER_NAME"] = ""
    app.config["USE_CDN"] = True
    app.config["DEBUG"] = False

    root_abspath = get_root_abspath()
    static_dir_abspath = os.path.join(root_abspath, static_dir_name)

    frozen_dir_abspath = os.path.join(root_abspath, frozen_dir_name)
    frozen_articles_dir_abspath = os.path.join(frozen_dir_abspath, articles_url_name)
    frozen_attachments_dir_abspath = os.path.join(frozen_dir_abspath, attachments_url_name)
    frozen_tags_dir_abspath = os.path.join(frozen_dir_abspath, tags_url_name)
    frozen_static_dir_abspath = os.path.join(frozen_dir_abspath, static_dir_name)

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
    ignore_list = ["bower_components", "node_modules", "*.json",
                   "edit.css", "edit.js", "index.css", "index.js"]
    shutil.copytree(static_dir_abspath, frozen_static_dir_abspath, ignore=shutil.ignore_patterns(*ignore_list))

    data_list = {}
    page_urls = {}
    with app.app_context():
        reindex()
        index_page_data = home_page()
        data_list[os.path.join(frozen_dir_abspath, "index.html")] = index_page_data
        for result_article in re.finditer("/%s/[0-9a-z]{%s}" % (articles_url_name, hash_length), index_page_data):
            article = get_item_by_url(result_article.group())
            article_title = os.path.splitext(article[index_title_key])[0]
            article_hash = article[index_url_key].split("/")[2]
            article_page_data = article_page(articles_url_name, article_hash)
            data_list[os.path.join(frozen_articles_dir_abspath, article_hash + ".html")] = article_page_data
            page_urls[result_article.group()] = "/%s/%s" % (articles_url_name, article_hash + ".html")

            for result_attach in re.finditer("/%s/[0-9a-z]{%s}" % (attachments_url_name, hash_length),
                                             article_page_data):
                attach = get_item_by_url(result_attach.group())
                attach_path = attach[index_path_key]
                attach_abspath = os.path.join(articles_dir_abspath, attach_path)
                attach_filename = attach[index_title_key]
                attach_ext = os.path.splitext(attach_filename)[1]
                attach_hash = attach[index_url_key].split("/")[2]
                new_attach_filename = attach_hash + attach_ext
                new_attach_abspath = os.path.join(frozen_attachments_dir_abspath, new_attach_filename)
                shutil.copy(attach_abspath, new_attach_abspath)
                page_urls[result_attach.group()] = "/%s/%s" % (attachments_url_name, new_attach_filename)

            tags = article[index_tags_key]
            for tag in tags:
                tag_abspath = os.path.join(frozen_tags_dir_abspath, tag + ".html")
                if tag_abspath not in data_list:
                    data_list[tag_abspath] = tag_page(tag)
                    page_urls["/%s/%s" % (tags_url_name, tag)] = "/%s/%s.html" % (tags_url_name, tag)


    def replace_url(data, urls):
        for result in re.finditer("/(%s|%s|%s)/[0-9a-z]{%s}" %
                                  (articles_url_name, attachments_url_name, tags_url_name, hash_length), data):
            data = re.sub(result.group(), urls[result.group()], data)
        return data.replace("http:///", "/")


    for path in data_list:
        with open(path, "w", encoding="utf-8") as f:
            f.write(replace_url(data_list[path], page_urls))
