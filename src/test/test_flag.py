import unittest

from flask import current_app

from src.flag import get_tags_flag, get_date_flag, get_notags_flag, get_fixed_flag, get_top_flag, get_highlight_flag, \
    get_ignore_flag, get_unignore_flag, get_plugin_flag
from uno import app

with app.app_context():
    DEFAULT_TAG = current_app.config["DEFAULT_TAG"]


def get_result(func, data):
    with app.app_context():
        return func(data)


class MyTest(unittest.TestCase):
    def test_get_tags_flag_0(self):
        tags = ["test"]
        data = "{tag %s}" % ",".join(tags)
        self.assertEqual(get_result(get_tags_flag, data), tags)

    def test_get_tags_flag_1(self):
        tags = ["test", "测试"]
        data = "{tag %s}" % ",".join(tags)
        self.assertEqual(get_result(get_tags_flag, data), tags)

    def test_get_tags_flag_2(self):
        tags = ["test", "测试"]
        data = "{tag %s}" % "，".join(tags)
        self.assertEqual(get_result(get_tags_flag, data), tags)

    def test_get_tags_flag_3(self):
        tags = ["test", "测试"]
        data = "{tag %s}" % "   ，   ".join(tags)
        self.assertEqual(get_result(get_tags_flag, data), tags)

    def test_get_date_flag_0(self):
        date = "18-12-01"
        data = "{date %s}" % date
        self.assertEqual(get_result(get_date_flag, data), date)

    def test_get_date_flag_1(self):
        date = "2018-12-1"
        data = "{date %s}" % date
        self.assertEqual(get_result(get_date_flag, data), "18-12-01")

    def test_get_date_flag_2(self):
        date = "18-12-01"
        data = "{date 20%s,18-01-01}" % date
        self.assertEqual(get_result(get_date_flag, data), date)

    def test_get_date_flag_3(self):
        date = "18-12-01"
        data = "{date 20%s，1111}" % date
        self.assertEqual(get_result(get_date_flag, data), date)

    def test_get_notags_flag_0(self):
        data = "{notags}"
        self.assertTrue(get_result(get_notags_flag, data))

    def test_get_fixed_flag_0(self):
        data = "{fixed}"
        self.assertTrue(get_result(get_fixed_flag, data))

    def test_get_top_flag_0(self):
        data = "{top}"
        self.assertTrue(get_result(get_top_flag, data))

    def test_get_highlight_flag_0(self):
        data = "{highlight}"
        self.assertTrue(get_result(get_highlight_flag, data))

    def test_get_ignore_flag_0(self):
        data = "{ignore}"
        self.assertTrue(get_result(get_ignore_flag, data))

    def test_get_unignore_flag_0(self):
        data = "{unignore}"
        self.assertTrue(get_result(get_unignore_flag, data))

    def test_get_plugin_flag_0(self):
        plugin = ["a", "b"]
        data = "{plugin %s}" % ",".join(plugin)
        self.assertEqual(get_result(get_plugin_flag, data), plugin)


if __name__ == '__main__':
    unittest.main()
