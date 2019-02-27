import json
import os
import re
from datetime import datetime
from threading import Thread

import feedparser
from flask import Blueprint, render_template, current_app

from src.cache import get_file_cache
from src.const import RSS, tags_url_name, index_parent_key
from src.const import index_date_key, index_url_key, index_title_key, index_tags_key, show_date_format
from src.util import get_articles_dir_abspath

rss = Blueprint("rss", __name__)


def get_rss_data():
    rss_file_path = os.path.join(get_articles_dir_abspath(), current_app.config["RSS_FILE_NAME"])
    return json.loads(get_file_cache(rss_file_path))


def convert_time(time):
    return datetime.strptime(time, "%a, %d %b %Y %H:%M:%S %z").strftime(show_date_format + " %H:%M:%S")


def convert_entry(entry, name="", tags=None):
    if tags is None:
        tags = {}
    return {
        index_date_key: convert_time(entry.get_published()),
        index_url_key: entry.get_link(),
        index_title_key: entry.get_title(),
        index_parent_key: name,
        index_tags_key: tags,
    }


class Entry:
    def __init__(self, entry):
        self.entry = entry

    def get_title(self):
        return self.entry[RSS.ENTRY_TITLE.value]

    def get_author(self):
        return self.entry[RSS.ENTRY_AUTHOR.value]

    def get_summary(self):
        return self.entry[RSS.ENTRY_SUMMARY.value]

    def get_published(self):
        return self.entry[RSS.ENTRY_PUBLISHED.value]

    def get_link(self):
        return self.entry[RSS.ENTRY_LINK.value]


class Feed:
    def __init__(self, rss_url):
        self.feed = feedparser.parse(rss_url)

    def get_title(self):
        return self.feed[RSS.FEED.value][RSS.FEED_TITLE.value]

    def get_subtitle(self):
        return self.feed[RSS.FEED.value][RSS.FEED_SUBTITLE.value]

    def get_link(self):
        return self.feed[RSS.FEED.value][RSS.FEED_LINK.value]

    def get_language(self):
        return self.feed[RSS.FEED.value][RSS.FEED_LANGUAGE.value]

    def get_published(self):
        return self.feed[RSS.FEED.value][RSS.FEED_PUBLISHED.value]

    def get_updated(self):
        return self.feed[RSS.FEED.value][RSS.FEED_UPDATED.value]

    def get_ttl(self):
        return self.feed[RSS.FEED.value][RSS.FEED_TTL.value]

    def get_entries(self):
        entries = []
        for entry in self.feed[RSS.FEED_ENTRIES.value]:
            entries.append(Entry(entry))
        return entries

    def get_href(self):
        return self.feed[RSS.FEED_HREF.value]

    def get_status(self):
        return self.feed[RSS.FEED_STATUS.value]

    def get_encoding(self):
        return self.feed[RSS.FEED_ENCODING.value]

    def get_version(self):
        return self.feed[RSS.FEED_VERSION.value]


@rss.route('/')
def home_page():
    rss_data = get_rss_data()
    articles = []
    feeds_data = rss_data[RSS.FEEDS_KEY.value]
    rss_filter = rss_data[RSS.FILTER_KEY.value]

    def th(url):
        feed_data = feeds_data[url]
        name = feed_data[RSS.NAME_KEY.value]
        tags = {tag: tag for tag in feed_data[RSS.TAGS_KEY.value]}
        feed = Feed(url)
        for entry in feed.get_entries():
            is_filter = False
            for regex in rss_filter:
                if re.match(".*?(%s)" % regex, entry.get_title()):
                    is_filter = True
                    break
            if not is_filter:
                articles.append(convert_entry(entry, name, tags))

    thread = []
    for rss_url in feeds_data:
        t = Thread(target=th, args=(rss_url,))
        thread.append(t)
        t.setDaemon(True)
        t.start()
    for t in thread:
        t.join()

    articles = sorted(articles, key=lambda k: k[index_date_key], reverse=True)
    return render_template('rss/home.html', rss_articles=articles)


@rss.route('/%s' % tags_url_name)
def tags_page():
    return ""


@rss.route('/%s/<tag_name>' % tags_url_name)
def tag_page(tag_name):
    return tag_name
