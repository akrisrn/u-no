from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor
from markdown.util import etree


class RatePattern(InlineProcessor):
    def handleMatch(self, m, data):
        el = etree.Element('div')
        el.set('class', 'star')
        # 实际展示的评分为匹配数字的一半
        el.set('data-score', str(int(m.group(1)) / 2))
        return el, m.start(0), m.end(0)


# 匹配*[]语法为评分标签，方括号内匹配0-10
class RateExtension(Extension):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.regex = r'\*\[([0-9]|10)\]'

    def extendMarkdown(self, md):
        md.inlinePatterns.register(RatePattern(self.regex), 'rate', 175)


def makeExtension(**kwargs):
    return RateExtension(**kwargs)
