import re

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor


class EvalPythonPreprocessor(Preprocessor):
    def run(self, lines):
        new_lines = []
        for line in lines:
            new_line = line
            match = re.match(r"(.*?)\$\$\s*(.*?)\s*\$\$(.*)", new_line)
            if match:
                try:
                    result = eval(match.group(2))
                except Exception as e:
                    result = "`#!py >>> %s: %s`" % (e.__class__.__name__, e)
                new_line = match.group(1) + result + match.group(3)
            new_lines.append(new_line)
        return new_lines


class EvalPythonExtension(Extension):
    def extendMarkdown(self, md):
        md.preprocessors.register(EvalPythonPreprocessor(md), "eval_python", 30)


def makeExtension(**kwargs):
    return EvalPythonExtension(**kwargs)
