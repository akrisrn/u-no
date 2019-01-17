from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor
from markdown.util import etree


class InlineQuotePattern(InlineProcessor):
    def handleMatch(self, m, data):
        el = etree.Element('em')
        el.set('class', 'inline-quote')
        el.text = m.group(1)
        return el, m.start(0), m.end(0)


# 匹配____text____语法为行内引用
class InlineQuoteExtension(Extension):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.regex = r'____(.+)____'

    def extendMarkdown(self, md):
        md.inlinePatterns.register(InlineQuotePattern(self.regex), 'inline_quote', 175)


def makeExtension(**kwargs):
    return InlineQuoteExtension(**kwargs)
