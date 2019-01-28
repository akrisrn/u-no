from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor


class TemplatePreprocessor(Preprocessor):
    def __init__(self, config, md):
        self.base_path = config.get("base_path")
        super().__init__(md)

    def run(self, lines):
        return lines


class TemplateExtension(Extension):
    def __init__(self, **kwargs):
        self.config = {
            'base_path': [".", ""],
        }
        super().__init__(**kwargs)

    def extendMarkdown(self, md):
        md.preprocessors.register(TemplatePreprocessor(self.getConfigs(), md), "template", 32)


def makeExtension(**kwargs):
    return TemplateExtension(**kwargs)
