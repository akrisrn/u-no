from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor
from markdown.util import etree


class FontawesomeInlineProcessor(InlineProcessor):
    def handleMatch(self, m, data):
        el = etree.Element('i')
        el.set('class', m.group(1))
        return el, m.start(0), m.end(0)


class FontawesomeExtension(Extension):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.regex = r'i\[(.*?)\]'

    def extendMarkdown(self, md):
        md.inlinePatterns.register(FontawesomeInlineProcessor(self.regex), 'fontawesome', 175)


def makeExtension(**kwargs):
    return FontawesomeExtension(**kwargs)
