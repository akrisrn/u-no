import re

from pymdownx.snippets import SnippetPreprocessor, SnippetExtension


class MySnippetPreprocessor(SnippetPreprocessor):
    def parse_snippets(self, lines, file_name=None):
        new_lines = [re.sub(r"(--8<--\s['\"])\[\]\((?:\.\./)*(.*?)\)(['\"])", r"\g<1>\g<2>\g<3>", line)
                     for line in lines]
        return super().parse_snippets(new_lines, file_name)


class MySnippetExtension(SnippetExtension):
    def extendMarkdown(self, md):
        super().extendMarkdown(md)
        md.preprocessors.register(MySnippetPreprocessor(self.getConfigs(), md), "snippet", 32)


def makeExtension(**kwargs):
    return MySnippetExtension(**kwargs)
