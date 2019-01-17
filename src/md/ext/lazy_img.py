import re

from markdown.extensions import Extension
from markdown.postprocessors import Postprocessor


class LazyImgPostprocessor(Postprocessor):
    def run(self, text):
        return re.sub(r'(<img.*?src=)(".*?")', r'\g<1>"" data-src=\g<2>', text)


class LazyImgExtension(Extension):
    def extendMarkdown(self, md):
        md.postprocessors.register(LazyImgPostprocessor(md), 'lazy_img', 175)


def makeExtension(**kwargs):
    return LazyImgExtension(**kwargs)
