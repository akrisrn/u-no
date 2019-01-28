import os
import re

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

from src.util import clean_link


class TemplatePreprocessor(Preprocessor):
    def __init__(self, config, md):
        self.base_path = config.get("base_path")
        self.seen = []
        super().__init__(md)

    @staticmethod
    def fill_params(param_dict, text):
        for match in re.finditer(r'{{(\d+)(\|(.*?))?}}', text):
            param_index = int(match.group(1))
            if param_index in param_dict:
                replace_value = param_dict[param_index]
            else:
                replace_value = match.group(3)
            if replace_value is not None:
                text = text.replace(match.group(), replace_value)
        return text

    def parse_template(self, lines, file_name=None):
        new_lines = []
        for line in lines:
            new_line = line
            template_match = re.match(r"^{%\s*(.*?)\s*%}$", new_line)
            if template_match:
                params = template_match.group(1).split("|")[1:]
                param_dict = {}
                i = 0
                for param in params:
                    param_match = re.match(r'(\d+)=(.*)', param)
                    if param_match:
                        param_index = int(param_match.group(1))
                        param_value = param_match.group(2)
                    else:
                        i += 1
                        param_index = i
                        param_value = param
                    param_dict[param_index] = param_value

                file_path = clean_link(template_match.group(1))
                file_abspath = os.path.join(self.base_path, file_path)
                if os.path.exists(file_abspath):
                    if file_path in self.seen:
                        continue
                    if file_name:
                        self.seen.append(file_name)
                    with open(file_abspath, 'r', encoding="utf-8") as f:
                        new_lines.extend([self.fill_params(param_dict, l2) for l2 in
                                          self.parse_template([l.rstrip('\r\n') for l in f], file_path)])
                    if file_name:
                        self.seen.remove(file_name)
                    continue
            new_lines.append(new_line)
        return new_lines

    def run(self, lines):
        return self.parse_template(lines)


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
