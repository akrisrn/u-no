from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor


class SymbolsExtendInlineProcessor(InlineProcessor):
    def __init__(self, pattern):
        super().__init__(pattern)
        self.symbols = {
            "<||>": "&updownarrow;",
            "||>": "&downarrow;",
            "<||": "&uparrow;",
        }

    def handleMatch(self, m, data):
        return self.symbols[m.group(1)], m.start(0), m.end(0)


# 替换为相应符号
class SymbolsExtendExtension(Extension):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.regex = r'(\<\|{2}\>|\|{2}\>|\<\|{2})'

    def extendMarkdown(self, md):
        md.inlinePatterns.register(SymbolsExtendInlineProcessor(self.regex), 'symbols_extend', 175)


def makeExtension(**kwargs):
    return SymbolsExtendExtension(**kwargs)
