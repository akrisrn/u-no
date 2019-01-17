from src.md.ext.widget import WidgetExtension


# 匹配music_list[]语法为网易云音乐歌单小部件，方括号内匹配歌单id
class MusicListWidgetExtension(WidgetExtension):
    def __init__(self, **kwargs):
        super().__init__("music_list", **kwargs)


def makeExtension(**kwargs):
    return MusicListWidgetExtension(**kwargs)
