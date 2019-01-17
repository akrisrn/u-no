import re

from markdown.extensions import Extension
from markdown.postprocessors import Postprocessor


class ForceDelInsPostprocessor(Postprocessor):
    def run(self, text):
        return re.sub(r"\+?(<del>|<ins>|</del>|</ins>)\+?", r"\g<1>", text)


# 下划线/删除线语法跟在字后面时会转换成上标/下标，在前后标记一个+号来强制使用下划/删除
class ForceDelInsExtension(Extension):
    def extendMarkdown(self, md):
        md.postprocessors.register(ForceDelInsPostprocessor(md), 'force_del_ins', 175)


def makeExtension(**kwargs):
    return ForceDelInsExtension(**kwargs)
