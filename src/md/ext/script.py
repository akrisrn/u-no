from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor
from markdown.util import etree


class ScriptInlineProcessor(InlineProcessor):
    def handleMatch(self, m, data):
        el = etree.Element('script')
        el.set('src', m.group(1))
        return el, m.start(0), m.end(0)


class ScriptExtension(Extension):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.regex = r'script\[\]\((.*?)\)'

    def extendMarkdown(self, md):
        md.inlinePatterns.register(ScriptInlineProcessor(self.regex), 'script', 175)


def makeExtension(**kwargs):
    return ScriptExtension(**kwargs)
