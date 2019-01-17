from src.md.ext.widget import WidgetExtension


# 匹配music[]语法为网易云音乐单曲小部件，方括号内匹配单曲id
class MusicWidgetExtension(WidgetExtension):
    def __init__(self, **kwargs):
        super().__init__("music", **kwargs)


def makeExtension(**kwargs):
    return MusicWidgetExtension(**kwargs)
