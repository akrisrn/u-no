import re

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

import src.flag


class CleanupPreprocessor(Preprocessor):
    def run(self, lines):
        return [re.sub(src.flag.get_flag_regexp(r"\w+"), "", line) for line in lines]


# 剔除flag标记内容
class CleanupExtension(Extension):
    def extendMarkdown(self, md):
        md.preprocessors.register(CleanupPreprocessor(md), "cleanup", 0)


def makeExtension(**kwargs):
    return CleanupExtension(**kwargs)
