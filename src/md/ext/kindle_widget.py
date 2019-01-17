from src.md.ext.widget import WidgetExtension


# 匹配kindle[]语法为亚马逊电子书小部件，方括号内匹配书籍id
class KindleWidgetExtension(WidgetExtension):
    def __init__(self, **kwargs):
        super().__init__("kindle", **kwargs)


def makeExtension(**kwargs):
    return KindleWidgetExtension(**kwargs)
