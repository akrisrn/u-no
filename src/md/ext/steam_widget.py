from src.md.ext.widget import WidgetExtension


# 匹配steam[]语法为steam小部件，方括号内匹配游戏id
class SteamWidgetExtension(WidgetExtension):
    def __init__(self, **kwargs):
        super().__init__("steam", **kwargs)


def makeExtension(**kwargs):
    return SteamWidgetExtension(**kwargs)
