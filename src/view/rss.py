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


def get_record_entry(entry):
    return {
        RSS.ENTRY_TITLE.value: entry.get_title(),
        RSS.ENTRY_AUTHOR.value: entry.get_author(),
        RSS.ENTRY_SUMMARY.value: entry.get_summary(),
        RSS.ENTRY_PUBLISHED.value: convert_time(entry.get_published())
    }


def handle_key_error(method):
    def wrapped(*args, **kwargs):
        try:
            return method(*args, **kwargs)
        except KeyError:
            return ""

    return wrapped


class Entry:
    def __init__(self, entry):
        self.entry = entry

    @handle_key_error
    def get_title(self):
        return self.entry[RSS.ENTRY_TITLE.value]

    @handle_key_error
    def get_author(self):
        return self.entry[RSS.ENTRY_AUTHOR.value]

    @handle_key_error
    def get_summary(self):
        return self.entry[RSS.ENTRY_SUMMARY.value]

    @handle_key_error
    def get_published(self):
        return self.entry[RSS.ENTRY_PUBLISHED.value]

    @handle_key_error
    def get_link(self):
        return self.entry[RSS.ENTRY_LINK.value]


class Feed:
    def __init__(self, rss_url):
        self.feed = feedparser.parse(rss_url)

    @handle_key_error
    def get_title(self):
        return self.feed[RSS.FEED.value][RSS.FEED_TITLE.value]

    @handle_key_error
    def get_subtitle(self):
        return self.feed[RSS.FEED.value][RSS.FEED_SUBTITLE.value]

    @handle_key_error
    def get_link(self):
        return self.feed[RSS.FEED.value][RSS.FEED_LINK.value]

    @handle_key_error
    def get_language(self):
        return self.feed[RSS.FEED.value][RSS.FEED_LANGUAGE.value]

    @handle_key_error
    def get_published(self):
        return self.feed[RSS.FEED.value][RSS.FEED_PUBLISHED.value]

    @handle_key_error
    def get_updated(self):
        return self.feed[RSS.FEED.value][RSS.FEED_UPDATED.value]

    @handle_key_error
    def get_ttl(self):
        return self.feed[RSS.FEED.value][RSS.FEED_TTL.value]

    @handle_key_error
    def get_entries(self):
        entries = []
        for entry in self.feed[RSS.FEED_ENTRIES.value]:
            entries.append(Entry(entry))
        return entries

    @handle_key_error
    def get_href(self):
        return self.feed[RSS.FEED_HREF.value]

    @handle_key_error
    def get_status(self):
        return self.feed[RSS.FEED_STATUS.value]

    @handle_key_error
    def get_encoding(self):
        return self.feed[RSS.FEED_ENCODING.value]

    @handle_key_error
    def get_version(self):
        return self.feed[RSS.FEED_VERSION.value]


@rss.route('/')
def home_page():
    rss_data = get_rss_data()
    articles = []
    feeds_data = rss_data[RSS.FEEDS_KEY.value]
    rss_filter = rss_data[RSS.FILTER_KEY.value]
    history = rss_data[RSS.HISTORY_KEY.value]

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
                if name not in history:
                    history[name] = {}
                records = history[name]
                link = entry.get_link()
                record_entry = get_record_entry(entry)
                if link not in records:
                    records[link] = {
                        RSS.ENTRY_KEY.value: record_entry,
                        RSS.READ_KEY.value: False,
                        RSS.SAVED_KEY.value: False,
                    }
                else:
                    records[link][RSS.ENTRY_KEY.value] = record_entry

    thread = []
    for rss_url in feeds_data:
        t = Thread(target=th, args=(rss_url,))
        thread.append(t)
        t.setDaemon(True)
        t.start()
    for t in thread:
        t.join()

    with open(os.path.join(get_articles_dir_abspath(), current_app.config["RSS_FILE_NAME"]), 'w',
              encoding='utf-8') as rss_file:
        rss_file.write(json.dumps(rss_data, separators=None, sort_keys=True, indent=2, ensure_ascii=False))

    articles = sorted(articles, key=lambda k: k[index_date_key], reverse=True)
    return render_template('rss/home.html', rss_articles=articles)


@rss.route('/%s' % tags_url_name)
def tags_page():
    return ""


@rss.route('/%s/<tag_name>' % tags_url_name)
def tag_page(tag_name):
    return tag_name
