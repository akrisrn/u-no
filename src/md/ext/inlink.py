import re

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

import src.flag
import src.index
from src.const import index_url_key


class InlinkPreprocessor(Preprocessor):
    def run(self, lines):
        new_lines = []
        for line in lines:
            new_line = line
            for group in re.finditer(r"\[(.*?)\]\((.*?)\)(\++)", line):
                file_path = group.group(2).replace("../", "")
                # 根据文件相对路径从索引文件中取出url
                item = src.index.get_item_by_path(file_path)
                if item:
                    if len(group.group(3)) == 2:
                        replace_value = item[index_url_key]
                    else:
                        replace_value = "[%s](%s)" % (group.group(1), item[index_url_key])
                    new_line = line.replace(group.group(), replace_value)
            new_lines.append(new_line)
        return new_lines


# 匹配[]()+语法为站内链接，小括号里填入文件相对路径，查找替换为索引文件中对应的url
class InlinkExtension(Extension):
    def extendMarkdown(self, md):
        md.preprocessors.register(InlinkPreprocessor(md), "inlink", 31)


def makeExtension(**kwargs):
    return InlinkExtension(**kwargs)
