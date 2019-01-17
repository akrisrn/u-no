import re

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor


class TableIncrementPreprocessor(Preprocessor):
    def run(self, lines):
        num = 1
        new_lines = []
        for line in lines:
            new_line = line
            match = re.match(r"\|\s*(1\.)\s*\|", line)
            if match:
                new_line = line.replace(match.group(), "| %d |" % num)
                num += 1
            else:
                num = 1
            new_lines.append(new_line)
        return new_lines


# 匹配md表格语法中| 1. |部分为自增序列
class TableIncrementExtension(Extension):
    def extendMarkdown(self, md):
        md.preprocessors.register(TableIncrementPreprocessor(md), "table_increment", 0)


def makeExtension(**kwargs):
    return TableIncrementExtension(**kwargs)
