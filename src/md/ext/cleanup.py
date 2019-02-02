import re

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

import src.flag


class CleanupPreprocessor(Preprocessor):
    def run(self, lines):
        new_lines = []
        for line in lines:
            if line.startswith("# "):
                continue
            new_lines.append(re.sub(src.flag.get_flag_regexp(r"[a-zA-Z]+"), "", line))
        return new_lines


# 剔除flag标记内容
class CleanupExtension(Extension):
    def extendMarkdown(self, md):
        md.preprocessors.register(CleanupPreprocessor(md), "cleanup", 0)


def makeExtension(**kwargs):
    return CleanupExtension(**kwargs)
