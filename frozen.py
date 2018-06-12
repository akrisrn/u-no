import os
import re
import shutil

import src.util
from config import uno_frozen_dir_name, uno_static_dir_name, uno_articles_dir_name, uno_attachments_dir_name
from src.index import get_fixed_articles, index_url_key, index_tags_key, get_item_by_url
from src.view.main import index, article_page, tag_page
from uno import app

uno_tags_dir_name = "tags"


def clean(data):
    # noinspection RegExpDuplicateAlternationBranch
    data = re.sub("(%s/.*?|%s/.*?)\"" % (uno_articles_dir_name, uno_tags_dir_name), "\g<1>.html\"", data)
    return data.replace("http:///", "/")


if __name__ == '__main__':
    app.config["SERVER_NAME"] = ""

    root_abspath = src.util.get_root_abspath()

    articles_dir_abspath = os.path.join(root_abspath, uno_articles_dir_name)
    static_dir_abspath = os.path.join(root_abspath, uno_static_dir_name)

    frozen_dir_abspath = os.path.join(root_abspath, uno_frozen_dir_name)
    frozen_articles_dir_abspath = os.path.join(frozen_dir_abspath, uno_articles_dir_name)
    frozen_attachments_dir_abspath = os.path.join(frozen_dir_abspath, uno_attachments_dir_name)
    frozen_tags_dir_abspath = os.path.join(frozen_dir_abspath, uno_tags_dir_name)
    frozen_static_dir_abspath = os.path.join(frozen_dir_abspath, uno_static_dir_name)

    if os.path.exists(frozen_dir_abspath):
        shutil.rmtree(frozen_articles_dir_abspath)
        shutil.rmtree(frozen_attachments_dir_abspath)
        shutil.rmtree(frozen_tags_dir_abspath)
        shutil.rmtree(frozen_static_dir_abspath)
    else:
        os.mkdir(frozen_dir_abspath)

    os.mkdir(frozen_articles_dir_abspath)
    os.mkdir(frozen_attachments_dir_abspath)
    os.mkdir(frozen_tags_dir_abspath)
    shutil.copytree(static_dir_abspath, frozen_static_dir_abspath, ignore=shutil.ignore_patterns("bower_components"))

    with app.app_context():
        with open(os.path.join(frozen_dir_abspath, "index.html"), "w", encoding="utf-8") as f:
            f.write(clean(index()))
        fixed_articles = get_fixed_articles()
        for article in fixed_articles:
            dir_name, file_hash = article[index_url_key][1:].split("/")
            with open(os.path.join(frozen_articles_dir_abspath, file_hash + ".html"), "w", encoding="utf-8") as f:
                article_page_data = clean(article_page(dir_name, file_hash, True))
                for result in re.finditer("/%s/([0-9a-z]{40})" % uno_attachments_dir_name, article_page_data):
                    item, item_path = get_item_by_url(result.group())
                    item_abspath = os.path.join(articles_dir_abspath, item_path)
                    file_ext = os.path.splitext(item_path)[1]
                    new_item_abspath = os.path.join(frozen_attachments_dir_abspath, result.group(1) + file_ext)
                    shutil.copy(item_abspath, new_item_abspath)
                    article_page_data = re.sub(result.group(), result.group() + file_ext, article_page_data)
                f.write(article_page_data)
            tags = article[index_tags_key]
            for tag in tags:
                tag_abspath = os.path.join(frozen_tags_dir_abspath, tag + ".html")
                if not os.path.exists(tag_abspath):
                    with open(tag_abspath, "w", encoding="utf-8") as f:
                        f.write(clean(tag_page(tag)))
