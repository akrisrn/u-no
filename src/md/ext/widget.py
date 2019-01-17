from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor
from markdown.util import etree


class WidgetPattern(InlineProcessor):
    def __init__(self, pattern, name):
        super().__init__(pattern)
        self.name = name

    def handleMatch(self, m, data):
        el = etree.Element('iframe')
        el.set('class', self.name + '-widget')
        el.set('data-id', m.group(1))
        return el, m.start(0), m.end(0)


class WidgetExtension(Extension):
    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.regex = self.name + r'\[(\w+)\]'

    def extendMarkdown(self, md):
        md.inlinePatterns.register(WidgetPattern(self.regex, self.name), self.name + '_widget', 175)


def makeExtension(**kwargs):
    return WidgetExtension(**kwargs)
